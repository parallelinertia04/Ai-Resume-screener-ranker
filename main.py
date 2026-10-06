import argparse
import asyncio
from src.pipeline import ScreeningPipeline

def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening CLI")
    parser.add_argument("--serve", action="store_true", help="Run the FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--input", help="Input directory containing resumes")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    if args.serve:
        if not 1 <= args.port <= 65535:
            parser.error("--port must be between 1 and 65535")

        import uvicorn

        print(f"Starting API server at http://127.0.0.1:{args.port}")
        uvicorn.run("src.app:app", host="127.0.0.1", port=args.port)
        return

    if not args.input or not args.output:
        parser.error("--input and --output are required unless --serve is used")

    print(f"Starting screening pipeline...")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")

    pipeline = ScreeningPipeline(args.input, args.output)
    summary = asyncio.run(pipeline.run())
    
    print("\n--- Batch Summary ---")
    print(f"Total Resumes: {summary.total_resumes}")
    print(f"Successfully Parsed: {summary.successfully_parsed}")
    print(f"Eligible: {summary.eligible}")
    print(f"Rejected: {summary.rejected}")
    print(f"Failed/Unreadable: {summary.failed}")
    print(f"Results saved to {args.output}")
    import os
    summary_path = os.path.join(os.path.dirname(args.output) or ".", "summary.json")
    print(f"Batch summary saved to {summary_path}")

if __name__ == "__main__":
    main()
