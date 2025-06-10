#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영상 파일 진단 도구
D-ID에서 생성된 영상 파일 검증
"""

import os
import glob
import subprocess
from datetime import datetime

def check_video_files():
    """영상 파일 검사"""
    print("=== D-ID 영상 파일 진단 ===\n")
    
    # 영상 디렉토리 확인
    base_dirs = [
        'videos',
        'videos/cache',
        'videos/interviews',
        'videos/debates',
        'videos/cache/debates',
        'videos/cache/interviews'
    ]
    
    for dir_path in base_dirs:
        if os.path.exists(dir_path):
            print(f"\n디렉토리: {dir_path}")
            # 모든 mp4 파일 찾기
            video_files = glob.glob(os.path.join(dir_path, '**/*.mp4'), recursive=True)
            
            if video_files:
                print(f"  파일 수: {len(video_files)}")
                for video_file in video_files[:5]:  # 최대 5개만 표시
                    file_size = os.path.getsize(video_file)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(video_file))
                    print(f"  - {os.path.basename(video_file)}: {file_size:,} bytes, 수정: {modified_time}")
                    
                    # ffprobe로 영상 정보 확인 (설치되어 있는 경우)
                    try:
                        result = subprocess.run(
                            ['ffprobe', '-v', 'error', '-show_entries', 
                             'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                             video_file],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            duration = float(result.stdout.strip())
                            print(f"    영상 길이: {duration:.1f}초")
                    except:
                        pass
            else:
                print("  파일 없음")
        else:
            print(f"\n디렉토리 없음: {dir_path}")
    
    # 최근 생성된 파일 확인
    print("\n\n=== 최근 생성된 영상 파일 (전체 검색) ===")
    all_videos = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.mp4'):
                file_path = os.path.join(root, file)
                all_videos.append((file_path, os.path.getmtime(file_path)))
    
    # 시간순 정렬
    all_videos.sort(key=lambda x: x[1], reverse=True)
    
    for video_path, mtime in all_videos[:10]:  # 최근 10개
        file_size = os.path.getsize(video_path)
        modified = datetime.fromtimestamp(mtime)
        print(f"\n{video_path}")
        print(f"  크기: {file_size:,} bytes")
        print(f"  수정: {modified}")
        
        # 0바이트 파일 검사
        if file_size == 0:
            print("  ⚠️ 경고: 0바이트 파일!")

if __name__ == "__main__":
    check_video_files()
