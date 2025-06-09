#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 인증 테스트
여러 인증 방식을 시도하여 올바른 방식 확인
"""

import os
import requests
import base64
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키
api_key = os.environ.get('D_ID_API_KEY')
print(f"API Key from env: {api_key}\n")

# 테스트할 인증 방식들
auth_methods = [
    # 1. API 키를 그대로 Basic으로 사용
    ("Basic (raw)", f"Basic {api_key}"),
    
    # 2. API 키를 Bearer로 사용
    ("Bearer", f"Bearer {api_key}"),
    
    # 3. API 키를 base64 인코딩하여 Basic으로 사용
    ("Basic (encoded)", f"Basic {base64.b64encode(api_key.encode()).decode()}"),
    
    # 4. username과 password를 분리하여 인코딩 (이미 :로 구분된 경우)
    ("Basic (user:pass encoded)", None)
]

# username:password 형식인 경우 처리
if ':' in api_key:
    username, password = api_key.split(':', 1)
    encoded_auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    auth_methods[3] = ("Basic (user:pass encoded)", f"Basic {encoded_auth}")

# 각 인증 방식 테스트
base_url = "https://api.d-id.com"
test_endpoint = "/talks"

print("=== D-ID API 인증 테스트 ===\n")

for method_name, auth_header in auth_methods:
    if auth_header is None:
        continue
        
    print(f"테스트: {method_name}")
    print(f"Header: {auth_header[:50]}...")
    
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    try:
        # GET 요청으로 인증 테스트
        response = requests.get(
            f"{base_url}{test_endpoint}",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 인증 성공!")
            print(f"Response: {response.text[:200]}...")
        elif response.status_code == 401:
            print("❌ 인증 실패 (401 Unauthorized)")
            print(f"Error: {response.text}")
        elif response.status_code == 403:
            print("⚠️ 권한 없음 (403 Forbidden)")
            print(f"Error: {response.text}")
        elif response.status_code == 404:
            print("⚠️ 엔드포인트 없음 (404) - 인증은 성공했을 수 있음")
        else:
            print(f"❓ 기타 응답: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
    
    print("-" * 60 + "\n")

# 간단한 talk 생성 테스트
print("\n=== Talk 생성 테스트 (가장 성공적인 인증 방식 사용) ===\n")

# Bearer 토큰 방식으로 시도
headers = {
    'Authorization': f'Basic {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

test_data = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
    "script": {
        "type": "text",
        "input": "Hello, this is a test."
    }
}

try:
    response = requests.post(
        f"{base_url}/talks",
        headers=headers,
        json=test_data,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("\n✅ Talk 생성 성공!")
    else:
        print("\n❌ Talk 생성 실패")
        
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}")
