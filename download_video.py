"""
Script tải video từ YouTube sử dụng yt-dlp
Cài đặt: pip install yt-dlp

Sử dụng:
    python download_video.py <url> [output]
    
Ví dụ:
    python download_video.py https://youtu.be/R1-PWEqsS8c
    python download_video.py https://youtu.be/R1-PWEqsS8c my_video.mp4
"""

import argparse
import os
import yt_dlp

def download_video(url, output_folder="output", filename="video.mp4"):
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_path = os.path.join(output_folder, filename)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Đang tải video từ: {url}")
        ydl.download([url])
        print(f"Đã tải xong: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tải video từ YouTube")
    parser.add_argument("url", help="URL video YouTube")
    parser.add_argument("-d", "--dir", default="output", help="Thư mục output (mặc định: output)")
    parser.add_argument("-o", "--output", default="video.mp4", help="Tên file video (mặc định: video.mp4)")
    
    args = parser.parse_args()
    download_video(args.url, args.dir, args.output)
