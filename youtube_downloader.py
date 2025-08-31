import os
import re
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8347888373:AAHrRKPkDSeuI3F_1MvrlS744oCmv-LbIro"

# YouTube URL pattern
YOUTUBE_URL_PATTERN = re.compile(
    r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
)

class YouTubeDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[height<=720]/best',  # Limit to 720p for faster download
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extract_flat': False,
        }

    def download_video(self, url: str, download_path: str) -> dict:
        """Download YouTube video and return info"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                # Check file size (limit to ~50MB for Telegram)
                filesize = info.get('filesize') or info.get('filesize_approx', 0)
                if filesize > 50 * 1024 * 1024:  # 50MB limit
                    return {
                        'success': False,
                        'error': 'Video is too large (>50MB). Please try a shorter video.'
                    }
                
                # Set download path
                self.ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')
                
                # Download the video
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl_download:
                    ydl_download.download([url])
                
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'filename': f"{info.get('title', 'video')}.{
