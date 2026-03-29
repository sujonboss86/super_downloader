from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import os
import yt_dlp
import uuid
import time  # server uptime calculation

app = FastAPI(
    title="Super Fast Downloader",
    description="Async all-platform video downloader with auto delete",
    version="3.3",
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


# ✅ Root route → UptimeRobot friendly HTML
@app.get("/", response_class=HTMLResponse)
def root_page():
    return f"""
    <h2>🚀 AutoDL API Online</h2>
    <p>👤 Author: SUJON-BOSS</p>
    <p>✅ Server running for {int(time.time() - start_time)} seconds</p>
    <p>Use: /?url=VIDEO_LINK to download video</p>
    """


# Store server start time
start_time = time.time()


# ✅ Download route
@app.get("/download")
async def download_video(url: str = Query(...), background_tasks: BackgroundTasks = None):
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
