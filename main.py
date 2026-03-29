from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import yt_dlp
import uuid

app = FastAPI(
    title="Super Fast Downloader",
    description="Async all-platform video downloader with auto delete",
    version="3.2",
    contact={"name": "SUJON-BOSS"}  # Author info
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# 🧹 function for deleting files
def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Deleted: {path}")


# ✅ Health route (UptimeRobot / monitoring)
@app.get("/health")
def health_check():
    return {"status": "ok", "author": "SUJON-BOSS"}


# ✅ Root route → download + send + delete
@app.get("/")
async def root_download(url: str = Query(None), background_tasks: BackgroundTasks = None):
    if not url:
        return {"message": "Use like: /?url=VIDEO_LINK", "author": "SUJON-BOSS"}

    try:
        unique_id = str(uuid.uuid4())
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.mp4")

        cookies_path = "cookies.txt"
        use_cookies = os.path.exists(cookies_path)

        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'noplaylist': True,
            'concurrent_fragment_downloads': 5,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        if use_cookies:
            ydl_opts['cookiefile'] = cookies_path

        # 🎥 download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            return JSONResponse({"error": "Download failed", "author": "SUJON-BOSS"}, status_code=500)

        # 🗑️ delete after send
        if background_tasks:
            background_tasks.add_task(delete_file, output_path)

        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="video.mp4"
        )

    except Exception as e:
        return JSONResponse({"error": str(e), "author": "SUJON-BOSS"}, status_code=500)
