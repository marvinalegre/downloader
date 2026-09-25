import uvicorn


def main() -> None:
    uvicorn.run("downloader.app:app", host="127.0.0.1", port=5000)
