from pathlib import Path
from subprocess import Popen
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/video", tags=["Video"])


class VideoStartRequest(BaseModel):
    video_path: str


@router.post("/start")
def start_video_session(request: VideoStartRequest):
    video_path = Path(request.video_path)

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found: {request.video_path}",
        )

    runner_path = (
    Path(__file__).resolve().parents[1]
    / "cv"
    / "detection_runner.py"
)
    if not runner_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Detection runner not found",
        )

    process = Popen(
    [
        sys.executable,
        "-m",
        "app.cv.detection_runner",
        "--video",
        str(video_path),
    ],
    cwd=Path(__file__).resolve().parents[2],
)

    return {
        "status": "started",
        "message": "Video analysis started",
        "process_id": process.pid,
    }