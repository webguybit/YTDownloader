#!/usr/bin/env python3
"""
Web-based YouTube Downloader using Flask
No Tkinter, runs in your web browser
"""

from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import threading
import time
import json
from datetime import datetime

app = Flask(__name__)

# Global variables for download status
download_status = {}
download_progress = {}

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
            
            # Map quality to yt-dlp format
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
            
            # Map quality to bitrate
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
    output_dir = data.get('output_dir', os.getcwd())
    
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

@app.route('/downloads')
def list_downloads():
    """List all downloads"""
    return jsonify(download_status)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Downloader - Web Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .radio-group {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
        
        .radio-group label {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-weight: normal;
        }
        
        .radio-group input[type="radio"] {
            width: auto;
            margin-right: 8px;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #51cf66;
            color: white;
        }
        
        .btn-success:hover {
            background: #40c057;
            transform: translateY(-2px);
        }
        
        .btn-warning {
            background: #ffd43b;
            color: #333;
        }
        
        .btn-warning:hover {
            background: #fcc419;
            transform: translateY(-2px);
        }
        
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #51cf66, #40c057);
            width: 0%;
            transition: width 0.3s;
        }
        
        .status {
            text-align: center;
            font-weight: 600;
            color: #333;
        }
        
        .log {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 2px 0;
        }
        
        .log-success { color: #51cf66; }
        .log-error { color: #ff6b6b; }
        .log-info { color: #667eea; }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 YouTube Downloader</h1>
            <p>Download videos, audio, and playlists easily</p>
        </div>
        
        <div class="content">
            <div id="alert" class="alert"></div>
            
            <form id="downloadForm">
                <div class="form-group">
                    <label for="url">YouTube URL:</label>
                    <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
                </div>
                
                <div class="form-group">
                    <label>Download Type:</label>
                    <div class="radio-group">
                        <label>
                            <input type="radio" name="type" value="video" checked>
                            Video
                        </label>
                        <label>
                            <input type="radio" name="type" value="audio">
                            Audio (MP3)
                        </label>
                        <label>
                            <input type="radio" name="type" value="playlist">
                            Playlist
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="quality">Quality:</label>
                    <select id="quality" name="quality">
                        <option value="720p">720p</option>
                        <option value="1080p">1080p</option>
                        <option value="480p">480p</option>
                        <option value="360p">360p</option>
                        <option value="Best">Best</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="output_dir">Output Directory:</label>
                    <input type="text" id="output_dir" name="output_dir" value="Current Directory" readonly>
                </div>
                
                <div class="button-group">
                    <button type="button" class="btn btn-warning" onclick="testUrl()">Test URL</button>
                    <button type="submit" class="btn btn-success">Download</button>
                </div>
            </form>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="status" id="status">Ready</div>
            </div>
            
            <div class="log" id="log"></div>
        </div>
    </div>

    <script>
        let currentDownloadId = null;
        let statusInterval = null;
        
        // Update quality options based on download type
        document.querySelectorAll('input[name="type"]').forEach(radio => {
            radio.addEventListener('change', updateQualityOptions);
        });
        
        function updateQualityOptions() {
            const type = document.querySelector('input[name="type"]:checked').value;
            const qualitySelect = document.getElementById('quality');
            
            if (type === 'audio') {
                qualitySelect.innerHTML = `
                    <option value="192k">192k</option>
                    <option value="128k">128k</option>
                    <option value="64k">64k</option>
                `;
            } else if (type === 'playlist') {
                qualitySelect.innerHTML = `
                    <option value="720p">720p</option>
                    <option value="480p">480p</option>
                    <option value="360p">360p</option>
                `;
            } else {
                qualitySelect.innerHTML = `
                    <option value="720p">720p</option>
                    <option value="1080p">1080p</option>
                    <option value="480p">480p</option>
                    <option value="360p">360p</option>
                    <option value="Best">Best</option>
                `;
            }
        }
        
        function showAlert(message, type = 'info') {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';
            
            setTimeout(() => {
                alert.style.display = 'none';
            }, 5000);
        }
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        
        async function testUrl() {
            const url = document.getElementById('url').value;
            if (!url) {
                showAlert('Please enter a URL', 'error');
                return;
            }
            
            addLog('Testing URL...', 'info');
            
            try {
                const response = await fetch('/test_url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addLog(`URL is valid! Title: ${data.title}`, 'success');
                    addLog(`Duration: ${data.duration} seconds`, 'info');
                    addLog(`Uploader: ${data.uploader}`, 'info');
                    showAlert('URL is valid!', 'success');
                } else {
                    addLog(`URL test failed: ${data.message}`, 'error');
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                addLog(`Error testing URL: ${error}`, 'error');
                showAlert('Error testing URL', 'error');
            }
        }
        
        document.getElementById('downloadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                url: formData.get('url'),
                type: formData.get('type'),
                quality: formData.get('quality'),
                output_dir: formData.get('output_dir')
            };
            
            if (!data.url) {
                showAlert('Please enter a URL', 'error');
                return;
            }
            
            addLog('Starting download...', 'info');
            showAlert('Starting download...', 'info');
            
            // Show progress container
            document.getElementById('progressContainer').style.display = 'block';
            
            try {
                const response = await fetch('/start_download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentDownloadId = result.download_id;
                    addLog(`Download started with ID: ${currentDownloadId}`, 'success');
                    startStatusPolling();
                } else {
                    addLog(`Failed to start download: ${result.message}`, 'error');
                    showAlert(result.message, 'error');
                }
            } catch (error) {
                addLog(`Error starting download: ${error}`, 'error');
                showAlert('Error starting download', 'error');
            }
        });
        
        function startStatusPolling() {
            if (statusInterval) {
                clearInterval(statusInterval);
            }
            
            statusInterval = setInterval(async () => {
                if (!currentDownloadId) return;
                
                try {
                    const response = await fetch(`/download_status/${currentDownloadId}`);
                    const status = await response.json();
                    
                    // Update progress bar
                    const progressFill = document.getElementById('progressFill');
                    const statusText = document.getElementById('status');
                    
                    progressFill.style.width = `${status.progress}%`;
                    statusText.textContent = status.message;
                    
                    // Add log entry for status changes
                    if (status.status === 'completed') {
                        addLog('Download completed successfully!', 'success');
                        showAlert('Download completed!', 'success');
                        clearInterval(statusInterval);
                        currentDownloadId = null;
                    } else if (status.status === 'error') {
                        addLog(`Download failed: ${status.error}`, 'error');
                        showAlert(`Download failed: ${status.error}`, 'error');
                        clearInterval(statusInterval);
                        currentDownloadId = null;
                    } else if (status.status === 'downloading') {
                        addLog(`Progress: ${status.progress.toFixed(1)}%`, 'info');
                    }
                    
                } catch (error) {
                    addLog(`Error checking status: ${error}`, 'error');
                }
            }, 1000);
        }
        
        // Initialize
        updateQualityOptions();
        addLog('YouTube Downloader Web Interface Ready', 'success');
    </script>
</body>
</html>'''
    
    # Write the HTML template
    with open('templates/index.html', 'w') as f:
        f.write(html_template)
    
    print("🎥 YouTube Downloader Web Interface")
    print("=" * 40)
    print("Starting web server...")
    print("Open your browser and go to: http://localhost:5550")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    app.run(debug=True, port=5550) 