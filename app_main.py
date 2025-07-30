#!/usr/bin/env python3
"""
YouTube Downloader - macOS App
Native macOS application for Apple Silicon
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import yt_dlp

# Add the app directory to Python path
if getattr(sys, 'frozen', False):
    # Running as compiled app
    app_dir = Path(sys._MEIPASS)
else:
    # Running as script
    app_dir = Path(__file__).parent

# Create Flask app
app = Flask(__name__)

# Global variables for download status
download_status = {}

class DownloadManager:
    def __init__(self):
        self.downloads = {}
    
    def start_download(self, download_id, url, download_type, quality, output_dir):
        """Start a download in a separate thread"""
        def download_worker():
            try:
                download_status[download_id] = {
                    'status': 'starting',
                    'progress': 0,
                    'message': 'Initializing download...',
                    'error': None
                }
                
                if download_type == "video":
                    self.download_video(download_id, url, quality, output_dir)
                elif download_type == "audio":
                    self.download_audio(download_id, url, quality, output_dir)
                elif download_type == "playlist":
                    self.download_playlist(download_id, url, quality, output_dir)
                    
            except Exception as e:
                download_status[download_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': f'Download failed: {str(e)}',
                    'error': str(e)
                }
        
        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()
    
    def progress_hook(self, download_id):
        """Progress callback for yt-dlp"""
        def hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    download_status[download_id] = {
                        'status': 'downloading',
                        'progress': percent,
                        'message': f'Downloading... {percent:.1f}%',
                        'error': None
                    }
                elif 'downloaded_bytes' in d:
                    download_status[download_id] = {
                        'status': 'downloading',
                        'progress': 0,
                        'message': f'Downloaded: {d["downloaded_bytes"]} bytes',
                        'error': None
                    }
            elif d['status'] == 'finished':
                download_status[download_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Download completed!',
                    'error': None
                }
        return hook
    
    def download_video(self, download_id, url, quality, output_dir):
        """Download video"""
        try:
            download_status[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'message': 'Starting video download...',
                'error': None
            }
            
            quality_map = {
                "Best": "best[height<=1080]",
                "1080p": "best[height<=1080]",
                "720p": "best[height<=720]",
                "480p": "best[height<=480]",
                "360p": "best[height<=360]"
            }
            
            format_spec = quality_map.get(quality, "best")
            
            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook(download_id)],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            download_status[download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Video download completed!',
                'error': None
            }
            
        except Exception as e:
            download_status[download_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Video download failed: {str(e)}',
                'error': str(e)
            }
    
    def download_audio(self, download_id, url, quality, output_dir):
        """Download audio and convert to MP3"""
        try:
            download_status[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'message': 'Starting audio download...',
                'error': None
            }
            
            quality_map = {
                "192k": "192",
                "128k": "128",
                "64k": "64"
            }
            
            bitrate = quality_map.get(quality, "192")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'progress_hooks': [self.progress_hook(download_id)],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            download_status[download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Audio download completed!',
                'error': None
            }
            
        except Exception as e:
            download_status[download_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Audio download failed: {str(e)}',
                'error': str(e)
            }
    
    def download_playlist(self, download_id, url, quality, output_dir):
        """Download playlist"""
        try:
            download_status[download_id] = {
                'status': 'downloading',
                'progress': 0,
                'message': 'Starting playlist download...',
                'error': None
            }
            
            quality_map = {
                "720p": "best[height<=720]",
                "480p": "best[height<=480]",
                "360p": "best[height<=360]"
            }
            
            format_spec = quality_map.get(quality, "best[height<=720]")
            
            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook(download_id)],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            download_status[download_id] = {
                'status': 'completed',
                'progress': 100,
                'message': 'Playlist download completed!',
                'error': None
            }
            
        except Exception as e:
            download_status[download_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Playlist download failed: {str(e)}',
                'error': str(e)
            }

# Initialize download manager
download_manager = DownloadManager()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/test_url', methods=['POST'])
def test_url():
    """Test if URL is valid"""
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is empty'})
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        return jsonify({
            'success': True,
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 'Unknown'),
            'uploader': info.get('uploader', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'URL test failed: {str(e)}'})

@app.route('/start_download', methods=['POST'])
def start_download():
    """Start a download"""
    data = request.get_json()
    url = data.get('url', '')
    download_type = data.get('type', 'video')
    quality = data.get('quality', '720p')
    output_dir = data.get('output_dir', os.path.expanduser('~/Downloads'))
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is empty'})
    
    # Create unique download ID
    download_id = f"download_{int(time.time())}"
    
    # Start download
    download_manager.start_download(download_id, url, download_type, quality, output_dir)
    
    return jsonify({'success': True, 'download_id': download_id})

@app.route('/download_status/<download_id>')
def get_download_status(download_id):
    """Get download status"""
    status = download_status.get(download_id, {
        'status': 'unknown',
        'progress': 0,
        'message': 'Download not found',
        'error': None
    })
    return jsonify(status)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5800')

def main():
    """Main application entry point"""
    print("🎥 YouTube Downloader - macOS App")
    print("Starting web server...")
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Run Flask app
    app.run(debug=False, port=5800)

if __name__ == '__main__':
    main()
