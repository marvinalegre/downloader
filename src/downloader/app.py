import os
import secrets
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
security = HTTPBasic()

DOWNLOADS = Path("data/downloads")
DOWNLOADS.mkdir(parents=True, exist_ok=True)

USERNAME = os.environ["DOWNLOADER_USERNAME"]
PASSWORD = os.environ["DOWNLOADER_PASSWORD"]


def authenticate(
    credentials: HTTPBasicCredentials = Depends(security),
):
    valid_username = secrets.compare_digest(
        credentials.username,
        USERNAME,
    )
    valid_password = secrets.compare_digest(
        credentials.password,
        PASSWORD,
    )

    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


class DownloadRequest(BaseModel):
    url: str


@app.get("/", dependencies=[Depends(authenticate)])
def index():
    return FileResponse("static/index.html")


@app.post("/download", dependencies=[Depends(authenticate)])
def download(request: DownloadRequest):
    subprocess.run(
        ["/home/marvin/desktop/downloader/.misc/yt-dlp_linux", request.url],

        cwd=DOWNLOADS,
        check=True,
    )

    file = max(DOWNLOADS.iterdir(), key=lambda p: p.stat().st_mtime)

    return {"downloadUrl": f"/downloads/{file.name}"}


@app.get("/downloads/{filename}", dependencies=[Depends(authenticate)])
def get_download(filename: str):
    file = DOWNLOADS / filename
    return FileResponse(file, filename=file.name)
