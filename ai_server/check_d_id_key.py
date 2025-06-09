#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 키 검증 도구
올바른 D-ID API 키인지 확인
"""

import os
import sys

def check_api_key():
    """API 키 형식 검증"""
    
    print("=== D-ID API 키 검증 도구 ===\n")
    
    # 환경 변수에서 키 가져오기
    api_key = os.environ.get('D_ID_API_KEY', '')
    
    if not api_key:
        print("D_ID_API_KEY가 설정되지 않았습니다.")
        return False
    
    print(f"API 키 길이: {len(api_key)} 문자")
    
    # D-ID API 키 특징 검사
    issues = []
    
    # 1. 길이 검사 (일반적으로 100자 이상)
    if len(api_key) < 100:
        issues.append(f"API 키가 너무 짧습니다 ({len(api_key)}자). D-ID API 키는 일반적으로 100자 이상입니다.")
    
    # 2. JWT 토큰 형식 검사
    if api_key.count('.') >= 2:
        print("JWT 토큰 형식으로 보입니다.")
        parts = api_key.split('.')
        print(f"   - Header 길이: {len(parts[0])}")
        print(f"   - Payload 길이: {len(parts[1])}")
        print(f"   - Signature 길이: {len(parts[2])}")
    else:
        # 3. UUID 형식 검사
        if api_key.startswith('did_'):
            print("D-ID UUID 형식으로 보입니다.")
        else:
            issues.append("JWT 토큰이나 UUID 형식이 아닙니다.")
    
    # 4. 의심스러운 패턴 검사
    if ':' in api_key:
        issues.append("콜론(:)이 포함되어 있습니다. 이는 D-ID API 키가 아닐 수 있습니다.")
    
    if api_key.startswith('Basic ') or api_key.startswith('Bearer '):
        issues.append("인증 헤더가 포함되어 있습니다. API 키만 입력하세요.")
    
    # 결과 출력
    print("\n" + "="*50)
    if issues:
        print("\n문제점:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n올바른 D-ID API 키가 아닌 것 같습니다.")
        return False
    else:
        print("\nD-ID API 키 형식이 올바른 것 같습니다.")
        return True

def show_instructions():
    """올바른 API 키 얻는 방법 안내"""
    print("\n" + "="*50)
    print("\n올바른 D-ID API 키 얻는 방법:\n")
    print("1. https://studio.d-id.com 에 로그인")
    print("2. 우측 상단 프로필 → 'API Keys' 클릭")
    print("3. 'Create New' 버튼 클릭")
    print("4. API 키 이름 입력 (예: 'VeriView')")
    print("5. 생성된 API 키 전체를 복사")
    print("   - 키는 한 번만 표시됩니다!")
    print("   - 키는 매우 깁니다 (200-500자)")
    print("6. .env 파일에 붙여넣기:")
    print("   D_ID_API_KEY=여기에_긴_API_키_붙여넣기")
    print("\n팁: 따옴표나 공백 없이 키만 입력하세요.")

if __name__ == "__main__":
    # .env 파일 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # API 키 검증
    is_valid = check_api_key()
    
    # 안내 표시
    if not is_valid:
        show_instructions()
    
    print("\n" + "="*50)
    
    # 샘플 모드 안내
    if not is_valid:
        print("\n임시 해결책:")
        print("API 키 문제가 해결될 때까지 샘플 비디오 모드를 사용하세요.")
        print(".env 파일에서: PREFERRED_AVATAR_SERVICE=SAMPLE")
