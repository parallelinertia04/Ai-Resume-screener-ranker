import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, Any

from src.pipeline import ScreeningPipeline

app = FastAPI(title="AI Resume Screening System")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


class ScreenRequest(BaseModel):
    input_dir: str
    output_path: str

# Simple in-memory state for assignment purposes
job_status: Dict[str, Any] = {}

@app.post("/screen")
async def screen_resumes(req: ScreenRequest, background_tasks: BackgroundTasks):
    job_id = f"{req.input_dir}_{req.output_path}"
    job_status[job_id] = {"status": "processing"}
    
    def run_pipeline():
        pipeline = ScreeningPipeline(req.input_dir, req.output_path)
        summary = asyncio.run(pipeline.run())
        job_status[job_id] = {
            "status": "completed",
            "summary": summary.model_dump()
        }
    
    background_tasks.add_task(run_pipeline)
    return {"message": "Screening started", "job_id": job_id}

@app.get("/results")
async def get_results(job_id: str):
    if job_id not in job_status:
        return {"error": "Job not found"}
    return job_status[job_id]
