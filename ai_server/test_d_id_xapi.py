#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 간단한 테스트
x-api-key 헤더 방식 테스트
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키
api_key = os.environ.get('D_ID_API_KEY')
print(f"API Key: {api_key}\n")

# x-api-key 헤더 사용
headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

base_url = "https://api.d-id.com"

# 1. 연결 테스트
print("=== 연결 테스트 ===")
response = requests.get(f"{base_url}/talks", headers=headers)
print(f"GET /talks - Status: {response.status_code}")
if response.status_code != 200:
    print(f"Response: {response.text}\n")

# 2. Talk 생성 테스트
print("\n=== Talk 생성 테스트 ===")
data = {
    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
    "script": {
        "type": "text",
        "input": "Hello, this is a test from Junho Jeong."
    }
}

response = requests.post(
    f"{base_url}/talks",
    headers=headers,
    json=data
)

print(f"POST /talks - Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\n✅ Talk 생성 성공!")
    result = response.json()
    talk_id = result.get('id')
    print(f"Talk ID: {talk_id}")
    
    # 3. Talk 상태 확인
    print("\n=== Talk 상태 확인 ===")
    status_response = requests.get(
        f"{base_url}/talks/{talk_id}",
        headers=headers
    )
    print(f"GET /talks/{talk_id} - Status: {status_response.status_code}")
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"Talk Status: {status_data.get('status')}")
        print(f"Created At: {status_data.get('created_at')}")
