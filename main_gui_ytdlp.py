import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading
import subprocess

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Downloader - yt-dlp GUI")
        self.master.geometry("700x500")
        self.master.configure(bg='#f0f0f0')
        
        # Variables
        self.video_url = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.download_type = tk.StringVar(value="video")
        self.quality = tk.StringVar(value="720p")
        self.progress = tk.DoubleVar()
        self.spinner_running = False
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.master, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="YouTube Downloader", 
                              font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))

        # URL input section
        url_frame = tk.Frame(main_frame, bg='#f0f0f0')
        url_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(url_frame, text="YouTube URL:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0', fg='#333333').pack(anchor='w')
        
        url_entry = tk.Entry(url_frame, textvariable=self.video_url, width=70, 
                            font=("Arial", 10), relief=tk.SOLID, bd=1)
        url_entry.pack(fill=tk.X, pady=5)
        url_entry.bind("<Control-v>", lambda e: self.master.clipboard_get())

        # Download type section
        type_frame = tk.Frame(main_frame, bg='#f0f0f0')
        type_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(type_frame, text="Download Type:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0', fg='#333333').pack(anchor='w')
        
        type_buttons_frame = tk.Frame(type_frame, bg='#f0f0f0')
        type_buttons_frame.pack(pady=5)
        
        for text, mode in [("Video", "video"), ("Audio (MP3)", "audio"), ("Playlist", "playlist")]:
            tk.Radiobutton(type_buttons_frame, text=text, variable=self.download_type, 
                          value=mode, command=self.update_quality_options,
                          font=("Arial", 10), bg='#f0f0f0', fg='#333333').pack(side=tk.LEFT, padx=10)

        # Quality selection section
        quality_frame = tk.Frame(main_frame, bg='#f0f0f0')
        quality_frame.pack(fill=tk.X, pady=10)
        
        self.quality_label = tk.Label(quality_frame, text="Video Quality:", 
                                     font=("Arial", 10, "bold"), bg='#f0f0f0', fg='#333333')
        self.quality_label.pack(anchor='w')
        
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality, 
                                         state="readonly", font=("Arial", 10))
        self.quality_combo.pack(fill=tk.X, pady=5)
        self.quality_combo['values'] = ["Best", "1080p", "720p", "480p", "360p"]

        # Output folder section
        output_frame = tk.Frame(main_frame, bg='#f0f0f0')
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(output_frame, text="Output Folder:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0', fg='#333333').pack(anchor='w')
        
        output_buttons_frame = tk.Frame(output_frame, bg='#f0f0f0')
        output_buttons_frame.pack(pady=5)
        
        tk.Button(output_buttons_frame, text="Browse Folder", command=self.select_output_folder,
                 font=("Arial", 10), bg='#4CAF50', fg='white', relief=tk.FLAT, 
                 padx=15, pady=5).pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_label = tk.Label(output_buttons_frame, textvariable=self.output_path,
                                    font=("Arial", 9), bg='#f0f0f0', fg='#666666')
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action buttons section
        action_frame = tk.Frame(main_frame, bg='#f0f0f0')
        action_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(action_frame, text="Test URL", command=self.test_url,
                 font=("Arial", 10), bg='#2196F3', fg='white', relief=tk.FLAT, 
                 padx=20, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(action_frame, text="Download", command=self.start_download,
                 font=("Arial", 10, "bold"), bg='#FF5722', fg='white', relief=tk.FLAT, 
                 padx=20, pady=8).pack(side=tk.LEFT)

        # Progress section
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                           mode="determinate", variable=self.progress)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready", 
                                    font=("Arial", 9), bg='#f0f0f0', fg='#666666')
        self.status_label.pack()

        # Log section
        log_frame = tk.Frame(main_frame, bg='#f0f0f0')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="Log:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0', fg='#333333').pack(anchor='w')
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(log_frame, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(text_frame, height=8, state='disabled', 
                               font=("Consolas", 9), bg='#ffffff', fg='#333333',
                               relief=tk.SOLID, bd=1)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initialize quality options
        self.update_quality_options()

    def update_quality_options(self):
        """Update quality options based on download type"""
        if self.download_type.get() == "video":
            self.quality_combo.configure(state="readonly")
            self.quality_label.configure(text="Video Quality:")
            self.quality_combo['values'] = ["Best", "1080p", "720p", "480p", "360p"]
            self.quality.set("720p")
        elif self.download_type.get() == "audio":
            self.quality_combo.configure(state="disabled")
            self.quality_label.configure(text="Audio Quality:")
            self.quality_combo['values'] = ["192k", "128k", "64k"]
            self.quality.set("192k")
        else:  # playlist
            self.quality_combo.configure(state="readonly")
            self.quality_label.configure(text="Video Quality:")
            self.quality_combo['values'] = ["720p", "480p", "360p"]
            self.quality.set("720p")

    def select_output_folder(self):
        """Select output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def log(self, message):
        """Add message to log"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def update_status(self, message):
        """Update status label"""
        self.status_label.configure(text=message)

    def progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress.set(percent)
                self.update_status(f"Downloading... {percent:.1f}%")
            elif 'downloaded_bytes' in d:
                self.update_status(f"Downloaded: {d['downloaded_bytes']} bytes")
        elif d['status'] == 'finished':
            self.progress.set(100)
            self.update_status("Download completed!")

    def test_url(self):
        """Test if URL is valid"""
        url = self.video_url.get()
        if not url:
            self.log("[ERROR] URL is empty")
            return

        self.log("[INFO] Testing URL...")
        self.update_status("Testing URL...")
        
        def test():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.log(f"[SUCCESS] URL is valid!")
                    self.log(f"[INFO] Title: {info.get('title', 'Unknown')}")
                    self.log(f"[INFO] Duration: {info.get('duration', 'Unknown')} seconds")
                    self.log(f"[INFO] Uploader: {info.get('uploader', 'Unknown')}")
                    self.update_status("URL is valid!")
                    
            except Exception as e:
                self.log(f"[ERROR] URL test failed: {e}")
                self.update_status("URL test failed!")
        
        threading.Thread(target=test, daemon=True).start()

    def start_download(self):
        """Start download process"""
        url = self.video_url.get()
        if not url:
            self.log("[ERROR] URL is empty")
            return

        self.progress.set(0)
        self.log("[INFO] Starting download...")
        self.update_status("Starting download...")
        
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        """Perform the actual download"""
        try:
            url = self.video_url.get()
            output = self.output_path.get()
            download_type = self.download_type.get()
            quality = self.quality.get()

            if download_type == "video":
                self.download_video(url, output, quality)
            elif download_type == "audio":
                self.download_audio(url, output, quality)
            elif download_type == "playlist":
                self.download_playlist(url, output, quality)

        except Exception as e:
            self.log(f"[ERROR] Download failed: {e}")
            self.update_status("Download failed!")

    def download_video(self, url, output, quality):
        """Download video"""
        try:
            self.log("[INFO] Starting video download...")
            
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
                'outtmpl': os.path.join(output, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.log("[SUCCESS] Video download completed!")
            self.update_status("Video download completed!")
            
        except Exception as e:
            self.log(f"[ERROR] Video download failed: {e}")
            self.update_status("Video download failed!")

    def download_audio(self, url, output, quality):
        """Download audio and convert to MP3"""
        try:
            self.log("[INFO] Starting audio download...")
            
            # Map quality to bitrate
            quality_map = {
                "192k": "192",
                "128k": "128",
                "64k": "64"
            }
            
            bitrate = quality_map.get(quality, "192")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.log("[SUCCESS] Audio download completed!")
            self.update_status("Audio download completed!")
            
        except Exception as e:
            self.log(f"[ERROR] Audio download failed: {e}")
            self.update_status("Audio download failed!")

    def download_playlist(self, url, output, quality):
        """Download playlist"""
        try:
            self.log("[INFO] Starting playlist download...")
            
            quality_map = {
                "720p": "best[height<=720]",
                "480p": "best[height<=480]",
                "360p": "best[height<=360]"
            }
            
            format_spec = quality_map.get(quality, "best[height<=720]")
            
            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output, '%(playlist_title)s/%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.log("[SUCCESS] Playlist download completed!")
            self.update_status("Playlist download completed!")
            
        except Exception as e:
            self.log(f"[ERROR] Playlist download failed: {e}")
            self.update_status("Playlist download failed!")

def main():
    try:
        root = tk.Tk()
        app = YouTubeDownloaderApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main() 