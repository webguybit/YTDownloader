import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading
import subprocess
import urllib.request
import socket

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Downloader (Robust)")
        self.master.geometry("700x500")
        self.video_url = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.download_type = tk.StringVar(value="video")
        self.resolution = tk.StringVar(value="720p")
        self.formats = []
        self.progress = tk.DoubleVar()
        self.current_download_title = ""
        self.spinner_running = False
        self.spinner_label = tk.Label(self.master, text="", font=("Courier", 12))
        self.spinner_label.pack()

        self.create_widgets()

    # spinner start 
    def start_spinner(self, message="Processing"):
        self.spinner_running = True
        threading.Thread(target=self.animate_spinner, args=(message,), daemon=True).start()

    def stop_spinner(self):
        self.spinner_running = False
        self.spinner_label.config(text="")  # Clear

    def animate_spinner(self, message):
        frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        i = 0
        while self.spinner_running:
            frame = frames[i % len(frames)]
            self.spinner_label.config(text=f"{frame} {message}")
            i += 1
            self.master.update_idletasks()
            self.master.after(100)  # 10fps
    # spinner end
    
    def create_widgets(self):
        # URL input
        tk.Label(self.master, text="YouTube URL:").pack(pady=5)
        url_entry = tk.Entry(self.master, textvariable=self.video_url, width=70)
        url_entry.pack()
        url_entry.bind("<Control-v>", lambda e: self.master.clipboard_get())  # Paste

        # Download type
        tk.Label(self.master, text="Download Type:").pack(pady=5)
        type_frame = tk.Frame(self.master)
        type_frame.pack()
        for text, mode in [("Video", "video"), ("Audio (MP3)", "audio"), ("Playlist", "playlist")]:
            tk.Radiobutton(type_frame, text=text, variable=self.download_type, value=mode, command=self.update_type).pack(side=tk.LEFT, padx=5)

        # Resolution selection
        self.resolution_label = tk.Label(self.master, text="Select Resolution:")
        self.resolution_label.pack(pady=5)
        self.res_combo = ttk.Combobox(self.master, textvariable=self.resolution, state="readonly")
        self.res_combo.pack()

        # Output folder
        tk.Button(self.master, text="Browse Output Folder", command=self.select_output_folder).pack(pady=5)
        tk.Label(self.master, textvariable=self.output_path).pack()

        # Action buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Fetch Options", command=self.load_formats).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Download", command=self.start_download_thread).pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", mode="determinate", variable=self.progress)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Log area
        self.log_text = tk.Text(self.master, height=12, state='disabled')
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def test_connection(self):
        """Test internet connectivity and YouTube access"""
        self.log("[INFO] Testing connection...")
        self.start_spinner("Testing connection...")
        
        def test():
            try:
                # Test basic internet connectivity
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                self.log("[SUCCESS] Internet connection: OK")
                
                # Test YouTube access
                req = urllib.request.Request("https://www.youtube.com")
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                urllib.request.urlopen(req, timeout=10)
                self.log("[SUCCESS] YouTube access: OK")
                
                # Test yt-dlp
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Test with a simple video
                    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    ydl.extract_info(test_url, download=False)
                self.log("[SUCCESS] yt-dlp: OK")
                self.log("[INFO] All tests passed! You can now download videos.")
                
            except Exception as e:
                self.log(f"[ERROR] Connection test failed: {str(e)}")
                self.log("[INFO] Try checking your internet connection or firewall settings.")
            finally:
                self.stop_spinner()
        
        threading.Thread(target=test, daemon=True).start()

    def update_type(self):
        if self.download_type.get() == "video":
            self.res_combo.configure(state="readonly")
            self.resolution_label.configure(text="Select Resolution:")
        else:
            self.res_combo.configure(state="disabled")
            self.resolution_label.configure(text="")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress.set(percent)
        elif d['status'] == 'finished':
            self.progress.set(100)

    def load_formats(self):
        url = self.video_url.get()
        if not url:
            self.log("[ERROR] URL is empty")
            return

        self.log("[INFO] Fetching available formats...")
        self.start_spinner("Fetching formats...")
        
        def fetch():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if self.download_type.get() == "video":
                        formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                        resolutions = sorted(set(f.get('resolution', 'N/A') for f in formats if f.get('resolution')), reverse=True)
                        self.res_combo['values'] = resolutions
                        self.res_combo.set("720p" if "720p" in resolutions else resolutions[0] if resolutions else "720p")
                        self.log(f"[INFO] Found resolutions: {resolutions}")
                        self.log(f"[INFO] Video title: {info.get('title', 'Unknown')}")
                    
                    self.formats = info.get('formats', [])
                    
            except Exception as e:
                self.log(f"[ERROR] Failed to fetch formats: {str(e)}")
                self.log("[INFO] Try running 'Test Connection' first to check your setup.")
            finally:
                self.stop_spinner()
        
        threading.Thread(target=fetch, daemon=True).start()

    def start_download_thread(self):
        threading.Thread(target=self.download).start()

    def download(self):
        try:
            url = self.video_url.get()
            output = self.output_path.get()
            self.progress.set(0)
            self.start_spinner("Downloading...")

            if self.download_type.get() == "video":
                ydl_opts = {
                    'format': f'best[height<={self.resolution.get().replace("p", "")}]',
                    'outtmpl': os.path.join(output, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.log("[INFO] Starting video download...")
                    ydl.download([url])
                    self.log("[SUCCESS] Video downloaded.")

            elif self.download_type.get() == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.log("[INFO] Starting audio download...")
                    ydl.download([url])
                    self.log("[SUCCESS] MP3 downloaded.")

            elif self.download_type.get() == "playlist":
                ydl_opts = {
                    'format': 'best[height<=720]',
                    'outtmpl': os.path.join(output, '%(playlist_title)s/%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.log("[INFO] Starting playlist download...")
                    ydl.download([url])
                    self.log("[SUCCESS] Playlist download complete.")

        except Exception as e:
            self.log(f"[ERROR] Download failed: {str(e)}")
            self.log("[INFO] Try running 'Test Connection' to diagnose the issue.")

        finally:
            self.stop_spinner()

# Launch
if __name__ == '__main__':
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop() 