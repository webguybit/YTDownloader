#!/usr/bin/env python3
"""
YouTube Downloader - CLI Version using yt-dlp
More reliable than pytube, handles YouTube changes better
"""

import sys
import os
import yt_dlp
import subprocess

def print_banner():
    print("=" * 50)
    print("    YouTube Downloader - yt-dlp CLI Version")
    print("=" * 50)

def get_user_input():
    """Get download parameters from user"""
    print("\nEnter YouTube URL:")
    url = input("> ").strip()
    
    if not url:
        print("[ERROR] URL cannot be empty")
        return None
    
    print("\nSelect download type:")
    print("1. Video (Best quality)")
    print("2. Video (720p)")
    print("3. Video (480p)")
    print("4. Audio (MP3)")
    print("5. Playlist")
    
    while True:
        try:
            choice = input("Enter choice (1-5): ").strip()
            if choice == "1":
                download_type = "video_best"
                break
            elif choice == "2":
                download_type = "video_720"
                break
            elif choice == "3":
                download_type = "video_480"
                break
            elif choice == "4":
                download_type = "audio"
                break
            elif choice == "5":
                download_type = "playlist"
                break
            else:
                print("Please enter 1-5")
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
    """Test if URL is valid using yt-dlp"""
    print(f"[INFO] Testing URL: {url}")
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"[SUCCESS] URL is valid!")
            print(f"[INFO] Title: {info.get('title', 'Unknown')}")
            print(f"[INFO] Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"[INFO] Uploader: {info.get('uploader', 'Unknown')}")
            return True
            
    except Exception as e:
        print(f"[ERROR] URL test failed: {e}")
        return False

def progress_hook(d):
    """Progress callback for yt-dlp"""
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes']:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            print(f"\r[INFO] Download progress: {percent:.1f}%", end='', flush=True)
        elif 'downloaded_bytes' in d:
            print(f"\r[INFO] Downloaded: {d['downloaded_bytes']} bytes", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\n[INFO] Download completed: {d['filename']}")

def download_video(url, output_dir, quality="best"):
    """Download video with specified quality"""
    try:
        print("[INFO] Starting video download...")
        
        if quality == "best":
            format_spec = "best[height<=1080]"
        elif quality == "720":
            format_spec = "best[height<=720]"
        elif quality == "480":
            format_spec = "best[height<=480]"
        else:
            format_spec = "best"
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"\n[SUCCESS] Video download completed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Video download failed: {e}")
        return False

def download_audio(url, output_dir):
    """Download audio and convert to MP3"""
    try:
        print("[INFO] Starting audio download...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"\n[SUCCESS] Audio download completed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Audio download failed: {e}")
        return False

def download_playlist(url, output_dir):
    """Download playlist"""
    try:
        print("[INFO] Starting playlist download...")
        
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"\n[SUCCESS] Playlist download completed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Playlist download failed: {e}")
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
            if params['type'] == "video_best":
                success = download_video(params['url'], params['output'], "best")
            elif params['type'] == "video_720":
                success = download_video(params['url'], params['output'], "720")
            elif params['type'] == "video_480":
                success = download_video(params['url'], params['output'], "480")
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