import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube, Playlist
import os
import threading
import subprocess
import sys

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Downloader (Simple)")
        self.master.geometry("600x450")
        self.video_url = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.download_type = tk.StringVar(value="video")
        self.resolution = tk.StringVar(value="720p")
        self.streams = []
        self.progress = tk.DoubleVar()
        self.spinner_running = False
        self.spinner_label = tk.Label(self.master, text="", font=("Courier", 12))
        self.spinner_label.pack()

        self.create_widgets()

    def start_spinner(self, message="Processing"):
        self.spinner_running = True
        threading.Thread(target=self.animate_spinner, args=(message,), daemon=True).start()

    def stop_spinner(self):
        self.spinner_running = False
        self.spinner_label.config(text="")

    def animate_spinner(self, message):
        frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        i = 0
        while self.spinner_running:
            frame = frames[i % len(frames)]
            self.spinner_label.config(text=f"{frame} {message}")
            i += 1
            self.master.update_idletasks()
            self.master.after(100)
    
    def create_widgets(self):
        # URL input
        tk.Label(self.master, text="YouTube URL:").pack(pady=5)
        url_entry = tk.Entry(self.master, textvariable=self.video_url, width=60)
        url_entry.pack()
        url_entry.bind("<Control-v>", lambda e: self.master.clipboard_get())

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
        tk.Button(button_frame, text="Test URL", command=self.test_url).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Fetch Options", command=self.load_streams).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Download", command=self.start_download_thread).pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", mode="determinate", variable=self.progress)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Log area
        self.log_text = tk.Text(self.master, height=10, state='disabled')
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def test_url(self):
        """Test if the URL is valid and accessible"""
        url = self.video_url.get()
        if not url:
            self.log("[ERROR] URL is empty")
            return

        self.log("[INFO] Testing URL...")
        self.start_spinner("Testing URL...")
        
        def test():
            try:
                yt = YouTube(url)
                self.log(f"[SUCCESS] URL is valid!")
                self.log(f"[INFO] Video title: {yt.title}")
                self.log(f"[INFO] Video length: {yt.length} seconds")
                self.log(f"[INFO] Available streams: {len(yt.streams)}")
                
            except Exception as e:
                self.log(f"[ERROR] URL test failed: {str(e)}")
                self.log("[INFO] Try a different URL or check your internet connection.")
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

    def on_progress(self, stream, chunk, bytes_remaining):
        try:
            total = stream.filesize
            downloaded = total - bytes_remaining
            percent = downloaded / total * 100
            self.progress.set(percent)
        except:
            pass

    def load_streams(self):
        url = self.video_url.get()
        if not url:
            self.log("[ERROR] URL is empty")
            return

        self.log("[INFO] Fetching available streams...")
        self.start_spinner("Fetching streams...")
        
        def fetch():
            try:
                if self.download_type.get() == "video":
                    yt = YouTube(url)
                    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
                    self.streams = list(streams)
                    resolutions = sorted(set(s.resolution for s in streams if s.resolution), reverse=True)
                    self.res_combo['values'] = resolutions
                    self.res_combo.set("720p" if "720p" in resolutions else resolutions[0] if resolutions else "720p")
                    self.log(f"[INFO] Found resolutions: {resolutions}")
                    self.log(f"[INFO] Video title: {yt.title}")
                
            except Exception as e:
                self.log(f"[ERROR] Failed to fetch streams: {str(e)}")
                self.log("[INFO] Try running 'Test URL' first to check the URL.")
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
                yt = YouTube(url, on_progress_callback=self.on_progress)
                stream = yt.streams.filter(progressive=True, file_extension='mp4', res=self.resolution.get()).first()
                if stream:
                    self.log(f"[INFO] Downloading video: {yt.title}")
                    stream.download(output_path=output)
                    self.log("[SUCCESS] Video downloaded.")
                else:
                    self.log("[ERROR] No suitable stream found for the selected resolution.")

            elif self.download_type.get() == "audio":
                yt = YouTube(url, on_progress_callback=self.on_progress)
                stream = yt.streams.filter(only_audio=True).first()
                if stream:
                    self.log(f"[INFO] Downloading audio: {yt.title}")
                    out_file = stream.download(output_path=output)
                    mp3_file = os.path.splitext(out_file)[0] + ".mp3"
                    self.log(f"[INFO] Converting to MP3...")
                    self.start_spinner("Converting to MP3...")
                    subprocess.run(["ffmpeg", "-y", "-i", out_file, mp3_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    os.remove(out_file)
                    self.log(f"[SUCCESS] MP3 saved: {mp3_file}")
                else:
                    self.log("[ERROR] No audio stream found.")

            elif self.download_type.get() == "playlist":
                pl = Playlist(url)
                self.log(f"[INFO] Downloading playlist: {pl.title}")
                for video in pl.videos:
                    stream = video.streams.filter(progressive=True, file_extension='mp4').first()
                    if stream:
                        self.log(f"[INFO] Downloading: {video.title}")
                        stream.download(output_path=output)
                self.log("[SUCCESS] Playlist download complete.")

        except Exception as e:
            self.log(f"[ERROR] Download failed: {str(e)}")
            self.log("[INFO] Try running 'Test URL' to check if the URL is valid.")

        finally:
            self.stop_spinner()

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = YouTubeDownloaderApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1) 