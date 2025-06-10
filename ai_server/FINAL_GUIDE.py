#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 최종 실행 가이드

D-ID API를 통한 AI 아바타 영상 생성
- 개인면접: AI 면접관
- 토론면접: AI 토론자
"""

print("="*80)
print("🚀 VeriView AI 서버 - D-ID API 통합 완료")
print("="*80)

print("\n📋 주요 기능:")
print("1. D-ID API를 통한 실사 AI 아바타 영상 생성")
print("2. 한국어 TTS 자동 포함 (D-ID 내장)")
print("3. 개인면접 AI 면접관 영상")
print("4. 토론면접 AI 토론자 영상")

print("\n🔧 필수 설정:")
print("1. D-ID API 키 발급")
print("   - https://studio.d-id.com 에서 회원가입")
print("   - API Keys → Create New Key")
print("   - 무료 플랜: 월 5분 제한")

print("\n2. .env 파일 설정")
print("   D_ID_API_KEY=your_actual_api_key_here")
print("   (username:password 형식)")

print("\n🚀 서버 실행:")
print("python run.py")

print("\n📡 주요 API 엔드포인트:")

print("\n[개인면접]")
print("POST /ai/interview/generate-question")
print("POST /ai/interview/{id}/{type}/answer-video")
print("POST /ai/interview/{id}/genergate-followup-question")
print("POST /ai/interview/next-question-video ← D-ID 영상")

print("\n[토론면접]")
print("POST /ai/debate/{id}/ai-opening")
print("POST /ai/debate/{id}/opening-video")
print("POST /ai/debate/ai-opening-video ← D-ID 영상")
print("POST /ai/debate/ai-rebuttal-video ← D-ID 영상")
print("POST /ai/debate/ai-counter-rebuttal-video ← D-ID 영상")
print("POST /ai/debate/ai-closing-video ← D-ID 영상")

print("\n[공고 추천]")
print("POST /ai/recruitment/posting")

print("\n💡 동작 흐름:")
print("1. 백엔드 → AI 서버: 텍스트 전송")
print("2. AI 서버 → D-ID API: 영상 생성 요청")
print("3. D-ID API: TTS + 아바타 영상 생성")
print("4. AI 서버 → 백엔드: MP4 영상 반환")
print("5. 프론트엔드: 영상 재생")

print("\n🧪 테스트:")
print("1. python run.py 실행")
print("2. http://localhost:5000/ai/test 접속")
print("3. D-ID 연결 상태 확인")
print("4. 백엔드/프론트엔드에서 면접/토론 시작")

print("\n❌ 제거된 기능:")
print("- 로컬 TTS (D-ID에서 처리)")
print("- 테스트용 샘플 비디오 (실제 D-ID 사용)")
print("- 불필요한 테스트 코드")

print("\n✅ 준비 완료!")
print("python run.py 로 서버를 시작하세요.")
print("="*80)
