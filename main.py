from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(
    title="Facebook Media Downloader API",
    description="API for downloading Facebook Videos, Reels, Audio, and Thumbnails"
)

# Enable CORS for Blogger / Web Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Facebook Media Downloader API is running!"
    }

@app.get("/download")
def download_media(url: str = Query(..., description="Facebook Video / Reel / Media URL")):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title') or info.get('description') or 'Facebook Media'
            thumbnail = info.get('thumbnail')
            duration = info.get('duration')
            
            formats = info.get('formats', [])
            hd_url = None
            sd_url = None
            
            # Extract HD & SD formats
            for f in formats:
                format_id = str(f.get('format_id', '')).lower()
                format_note = str(f.get('format_note', '')).lower()
                f_url = f.get('url')
                
                if f_url:
                    if 'hd' in format_id or 'hd' in format_note:
                        hd_url = f_url
                    elif 'sd' in format_id or 'sd' in format_note:
                        sd_url = f_url
            
            # Fallback direct URL if specific format isn't isolated
            direct_url = info.get('url') or (formats[-1].get('url') if formats else None)
            
            if not hd_url:
                hd_url = direct_url
            if not sd_url:
                sd_url = direct_url

            return {
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "duration": duration,
                "media": {
                    "hd_video": hd_url,
                    "sd_video": sd_url,
                    "direct_link": direct_url
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch media: {str(e)}")
