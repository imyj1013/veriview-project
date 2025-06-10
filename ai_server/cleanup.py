#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 정리 스크립트
불필요한 테스트 파일 제거
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """불필요한 파일 제거"""
    
    # 제거할 파일 목록
    files_to_remove = [
        'test_d_id_integration.py',
        'quick_test.py',
        'create_sample_videos.py',
        'create_minimal_samples.py',
        'run_integrated_server.py',
        'RUN_GUIDE.py',
        'd_id_config.json',
        'd_id_working_config.json',
        'fix_ai_server_issues.py',
        'AI_SERVER_INTEGRATION_GUIDE.md'
    ]
    
    removed_count = 0
    for filename in files_to_remove:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"✅ 삭제됨: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ 삭제 실패: {filename} - {e}")
        else:
            print(f"⏭️  없음: {filename}")
    
    # 샘플 비디오 디렉토리 제거 (선택사항)
    sample_dir = Path('videos/samples')
    if sample_dir.exists():
        try:
            shutil.rmtree(sample_dir)
            print(f"✅ 디렉토리 삭제됨: {sample_dir}")
        except Exception as e:
            print(f"❌ 디렉토리 삭제 실패: {sample_dir} - {e}")
    
    print(f"\n총 {removed_count}개 파일 삭제됨")

def main():
    print("="*60)
    print("VeriView AI 서버 정리")
    print("="*60)
    
    print("\n불필요한 테스트 파일을 제거합니다.")
    response = input("계속하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        cleanup_files()
        print("\n✅ 정리 완료!")
        
        print("\n남은 주요 파일:")
        print("- run.py: 서버 실행기")
        print("- server_runner_d_id.py: 메인 서버")
        print("- modules/d_id/: D-ID 통합 모듈")
        print("- D_ID_GUIDE.py: 실행 가이드")
        print("- .env: 환경 설정")
    else:
        print("\n취소되었습니다.")

if __name__ == "__main__":
    main()
