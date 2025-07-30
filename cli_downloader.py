#!/usr/bin/env python3
"""
Simple YouTube Downloader - Command Line Version
No GUI, no Tkinter, just pure command line interface
"""

import sys
import os
from pytube import YouTube, Playlist
import subprocess

def print_banner():
    print("=" * 50)
    print("    YouTube Downloader - CLI Version")
    print("=" * 50)

def get_user_input():
    """Get download parameters from user"""
    print("\nEnter YouTube URL:")
    url = input("> ").strip()
    
    if not url:
        print("[ERROR] URL cannot be empty")
        return None
    
    print("\nSelect download type:")
    print("1. Video")
    print("2. Audio (MP3)")
    print("3. Playlist")
    
    while True:
        try:
            choice = input("Enter choice (1-3): ").strip()
            if choice == "1":
                download_type = "video"
                break
            elif choice == "2":
                download_type = "audio"
                break
            elif choice == "3":
                download_type = "playlist"
                break
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    
    print("\nEnter output directory (press Enter for current directory):")
    output_dir = input("> ").strip()
    if not output_dir:
        output_dir = os.getcwd()
    
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"[INFO] Created directory: {output_dir}")
        except Exception as e:
            print(f"[ERROR] Cannot create directory: {e}")
            return None
    
    return {
        'url': url,
        'type': download_type,
        'output': output_dir
    }

def test_url(url):
    """Test if URL is valid"""
    print(f"[INFO] Testing URL: {url}")
    try:
        yt = YouTube(url)
        print(f"[SUCCESS] URL is valid!")
        print(f"[INFO] Title: {yt.title}")
        print(f"[INFO] Length: {yt.length} seconds")
        print(f"[INFO] Available streams: {len(yt.streams)}")
        return True
    except Exception as e:
        print(f"[ERROR] URL test failed: {e}")
        return False

def download_video(url, output_dir):
    """Download video"""
    try:
        print("[INFO] Fetching video information...")
        yt = YouTube(url)
        
        print(f"[INFO] Downloading: {yt.title}")
        
        # Get best quality video
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            print("[ERROR] No suitable video stream found")
            return False
        
        print(f"[INFO] Selected quality: {stream.resolution}")
        print("[INFO] Starting download...")
        
        # Download with progress
        def progress_callback(stream, chunk, bytes_remaining):
            total = stream.filesize
            downloaded = total - bytes_remaining
            percent = (downloaded / total) * 100
            print(f"\r[INFO] Download progress: {percent:.1f}%", end='', flush=True)
        
        yt.register_on_progress_callback(progress_callback)
        
        file_path = stream.download(output_path=output_dir)
        print(f"\n[SUCCESS] Video downloaded: {file_path}")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False

def download_audio(url, output_dir):
    """Download audio and convert to MP3"""
    try:
        print("[INFO] Fetching audio information...")
        yt = YouTube(url)
        
        print(f"[INFO] Downloading audio: {yt.title}")
        
        # Get best audio stream
        stream = yt.streams.filter(only_audio=True).first()
        
        if not stream:
            print("[ERROR] No audio stream found")
            return False
        
        print("[INFO] Starting audio download...")
        
        # Download with progress
        def progress_callback(stream, chunk, bytes_remaining):
            total = stream.filesize
            downloaded = total - bytes_remaining
            percent = (downloaded / total) * 100
            print(f"\r[INFO] Download progress: {percent:.1f}%", end='', flush=True)
        
        yt.register_on_progress_callback(progress_callback)
        
        # Download audio file
        out_file = stream.download(output_path=output_dir)
        print(f"\n[INFO] Audio downloaded: {out_file}")
        
        # Convert to MP3
        print("[INFO] Converting to MP3...")
        mp3_file = os.path.splitext(out_file)[0] + ".mp3"
        
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", out_file, mp3_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # Remove original file
            os.remove(out_file)
            print(f"[SUCCESS] MP3 saved: {mp3_file}")
            return True
            
        except subprocess.CalledProcessError:
            print("[WARNING] FFmpeg not found or failed. Keeping original audio file.")
            return True
        except FileNotFoundError:
            print("[WARNING] FFmpeg not found. Install FFmpeg for MP3 conversion.")
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Audio download failed: {e}")
        return False

def download_playlist(url, output_dir):
    """Download playlist"""
    try:
        print("[INFO] Fetching playlist information...")
        pl = Playlist(url)
        
        print(f"[INFO] Playlist: {pl.title}")
        print(f"[INFO] Videos in playlist: {len(pl.videos)}")
        
        success_count = 0
        total_count = len(pl.videos)
        
        for i, video in enumerate(pl.videos, 1):
            try:
                print(f"\n[{i}/{total_count}] Downloading: {video.title}")
                
                stream = video.streams.filter(progressive=True, file_extension='mp4').first()
                if stream:
                    stream.download(output_path=output_dir)
                    success_count += 1
                    print(f"[SUCCESS] Downloaded: {video.title}")
                else:
                    print(f"[ERROR] No stream found for: {video.title}")
                    
            except Exception as e:
                print(f"[ERROR] Failed to download: {video.title} - {e}")
        
        print(f"\n[SUCCESS] Playlist download complete!")
        print(f"[INFO] Successfully downloaded: {success_count}/{total_count} videos")
        return True
        
    except Exception as e:
        print(f"[ERROR] Playlist download failed: {e}")
        return False

def main():
    print_banner()
    
    while True:
        try:
            # Get user input
            params = get_user_input()
            if not params:
                continue
            
            # Test URL first
            if not test_url(params['url']):
                print("\n[ERROR] Invalid URL. Please try again.")
                continue
            
            # Perform download based on type
            success = False
            if params['type'] == "video":
                success = download_video(params['url'], params['output'])
            elif params['type'] == "audio":
                success = download_audio(params['url'], params['output'])
            elif params['type'] == "playlist":
                success = download_playlist(params['url'], params['output'])
            
            if success:
                print("\n[SUCCESS] Download completed successfully!")
            else:
                print("\n[ERROR] Download failed!")
            
            # Ask if user wants to download another
            print("\nDownload another? (y/n):")
            choice = input("> ").strip().lower()
            if choice not in ['y', 'yes']:
                print("Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main() 