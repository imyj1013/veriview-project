import cv2
import sounddevice as sd
import numpy as np
import requests
import threading
import time
import logging
import os
import uuid
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DebateClient:
    def __init__(self, server_url="http://223.195.34.206:8080", user_id="mola", password="password"):
        self.server_url = server_url
        self.user_id = user_id
        self.password = password
        self.sample_rate = 16000
        self.chunk = 1024
        self.video_dir = os.path.join(os.getcwd(), "client_videos")
        self.token = None
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)

    def login(self):
        response = requests.post(
            f"{self.server_url}/api/auth/login",
            json={"user_id": self.user_id, "password": self.password}
        )
        if response.status_code != 200:
            raise Exception(f"로그인 실패: {response.json()['error']}")
        self.token = response.json()['token']
        logger.info("로그인 성공, 토큰 획득")

    def record_video(self, duration=10):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("웹캠을 열 수 없습니다.")
            return None

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = os.path.join(self.video_dir, f"{uuid.uuid4()}.mp4")
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

        audio_data = []
        def audio_callback(indata, frames, time, status):
            if status:
                logger.error(f"오디오 캡처 오류: {status}")
            audio_data.append(indata.copy())

        stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32',
                               blocksize=self.chunk, callback=audio_callback)

        start_time = time.time()
        with stream:
            while time.time() - start_time < duration:
                ret, frame = cap.read()
                if not ret:
                    logger.error("프레임 캡처 실패")
                    break
                out.write(frame)
                time.sleep(0.05)

        cap.release()
        out.release()

        import soundfile as sf
        audio_path = os.path.join(self.video_dir, "temp_audio.wav")
        audio = np.concatenate(audio_data) if audio_data else np.array([])
        sf.write(audio_path, audio, self.sample_rate)

        final_video_path = os.path.join(self.video_dir, f"{uuid.uuid4()}_final.mp4")
        os.system(f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac {final_video_path}")

        os.remove(video_path)
        os.remove(audio_path)
        return final_video_path

    def start(self):
        self.login()
        print("\n=== 토론 시작 ===")

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.server_url}/api/debate/start",
            json={"user_id": self.user_id},
            headers=headers
        )
        if response.status_code != 200:
            logger.error(f"토론 시작 실패: {response.json()['error']}")
            return
        data = response.json()
        topic = data["topic"]
        position = data["position"]
        debate_id = data["debate_id"]
        ai_opening_text = data["ai_opening_text"]
        logger.info(f"토론 주제: {topic}")
        logger.info(f"사용자 입장: {position}")
        logger.info(f"Debate ID: {debate_id}")
        print(f"주제: {topic}")
        print(f"사용자 입장: {position}")
        print(f"AI 입론: {ai_opening_text}")

        round_titles = ["입론", "반론", "재반론", "최종 변론"]
        endpoints = [
            ("opening-video", "ai-opening-video"),
            ("rebuttal-video", "ai-rebuttal-video"),
            ("counter-rebuttal-video", "ai-counter-rebuttal-video"),
            ("closing-video", "ai-closing-video")
        ]
        ai_endpoints = ["ai-rebuttal", "ai-counter-rebuttal", "ai-closing"]

        for round_num, (save_endpoint, analyze_endpoint) in enumerate(endpoints, 1):
            print(f"\n[{round_titles[round_num-1]}]")
            print("당신의 발언을 시작하세요 (10초 내 녹화)...")
            video_path = self.record_video(duration=10)
            if not video_path:
                logger.error("영상 녹화 실패")
                continue

            with open(video_path, 'rb') as f:
                files = {'video': f}
                response = requests.post(
                    f"{self.server_url}/api/debate/{debate_id}/{save_endpoint}",
                    files=files,
                    headers=headers
                )
                if response.status_code != 200:
                    logger.error(f"영상 업로드 실패: {response.json()['error']}")
                    continue
                print(response.json()["message"])

            with open(video_path, 'rb') as f:
                files = {'video': f}
                response = requests.post(
                    f"{self.server_url}/api/debate/{debate_id}/{analyze_endpoint}",
                    files=files,
                    headers=headers
                )
                if response.status_code != 200:
                    logger.error(f"영상 분석 실패: {response.json()['error']}")
                    continue
                result = response.json()
                phase_key = f"user_{round_titles[round_num-1].lower()}_text"
                print(f"사용자 발언: {result.get(phase_key, '발언 없음')}")
                print(f"피드백: {result['feedback']}")
                print(f"모범답안: {result['sample_answer']}")
                print(f"점수: 적극성({result['initiative_score']}), 협력({result['collaborative_score']}), "
                      f"의사소통({result['communication_score']}), 논리({result['logic_score']}), "
                      f"문제해결({result['problem_solving_score']}), 목소리({result['voice_score']}), "
                      f"행동({result['action_score']})")
                if round_num < 4:
                    ai_key = f"ai_{round_titles[round_num].lower()}_text"
                    print(f"AI {round_titles[round_num]}: {result.get(ai_key, 'AI 응답 없음')}")

            os.remove(video_path)

            if round_num < 4:
                response = requests.get(
                    f"{self.server_url}/api/debate/{debate_id}/{ai_endpoints[round_num-1]}",
                    headers=headers
                )
                if response.status_code == 200:
                    ai_key = f"ai_{round_titles[round_num].lower()}_text"
                    ai_text = response.json().get(ai_key, "AI 응답 없음")
                    print(f"AI {round_titles[round_num]}: {ai_text}")

            if round_num == 4:
                response = requests.get(
                    f"{self.server_url}/api/debate/{debate_id}/feedback",
                    headers=headers
                )
                if response.status_code == 200:
                    feedback = response.json()["debate_feedback"]
                    print("\n=== 최종 피드백 ===")
                    for i, fb in enumerate(feedback):
                        print(f"\n[{round_titles[i]}]")
                        print(f"발언: {fb['user_text']}")
                        print(f"피드백: {fb['feedback']}")
                        print(f"모범답안: {fb['sample_answer']}")
                        print(f"점수: 적극성({fb['initiative_score']}), 협력({fb['collaborative_score']}), "
                              f"의사소통({fb['communication_score']}), 논리({fb['logic_score']}), "
                              f"문제해결({fb['problem_solving_score']})")
                break

        print("\n=== 토론 종료 ===")

if __name__ == "__main__":
    client = DebateClient(server_url="http://223.195.34.206:8080", user_id="mola", password="password")
    client.start()