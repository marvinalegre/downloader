from pathlib import Path
import subprocess
import uuid

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

DOWNLOADS = Path("data/downloads")
DOWNLOADS.mkdir(parents=True, exist_ok=True)


class DownloadRequest(BaseModel):
    url: str


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.post("/download")
def download(request: DownloadRequest):
    output = DOWNLOADS / str(uuid.uuid4())
    subprocess.run(
        ["/home/marvin/desktop/downloader/.misc/yt-dlp_linux", request.url],
        cwd=DOWNLOADS,
        check=True,
    )

    file = max(DOWNLOADS.iterdir(), key=lambda p: p.stat().st_mtime)

    return {"downloadUrl": f"/downloads/{file.name}"}


@app.get("/downloads/{filename}")
def get_download(filename: str):
    file = DOWNLOADS / filename
    return FileResponse(file, filename=file.name)
