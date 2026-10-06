import asyncio
import json
from pathlib import Path

from src.models import CandidateResult
from src.pipeline import ScreeningPipeline


def test_run_replaces_old_output_and_summarizes_current_files(tmp_path, monkeypatch):
    input_dir = tmp_path / "resumes"
    input_dir.mkdir()
    (input_dir / "candidate_01.txt").write_text("resume one", encoding="utf-8")
    (input_dir / "candidate_02.txt").write_text("resume two", encoding="utf-8")

    output_path = tmp_path / "output" / "results.json"
    output_path.parent.mkdir()
    output_path.write_text(
        json.dumps([{"candidate_name": "stale cached candidate", "eligible": False}]),
        encoding="utf-8",
    )

    async def process_file(file_path):
        return CandidateResult(
            candidate_name=Path(file_path).stem,
            eligible=False,
            file_path=file_path,
        )

    pipeline = ScreeningPipeline(str(input_dir), str(output_path))
    monkeypatch.setattr(pipeline, "process_file", process_file)

    summary = asyncio.run(pipeline.run())

    saved_results = json.loads(output_path.read_text(encoding="utf-8"))
    assert summary.total_resumes == 2
    assert summary.successfully_parsed == 2
    assert summary.failed == 0
    assert [result["candidate_name"] for result in saved_results] == [
        "candidate_01",
        "candidate_02",
    ]
