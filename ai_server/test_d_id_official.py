#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 테스트 - 공식 문서 기반
https://docs.d-id.com/reference/basic-authentication
"""

import os
import requests
import base64
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 가져오기
api_key = os.environ.get('D_ID_API_KEY', '').strip()
print(f"API Key from .env: {api_key}")
print(f"API Key length: {len(api_key)}")
print(f"API Key preview: {api_key[:30]}...{api_key[-20:]}")
print()

# D-ID 공식 문서에 따른 Basic Authentication
# username:password 형식이면 base64 인코딩
if ':' in api_key:
    print("API 키에 콜론(:)이 포함되어 있습니다.")
    username, password = api_key.split(':', 1)
    print(f"Username: {username}")
    print(f"Password preview: {password[:10]}...{password[-10:]}")
    
    # base64 인코딩
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode('ascii')
    auth_header = f"Basic {encoded}"
    print(f"Encoded auth: Basic {encoded[:30]}...")
else:
    # 단일 API 키인 경우
    print("단일 API 키 형식입니다.")
    auth_header = f"Basic {api_key}"

headers = {
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

base_url = "https://api.d-id.com"

print("\n=== D-ID API 연결 테스트 ===")

# 1. GET /talks 테스트
print("\n1. GET /talks")
try:
    response = requests.get(
        f"{base_url}/talks",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("✅ 인증 성공!")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 2. POST /talks 테스트
print("\n2. POST /talks (영상 생성)")
data = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
    "script": {
        "type": "text",
        "input": "Hello, this is a test message."
    }
}

try:
    response = requests.post(
        f"{base_url}/talks",
        headers=headers,
        json=data,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 201:
        print("✅ 영상 생성 요청 성공!")
        result = response.json()
        print(f"Talk ID: {result.get('id')}")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

print("\n" + "="*60)
print("\n💡 문제 해결 가이드:")
print("\n1. 401 Unauthorized 오류가 발생하면:")
print("   - D-ID Studio에서 새 API 키를 생성하세요")
print("   - API 키가 올바른 형식인지 확인하세요")
print("\n2. D-ID API 키 형식:")
print("   - 일반적으로 매우 긴 문자열 (100자 이상)")
print("   - JWT 토큰 형식일 수 있음")
print("   - 또는 특수한 인코딩된 문자열")
print("\n3. 올바른 API 키 얻기:")
print("   a. https://studio.d-id.com 로그인")
print("   b. Settings → API Keys")
print("   c. 'Create New' 클릭")
print("   d. 생성된 키 전체 복사")
print("   e. .env 파일에 붙여넣기")
