"""
Script tách video thành ảnh sử dụng OpenCV
Cài đặt: pip install opencv-python

Sử dụng:
    python extract_frames.py <video> [options]
    
Ví dụ:
    python extract_frames.py video.mp4
    python extract_frames.py video.mp4 -o images -f 2
    python extract_frames.py video.mp4 --output my_frames --fps 0.5
"""

import argparse
import cv2
import os

def extract_frames(video_path, output_folder="frames", fps=1):
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Mở video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Không thể mở video: {video_path}")
        return
    
    # Lấy FPS gốc của video
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / original_fps
    
    print(f"Video info:")
    print(f"  - FPS gốc: {original_fps}")
    print(f"  - Tổng số frame: {total_frames}")
    print(f"  - Thời lượng: {duration:.2f} giây")
    print(f"  - Sẽ trích xuất ~{int(duration * fps)} ảnh ({fps} FPS)")
    
    # Tính khoảng cách giữa các frame cần lấy
    frame_interval = int(original_fps / fps)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Lưu frame theo interval
        if frame_count % frame_interval == 0:
            output_path = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            print(f"Đã lưu: {output_path}")
        
        frame_count += 1
    
    cap.release()
    print(f"\nHoàn thành! Đã trích xuất {saved_count} ảnh vào thư mục '{output_folder}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tách video thành ảnh")
    parser.add_argument("video", help="Đường dẫn file video")
    parser.add_argument("-o", "--output", default="output/frames", help="Thư mục output (mặc định: output/frames)")
    parser.add_argument("-f", "--fps", type=float, default=1, help="Số ảnh/giây cần trích xuất (mặc định: 1)")
    
    args = parser.parse_args()
    extract_frames(args.video, args.output, args.fps)
