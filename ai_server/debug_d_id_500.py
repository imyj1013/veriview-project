#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 500 에러 디버깅
다양한 요청 형식으로 테스트
"""

import os
import requests
import base64
from dotenv import load_dotenv
import json

# .env 파일 로드
load_dotenv()

# API 키 설정
api_key = os.environ.get('D_ID_API_KEY', '').strip()
username, password = api_key.split(':', 1)
credentials = f"{username}:{password}"
encoded = base64.b64encode(credentials.encode()).decode('ascii')

headers = {
    'Authorization': f'Basic {encoded}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

base_url = "https://api.d-id.com"

print("=== D-ID API 500 에러 디버깅 ===\n")

# 테스트 1: 가장 간단한 요청
print("1. 최소 요청 데이터")
data1 = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
    "script": {
        "type": "text",
        "input": "Hello"
    }
}

try:
    response = requests.post(f"{base_url}/talks", headers=headers, json=data1)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    if response.status_code == 201:
        print("✅ 성공!")
except Exception as e:
    print(f"❌ 오류: {str(e)}\n")

# 테스트 2: 다른 아바타 이미지
print("2. 다른 아바타 이미지 URL")
data2 = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Maya_front_thumbnail_v3.jpg",
    "script": {
        "type": "text",
        "input": "Hello"
    }
}

try:
    response = requests.post(f"{base_url}/talks", headers=headers, json=data2)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
except Exception as e:
    print(f"❌ 오류: {str(e)}\n")

# 테스트 3: Express Avatars 엔드포인트 시도
print("3. Express Avatars 엔드포인트 테스트")
express_data = {
    "presenter_id": "amy-jcwCkr1grs",
    "script": {
        "type": "text",
        "input": "Hello"
    }
}

try:
    response = requests.post(f"{base_url}/talks", headers=headers, json=express_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
except Exception as e:
    print(f"❌ 오류: {str(e)}\n")

# 테스트 4: 스트림 엔드포인트
print("4. Streams 엔드포인트 테스트")
stream_data = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg"
}

try:
    response = requests.post(f"{base_url}/talks/streams", headers=headers, json=stream_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
except Exception as e:
    print(f"❌ 오류: {str(e)}\n")

# 테스트 5: 사용 가능한 프레젠터 목록 확인
print("5. 사용 가능한 프레젠터 확인")
try:
    response = requests.get(f"{base_url}/presenters", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        presenters = response.json()
        print(f"프레젠터 수: {len(presenters.get('presenters', []))}")
        if presenters.get('presenters'):
            first_presenter = presenters['presenters'][0]
            print(f"첫 번째 프레젠터: {json.dumps(first_presenter, indent=2)}")
except Exception as e:
    print(f"응답: {response.text[:200] if 'response' in locals() else str(e)}\n")

# 테스트 6: 크레딧 확인
print("6. 크레딧 잔액 확인")
try:
    response = requests.get(f"{base_url}/credits", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
except Exception as e:
    print(f"❌ 오류: {str(e)}\n")

print("="*60)
print("\n💡 500 에러 해결 방법:")
print("1. 크레딧이 부족한 경우 - Trial Plan은 제한적")
print("2. 아바타 이미지 URL이 유효하지 않은 경우")
print("3. D-ID 서버 일시적 문제")
print("4. Express Avatars를 사용해야 하는 경우")
print("\n권장: 샘플 비디오 모드를 계속 사용하세요 (PREFERRED_AVATAR_SERVICE=SAMPLE)")
