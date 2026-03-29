from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import yt_dlp
import uuid

app = FastAPI(
    title="Super Fast Downloader",
    description="Async all-platform video downloader with auto delete",
    version="3.1"
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# 🧹 function for deleting files
def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Deleted: {path}")


# ✅ Root route → download + send + delete
@app.get("/")
async def root_download(url: str = Query(None), background_tasks: BackgroundTasks = None):
    if not url:
        return {"message": "Use like: /?url=VIDEO_LINK"}

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
            return JSONResponse({"error": "Download failed"}, status_code=500)

        # 🗑️ Schedule delete after send
        # Option 1: delete immediately after sending
        background_tasks.add_task(delete_file, output_path)

        # Option 2: delete after 5 minutes (comment above line & uncomment below line)
        # background_tasks.add_task(lambda: os.remove(output_path) if os.path.exists(output_path) else None,)

        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="video.mp4"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)