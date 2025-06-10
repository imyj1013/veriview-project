#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
생성된 D-ID 영상 파일 검사
"""

import os
import subprocess
import json
from datetime import datetime

# 영상 디렉토리
video_dir = r"C:\Users\junsa\capstone_7\veriview-project\ai_server\videos\cache\debates"

print("=== D-ID 생성 영상 파일 검사 ===\n")

# 디렉토리의 모든 mp4 파일 찾기
if os.path.exists(video_dir):
    video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print(f"영상 파일이 없습니다: {video_dir}")
    else:
        print(f"발견된 영상 파일: {len(video_files)}개\n")
        
        for video_file in video_files[:5]:  # 최근 5개만
            video_path = os.path.join(video_dir, video_file)
            
            print(f"파일: {video_file}")
            
            # 파일 크기
            file_size = os.path.getsize(video_path)
            print(f"  크기: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # 파일 생성 시간
            mtime = os.path.getmtime(video_path)
            print(f"  생성: {datetime.fromtimestamp(mtime)}")
            
            # ffprobe로 영상 정보 확인 (설치되어 있는 경우)
            try:
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', video_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    
                    # 영상 길이
                    duration = float(info.get('format', {}).get('duration', 0))
                    print(f"  길이: {duration:.2f}초")
                    
                    # 비디오 스트림 정보
                    for stream in info.get('streams', []):
                        if stream.get('codec_type') == 'video':
                            print(f"  해상도: {stream.get('width')}x{stream.get('height')}")
                            print(f"  코덱: {stream.get('codec_name')}")
                            break
                else:
                    print("  (ffprobe 사용 불가)")
                    
            except FileNotFoundError:
                print("  (ffprobe가 설치되지 않음)")
            except Exception as e:
                print(f"  (영상 정보 확인 실패: {e})")
            
            print()
else:
    print(f"디렉토리가 존재하지 않습니다: {video_dir}")

print("\n영상 파일 검사 팁:")
print("1. 파일 크기가 너무 작으면 (< 100KB) 영상이 비어있을 수 있습니다")
print("2. ffprobe로 실제 영상 길이를 확인할 수 있습니다")
print("3. VLC 플레이어 등으로 직접 재생해보세요")
