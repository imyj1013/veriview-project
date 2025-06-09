#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 D-ID API 테스트
500 에러 디버깅용
"""

import os
import requests
import base64
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 설정
api_key = os.environ.get('D_ID_API_KEY')
print(f"API Key: {api_key[:20]}...")

# Basic Auth 헤더 생성
encoded_key = base64.b64encode(api_key.encode()).decode('ascii')
headers = {
    'Authorization': f'Basic {encoded_key}',
    'Content-Type': 'application/json'
}

# 1. 가장 간단한 요청으로 테스트
print("\n=== 최소 요청 테스트 ===")
data = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
    "script": {
        "type": "text",
        "input": "Hello"
    }
}

response = requests.post(
    "https://api.d-id.com/talks",
    headers=headers,
    json=data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# 2. 다른 엔드포인트 테스트
print("\n=== Actors 엔드포인트 테스트 ===")
response = requests.get(
    "https://api.d-id.com/actors",
    headers=headers
)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500] if response.status_code == 200 else response.text}")
