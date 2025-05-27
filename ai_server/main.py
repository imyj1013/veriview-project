#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 서버 보조 실행 파일
주 진입점은 server_runner.py이며, 이 파일은 보조적 역할
"""

import os
import sys

def main():
    """메인 함수 - server_runner.py 실행을 권장"""
    print("🔄 AI 서버 실행 요청")
    print("=" * 50)
    print("⚠️  주의: 이 파일은 보조 실행 파일입니다.")
    print("📌 권장 실행 방법:")
    print("   python server_runner.py")
    print("=" * 50)
    
    # 사용자 선택 옵션
    choice = input("\n계속 실행하시겠습니까? (y/N): ").lower().strip()
    
    if choice == 'y':
        print("\n🚀 AI 서버를 시작합니다...")
        
        # server_runner.py 실행
        try:
            import subprocess
            subprocess.run([sys.executable, "server_runner.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            print(f"❌ 서버 실행 실패: {e}")
            print("📌 직접 실행: python server_runner.py")
    else:
        print("\n👋 실행을 취소했습니다.")
        print("📌 올바른 실행 방법: python server_runner.py")

if __name__ == "__main__":
    main()
