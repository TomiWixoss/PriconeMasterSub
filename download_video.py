"""
Script tải video từ YouTube sử dụng yt-dlp
Cài đặt: pip install yt-dlp ffmpeg

Sử dụng:
    python download_video.py <url> [options]
    
Ví dụ:
    python download_video.py https://youtu.be/R1-PWEqsS8c
    python download_video.py https://youtu.be/R1-PWEqsS8c -s 00:01:30 -e 00:02:45
    python download_video.py https://youtu.be/R1-PWEqsS8c --start 00:00:10 --end 00:00:30
"""

import argparse
import os
import yt_dlp

def download_video(url, output_folder="output", filename="video.mp4", start_time=None, end_time=None):
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
    
    # Thêm tùy chọn cắt video nếu có start/end time
    if start_time or end_time:
        download_ranges = []
        if start_time and end_time:
            download_ranges = [{'start_time': start_time, 'end_time': end_time}]
        elif start_time:
            download_ranges = [{'start_time': start_time}]
        elif end_time:
            download_ranges = [{'end_time': end_time}]
        
        ydl_opts['download_ranges'] = lambda info, ydl: download_ranges
        ydl_opts['force_keyframes_at_cuts'] = True
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Đang tải video từ: {url}")
        if start_time or end_time:
            print(f"  - Từ: {start_time or '00:00:00'}")
            print(f"  - Đến: {end_time or 'hết video'}")
        ydl.download([url])
        print(f"Đã tải xong: {output_path}")

def parse_time(time_str):
    """Chuyển đổi hh:mm:ss thành số giây"""
    if not time_str:
        return None
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(parts[0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tải video từ YouTube")
    parser.add_argument("url", help="URL video YouTube")
    parser.add_argument("-d", "--dir", default="output", help="Thư mục output (mặc định: output)")
    parser.add_argument("-o", "--output", default="video.mp4", help="Tên file video (mặc định: video.mp4)")
    parser.add_argument("-s", "--start", help="Thời gian bắt đầu (hh:mm:ss hoặc mm:ss)")
    parser.add_argument("-e", "--end", help="Thời gian kết thúc (hh:mm:ss hoặc mm:ss)")
    
    args = parser.parse_args()
    
    start = parse_time(args.start)
    end = parse_time(args.end)
    
    download_video(args.url, args.dir, args.output, start, end)
