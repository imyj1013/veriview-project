#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VeriView AI 서버 V2 - 마이크로서비스 아키텍처 버전
API Gateway를 통한 마이크로서비스 통합
"""
import subprocess
import sys
import time
import os
import signal
import logging
from typing import List, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MicroserviceManager:
    """마이크로서비스 관리자"""
    
    def __init__(self):
        self.services = {
            "api_gateway": {
                "script": "api_gateway.py",
                "port": 5000,
                "name": "API Gateway"
            },
            "speech_service": {
                "script": "microservices/speech_service.py", 
                "port": 5001,
                "name": "Speech Service"
            },
            "vision_service": {
                "script": "microservices/vision_service.py",
                "port": 5002,
                "name": "Vision Service"
            },
            "nlp_service": {
                "script": "microservices/nlp_service.py",
                "port": 5003,
                "name": "NLP Service"
            },
            "tts_service": {
                "script": "microservices/tts_service.py",
                "port": 5004,
                "name": "TTS Service"
            },
            "job_service": {
                "script": "microservices/job_recommendation_service.py",
                "port": 5005,
                "name": "Job Recommendation Service"
            }
        }
        self.processes = {}
        
    def start_redis(self):
        """Redis 서버 시작"""
        try:
            # Redis가 이미 실행 중인지 확인
            result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
            if result.stdout.strip() == "PONG":
                logger.info("Redis가 이미 실행 중입니다.")
                return True
        except:
            pass
        
        # Redis 시작
        try:
            if sys.platform == "win32":
                # Windows에서는 WSL을 통해 실행하거나 Windows용 Redis 사용
                logger.warning("Windows에서 Redis를 시작하려면 별도로 설치하고 실행해주세요.")
                logger.info("Redis 없이도 동기 모드로 작동 가능합니다.")
                return False
            else:
                # Linux/Mac에서 Redis 시작
                subprocess.Popen(["redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)
                logger.info("Redis 서버가 시작되었습니다.")
                return True
        except Exception as e:
            logger.error(f"Redis 시작 실패: {str(e)}")
            return False
    
    def start_service(self, service_key: str):
        """개별 서비스 시작"""
        service = self.services[service_key]
        script_path = service["script"]
        
        # 실제 파일이 없으면 기본 서버 사용
        if service_key == "api_gateway":
            script_path = "api_gateway.py"
            if not os.path.exists(script_path):
                # API Gateway가 없으면 기존 main_server.py 사용
                logger.warning(f"API Gateway 파일이 없습니다. 기존 main_server.py를 사용합니다.")
                script_path = "main_server.py"
        
        try:
            cmd = [sys.executable, script_path]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[service_key] = process
            logger.info(f"{service['name']} 시작됨 (포트: {service['port']})")
            return True
        except Exception as e:
            logger.error(f"{service['name']} 시작 실패: {str(e)}")
            return False
    
    def start_all(self):
        """모든 서비스 시작"""
        print("=" * 80)
        print(" VeriView 마이크로서비스 아키텍처 시작")
        print("=" * 80)
        
        # Redis 시작
        redis_started = self.start_redis()
        
        # API Gateway 먼저 시작
        if not self.start_service("api_gateway"):
            logger.error("API Gateway 시작 실패. 기존 모드로 전환합니다.")
            # 기존 main_server.py 직접 실행
            os.system(f"{sys.executable} main_server.py")
            return
        
        time.sleep(2)
        
        # 나머지 서비스들 시작 (파일이 있는 경우에만)
        for service_key in ["speech_service", "nlp_service", "job_service"]:
            if os.path.exists(self.services[service_key]["script"]):
                self.start_service(service_key)
                time.sleep(1)
        
        print("=" * 80)
        print(" 서비스 상태:")
        print(f"   - Redis: {'✅ 실행 중' if redis_started else '❌ 미실행 (동기 모드)'}")
        for service_key, process in self.processes.items():
            service = self.services[service_key]
            status = "✅ 실행 중" if process.poll() is None else "❌ 중지됨"
            print(f"   - {service['name']}: {status} (포트: {service['port']})")
        print("=" * 80)
        print(" 주요 기능:")
        print("   - 스트리밍 AI 응답: http://localhost:5000/ai/debate/{debate_id}/ai-response-stream")
        print("   - 비동기 영상 처리: http://localhost:5000/ai/debate/{debate_id}/opening-video")
        print("   - 면접 실시간 피드백: http://localhost:5000/ai/interview/{interview_id}/answer-stream")
        print("   - 서비스 상태: http://localhost:5000/ai/health")
        print("=" * 80)
        
    def stop_all(self):
        """모든 서비스 중지"""
        logger.info("모든 서비스를 중지합니다...")
        
        for service_key, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logger.info(f"{self.services[service_key]['name']} 중지됨")
        
        # Redis 중지 시도
        try:
            subprocess.run(["redis-cli", "shutdown"], capture_output=True)
            logger.info("Redis 서버 중지됨")
        except:
            pass
    
    def monitor(self):
        """서비스 모니터링"""
        try:
            while True:
                time.sleep(5)
                
                # 서비스 상태 확인
                for service_key, process in self.processes.items():
                    if process.poll() is not None:
                        logger.warning(f"{self.services[service_key]['name']}가 중지되었습니다. 재시작 시도...")
                        self.start_service(service_key)
                
        except KeyboardInterrupt:
            logger.info("서비스 모니터링 중지")
            self.stop_all()

def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info("종료 신호 받음")
    manager.stop_all()
    sys.exit(0)

if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 마이크로서비스 매니저 생성
    manager = MicroserviceManager()
    
    # 모든 서비스 시작
    manager.start_all()
    
    # 서비스 모니터링
    manager.monitor()
