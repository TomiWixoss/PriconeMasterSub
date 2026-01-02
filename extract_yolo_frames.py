"""
Script tự động tải video và trích xuất frames theo các mốc thời gian cụ thể cho training YOLO
Sử dụng: python extract_yolo_frames.py
"""

import os
import cv2
import yt_dlp

VIDEO_URL = "https://youtu.be/R1-PWEqsS8c"
OUTPUT_DIR = "output"
VIDEO_FILE = os.path.join(OUTPUT_DIR, "video.mp4")

# Định nghĩa các đoạn cần trích xuất
SEGMENTS = {
    "textbox_namebox": {
        "description": "Textbox + Namebox samples",
        "timestamps": [
            # Đoạn Ames (Nền tiên cảnh)
            ("00:05", "00:06", 2),
            ("00:15", "00:16", 2),
            ("00:47", "00:48", 2),
            ("01:15", "01:16", 2),
            # Đoạn Kokkoro (Nền thành phố ban ngày)
            ("02:52", "02:53", 2),
            ("03:10", "03:11", 2),
            ("03:45", "03:46", 2),
            ("04:20", "04:21", 2),
            # Đoạn Suzume (Nền thành phố, góc nhìn khác)
            ("07:05", "07:06", 2),
            ("07:30", "07:31", 2),
            ("08:20", "08:21", 2),
            ("09:05", "09:06", 2),
            # Đoạn Anime (Textbox đè lên cảnh hành động) - QUAN TRỌNG
            ("06:48", "07:02", 10),  # 10 FPS để lấy nhiều frame
            ("10:35", "11:00", 10),
        ]
    },
    "choice_box": {
        "description": "Choice Box samples",
        "timestamps": [
            ("09:54", "09:56", 15),  # Lấy nhiều frame liên tiếp
        ]
    },
    "negative_samples": {
        "description": "Negative samples (không có textbox)",
        "timestamps": [
            ("06:20", "06:45", 2),   # Cảnh quảng trường
            ("10:11", "10:30", 2),   # Cảnh hành động
            ("02:35", "02:36", 2),   # Màn hình chuyển cảnh
            ("02:45", "02:46", 2),   # Tên chương
        ]
    }
}

def parse_time(time_str):
    """Chuyển mm:ss hoặc hh:mm:ss thành giây"""
    parts = time_str.split(':')
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    return float(parts[0])

def get_all_time_ranges():
    """Lấy tất cả các khoảng thời gian cần tải"""
    ranges = []
    for group_data in SEGMENTS.values():
        for start_time, end_time, _ in group_data['timestamps']:
            start_sec = parse_time(start_time)
            end_sec = parse_time(end_time)
            ranges.append({'start_time': start_sec, 'end_time': end_sec})
    return ranges

def download_video():
    """Tải chỉ các đoạn cần thiết từ YouTube"""
    if os.path.exists(VIDEO_FILE):
        print(f"Video đã tồn tại: {VIDEO_FILE}")
        return True
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    download_ranges = get_all_time_ranges()
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': VIDEO_FILE,
        'quiet': False,
        'download_ranges': lambda info, ydl: download_ranges,
        'force_keyframes_at_cuts': True,
    }
    
    print(f"Đang tải {len(download_ranges)} đoạn video từ: {VIDEO_URL}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])
    print(f"Đã tải xong: {VIDEO_FILE}")
    return True

def extract_frames_from_segment(cap, start_sec, end_sec, fps_extract, output_folder, prefix, counter):
    """Trích xuất frames từ một đoạn video"""
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(1, int(original_fps / fps_extract))
    
    start_frame = int(start_sec * original_fps)
    end_frame = int(end_sec * original_fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    current_frame = start_frame
    saved = 0
    
    while current_frame < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        
        if (current_frame - start_frame) % frame_interval == 0:
            filename = f"{prefix}_{counter:04d}.jpg"
            filepath = os.path.join(output_folder, filename)
            cv2.imwrite(filepath, frame)
            counter += 1
            saved += 1
        
        current_frame += 1
    
    return counter, saved

def main():
    # Tải video
    if not download_video():
        return
    
    # Mở video
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        print(f"Không thể mở video: {VIDEO_FILE}")
        return
    
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"\nVideo FPS: {original_fps}")
    
    total_saved = 0
    
    # Trích xuất từng nhóm
    for group_name, group_data in SEGMENTS.items():
        output_folder = os.path.join(OUTPUT_DIR, "frames", group_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        print(f"\n{'='*50}")
        print(f"Đang xử lý: {group_data['description']}")
        print(f"Output: {output_folder}")
        
        counter = 0
        group_saved = 0
        
        for start_time, end_time, fps_extract in group_data['timestamps']:
            start_sec = parse_time(start_time)
            end_sec = parse_time(end_time)
            
            counter, saved = extract_frames_from_segment(
                cap, start_sec, end_sec, fps_extract,
                output_folder, group_name, counter
            )
            group_saved += saved
            print(f"  {start_time} - {end_time}: {saved} frames")
        
        print(f"Tổng {group_name}: {group_saved} frames")
        total_saved += group_saved
    
    cap.release()
    
    print(f"\n{'='*50}")
    print(f"HOÀN THÀNH! Tổng cộng: {total_saved} frames")
    print(f"Frames được lưu tại: {os.path.join(OUTPUT_DIR, 'frames')}")
    print("\nCấu trúc thư mục:")
    print("  output/frames/textbox_namebox/  - Ảnh có textbox + namebox")
    print("  output/frames/choice_box/       - Ảnh có choice box")
    print("  output/frames/negative_samples/ - Ảnh không có UI (negative)")

if __name__ == "__main__":
    main()
