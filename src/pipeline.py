import os
import glob
import json
import asyncio
from typing import List, Optional
from src.parser import ResumeParser
from src.filters import EligibilityFilter
from src.llm_adapter import LLMAdapter
from src.github_enricher import GithubEnricher
from src.models import CandidateResult, BatchSummary
from src.config import MAX_CONCURRENCY, LLM_PROVIDER

class ScreeningPipeline:
    def __init__(self, input_dir: str, output_path: str):
        self.input_dir = input_dir
        self.output_path = output_path
        concurrency = 1 if LLM_PROVIDER == "groq" else MAX_CONCURRENCY
        self.semaphore = asyncio.Semaphore(concurrency)

    async def process_file(self, file_path: str) -> Optional[CandidateResult]:
        async with self.semaphore:
            try:
                # 1. Parse
                from pathlib import Path
                path_obj = Path(file_path)
                text, error_msg, links = await asyncio.to_thread(ResumeParser.parse_file, path_obj)
                
                if not text:
                    return CandidateResult(
                        candidate_name=os.path.basename(file_path),
                        eligible=False,
                        rejection_reasons=[error_msg or "Failed to parse text"],
                        file_path=file_path
                    )
                
                github_username = ResumeParser.extract_github_username(text, links)
                github_url = f"https://github.com/{github_username}" if github_username else None
                
                # Try to extract name
                filename = os.path.basename(file_path)
                default_name = os.path.splitext(filename)[0].replace("_", " ").title()
                name = ResumeParser.extract_candidate_name_fallback(text, default_name)

                # 2. Hard Eligibility
                eligible, reasons, skills = EligibilityFilter.check_eligibility(text)
                
                result = CandidateResult(
                    candidate_name=name,
                    eligible=eligible,
                    matched_skills=skills,
                    rejection_reasons=reasons,
                    file_path=file_path,
                    github_url=github_url
                )

                if not eligible:
                    return result

                # 3. LLM Scoring
                eval_data = await asyncio.to_thread(LLMAdapter.evaluate_candidate, text)
                if eval_data:
                    result.score_breakdown = eval_data.score_breakdown
                    result.project_summary = eval_data.project_summary
                    result.strengths = eval_data.strengths
                    result.concerns = eval_data.concerns
                    result.matched_skills = list(set(skills + eval_data.matched_skills))
                    # Sum values, github will be added later
                    result.total_score = (
                        eval_data.score_breakdown.ai_project_depth +
                        eval_data.score_breakdown.python_backend +
                        eval_data.score_breakdown.cloud_fullstack +
                        eval_data.score_breakdown.engineering_depth
                    )
                else:
                    result.eligible = False
                    result.rejection_reasons.append("LLM Evaluation Failed")
                    return result

                # 4. GitHub Enrichment
                if github_url:
                    gh_score, gh_summary = await GithubEnricher.get_github_score_async(github_url)
                    result.score_breakdown.github = gh_score
                    result.github_summary = gh_summary
                    result.total_score += gh_score

                return result

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                return None

    async def run(self) -> BatchSummary:
        files = []
        for ext in ["*.pdf", "*.docx", "*.txt"]:
            files.extend(glob.glob(os.path.join(self.input_dir, ext)))
        
        results = await asyncio.gather(*(self.process_file(f) for f in files))
        
        valid_results = [r for r in results if r is not None]
        
        # Rank eligible
        eligible_candidates = [r for r in valid_results if r.eligible]
        eligible_candidates.sort(key=lambda x: x.total_score, reverse=True)
        
        # Assign rank
        for i, c in enumerate(eligible_candidates):
            c.rank = i + 1
            
        rejected_candidates = [r for r in valid_results if not r.eligible]
        
        all_candidates = eligible_candidates + rejected_candidates
        
        # Save output
        output_data = [c.model_dump(exclude={"file_path", "github_url"}, exclude_none=True) for c in all_candidates]
        output_dir = os.path.dirname(self.output_path) or "."
        os.makedirs(output_dir, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        summary = BatchSummary(
            total_resumes=len(files),
            successfully_parsed=len(valid_results),
            eligible=len(eligible_candidates),
            rejected=len(rejected_candidates),
            failed=len(files) - len(valid_results)
        )

        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=2)

        return summary
