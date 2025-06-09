#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API Bearer Token 테스트
D-ID의 최신 API는 Bearer 토큰을 사용할 가능성이 높음
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 실제 D-ID API 키 형식 예시
print("=== D-ID API 키 형식 안내 ===")
print("D-ID API 키는 일반적으로 다음과 같은 형식입니다:")
print("1. 긴 랜덤 문자열 (예: 'ZGlkOmV5SnpJam9pTW1FME1tRTRZV0V0TURCa1ppMDBOMkZqTFRrNU5HTXRaR1UxWldGaFpqZGhOR1JoSW4wLkVrUmZWMGx3...')")
print("2. UUID 형식 (예: 'did_1234567890abcdef')")
print("3. JWT 토큰 형식 (점(.)으로 구분된 긴 문자열)")
print()

# API 키 가져오기
api_key = os.environ.get('D_ID_API_KEY', '').strip()

if not api_key:
    print("❌ D_ID_API_KEY가 설정되지 않았습니다.")
    exit(1)

print(f"현재 API Key 길이: {len(api_key)} 문자")
print(f"API Key 첫 20자: {api_key[:20]}...")
print(f"API Key 마지막 10자: ...{api_key[-10:]}")
print()

# Bearer 토큰으로 테스트
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

base_url = "https://api.d-id.com"

print("=== Bearer Token 인증 테스트 ===")
try:
    # /talks 엔드포인트는 실제 talk 목록을 반환
    response = requests.get(f"{base_url}/talks", headers=headers)
    print(f"GET /talks - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Bearer 토큰 인증 성공!")
        data = response.json()
        print(f"Talks count: {len(data.get('talks', []))}")
    else:
        print(f"Response: {response.text}")
        
        # 다른 엔드포인트 시도
        print("\n다른 엔드포인트 테스트...")
        
        # /credits 엔드포인트 테스트
        response2 = requests.get(f"{base_url}/credits", headers=headers)
        print(f"GET /credits - Status: {response2.status_code}")
        if response2.status_code == 200:
            print("✅ /credits 엔드포인트 성공!")
            print(f"Response: {response2.text}")
        else:
            print(f"Response: {response2.text}")
            
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}")

print("\n" + "="*60)
print("\n💡 해결 방법:")
print("1. D-ID Studio (https://studio.d-id.com)에 로그인")
print("2. 상단 메뉴에서 'API' 또는 'Settings' 클릭")
print("3. 'API Keys' 섹션에서 'Create New API Key' 클릭")
print("4. 생성된 API 키를 완전히 복사 (Show 버튼 클릭 후)")
print("5. .env 파일의 D_ID_API_KEY= 뒤에 붙여넣기")
print("6. 따옴표 없이 키만 입력 (예: D_ID_API_KEY=your_actual_key_here)")
