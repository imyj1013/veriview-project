#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-ID API 인증 디버깅
모든 가능한 인증 방식 테스트
"""

import os
import requests
import base64
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키
api_key = os.environ.get('D_ID_API_KEY')
print(f"Raw API Key: {api_key}\n")

# API 키 분석
if ':' in api_key:
    parts = api_key.split(':', 1)
    print(f"Part 1: {parts[0]}")
    print(f"Part 2: {parts[1]}")
    
    # Part 1을 base64 디코딩 시도
    try:
        decoded = base64.b64decode(parts[0]).decode('utf-8')
        print(f"Part 1 decoded: {decoded}")
    except:
        print("Part 1 is not base64")
    print()

base_url = "https://api.d-id.com"

# 테스트할 모든 인증 방식
auth_methods = [
    # 1. Bearer token (API 키 전체)
    {
        "name": "Bearer (full key)",
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    },
    
    # 2. x-api-key 헤더 (API 키 전체)
    {
        "name": "x-api-key (full key)",
        "headers": {
            "x-api-key": api_key,
            "Accept": "application/json"
        }
    },
    
    # 3. Basic Auth (API 키 전체)
    {
        "name": "Basic (full key)",
        "headers": {
            "Authorization": f"Basic {api_key}",
            "Accept": "application/json"
        }
    },
    
    # 4. 만약 키가 이미 인코딩된 경우, 디코딩 후 재인코딩
    {
        "name": "Basic (re-encoded)",
        "headers": None
    },
    
    # 5. Bearer token (두 번째 부분만)
    {
        "name": "Bearer (part 2 only)",
        "headers": None
    },
    
    # 6. x-api-key (두 번째 부분만)
    {
        "name": "x-api-key (part 2 only)",
        "headers": None
    }
]

# 키가 : 로 구분된 경우 추가 처리
if ':' in api_key:
    username, password = api_key.split(':', 1)
    
    # username이 base64인 경우 디코딩
    try:
        decoded_username = base64.b64decode(username).decode('utf-8')
        # email:password 형식으로 재인코딩
        new_auth = base64.b64encode(f"{decoded_username}:{password}".encode()).decode()
        auth_methods[3]["headers"] = {
            "Authorization": f"Basic {new_auth}",
            "Accept": "application/json"
        }
    except:
        pass
    
    # password 부분만 사용
    auth_methods[4]["headers"] = {
        "Authorization": f"Bearer {password}",
        "Accept": "application/json"
    }
    
    auth_methods[5]["headers"] = {
        "x-api-key": password,
        "Accept": "application/json"
    }

print("=== D-ID API 인증 테스트 ===\n")

for method in auth_methods:
    if method["headers"] is None:
        continue
        
    print(f"테스트: {method['name']}")
    
    try:
        # GET /talks로 인증 테스트
        response = requests.get(
            f"{base_url}/talks",
            headers=method["headers"],
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 인증 성공!")
            print(f"Response preview: {response.text[:100]}...")
            print("\n" + "="*60 + "\n")
            
            # 성공한 방식으로 talk 생성 테스트
            print(f"Talk 생성 테스트 ({method['name']})")
            
            create_headers = method["headers"].copy()
            create_headers["Content-Type"] = "application/json"
            
            data = {
                "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noam_front_thumbnail.jpg",
                "script": {
                    "type": "text",
                    "input": "Hello, test from Junho."
                }
            }
            
            create_response = requests.post(
                f"{base_url}/talks",
                headers=create_headers,
                json=data,
                timeout=30
            )
            
            print(f"Create Status: {create_response.status_code}")
            print(f"Create Response: {create_response.text}")
            break
            
        elif response.status_code == 401:
            print("❌ 인증 실패 (401)")
            error_msg = response.text[:100] if response.text else "No error message"
            print(f"Error: {error_msg}")
        else:
            print(f"❓ 기타 응답: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
    
    print("-" * 40 + "\n")

# D-ID 공식 문서 확인 안내
print("\nℹ️ D-ID API 키 확인 방법:")
print("1. https://studio.d-id.com 에 로그인")
print("2. API Key 탭에서 'Show' 버튼 클릭")
print("3. 표시된 전체 API 키를 복사")
print("4. .env 파일의 D_ID_API_KEY에 붙여넣기")
