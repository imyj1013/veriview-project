import cv2
import subprocess
import os
import tempfile
import logging
import threading
import queue
import time
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RealtimeFacialAnalysis:
    def __init__(self, openface_path=os.getenv("OPENFACE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "FeatureExtraction.exe")), 
                 output_dir=os.path.join(os.getcwd(), "facial_output")):
        self.openface_path = openface_path
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.result_queue = queue.Queue()
        self.running = False
        if not os.path.exists(self.openface_path):
            logger.error(f"OpenFace 실행 파일을 찾을 수 없습니다: {self.openface_path}")
            raise FileNotFoundError(f"OpenFace 실행 파일이 존재하지 않습니다: {self.openface_path}")

    def analyze_image(self, temp_path):
        output_csv = os.path.join(self.output_dir, "temp_output.csv")
        command = f'"{self.openface_path}" -f "{temp_path}" -out_dir "{self.output_dir}" -q'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            logger.debug(f"OpenFace 출력: {result.stdout}")
            if os.path.exists(output_csv):
                with open(output_csv, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        last_line = lines[-1].strip().split(',')
                        result = {
                            "confidence": float(last_line[1]),
                            "gaze_angle_x": float(last_line[5]),
                            "gaze_angle_y": float(last_line[6]),
                            "AU01_r": float(last_line[-10]),
                            "AU02_r": float(last_line[-9]),
                        }
                        return result
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenFace 실행 실패: {e.stderr}")
            return None
        except ValueError as e:
            logger.error(f"CSV 파싱 오류: {str(e)}")
            return None
        finally:
            if os.path.exists(output_csv):
                os.remove(output_csv)

    def analyze_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"영상 파일 열기 실패: {video_path}")
            return None
        results = []
        frame_count = 0
        max_frames = 30
        while cap.isOpened() and frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir=self.output_dir) as temp_file:
                temp_path = temp_file.name
                cv2.imwrite(temp_path, frame)
                result = self.analyze_image(temp_path)
                if result:
                    results.append(result)
                os.remove(temp_path)
            frame_count += 1
        cap.release()
        if results:
            avg_result = {
                "confidence": np.mean([r["confidence"] for r in results]),
                "gaze_angle_x": np.mean([r["gaze_angle_x"] for r in results]),
                "gaze_angle_y": np.mean([r["gaze_angle_y"] for r in results]),
                "AU01_r": np.mean([r["AU01_r"] for r in results]),
                "AU02_r": np.mean([r["AU02_r"] for r in results]),
            }
            return avg_result
        return None

    def evaluate_emotion(self, analysis_result):
        if not analysis_result:
            return "분석 결과 없음"
        au01 = analysis_result.get("AU01_r", 0)
        au02 = analysis_result.get("AU02_r", 0)
        gaze_x = analysis_result.get("gaze_angle_x", 0)
        gaze_y = analysis_result.get("gaze_angle_y", 0)
        
        if au01 > 1.0 and au02 > 1.0:
            return "긍정적 (자신감 있는 미소)"
        elif au01 < 0.5 and au02 < 0.5 and abs(gaze_x) < 0.2 and abs(gaze_y) < 0.2:
            return "중립 (안정적)"
        elif au01 > 1.5 or au02 > 1.5:
            return "긴장 (불안 또는 놀람)"
        else:
            return "부정적 (불편 또는 망설임)"

    def calculate_scores(self, analysis_result, text):
        if not analysis_result or not text:
            return {
                "initiative_score": 1.0,
                "collaborative_score": 1.0,
                "communication_score": 1.0,
                "logic_score": 1.0,
                "problem_solving_score": 1.0,
                "voice_score": 1.0,
                "action_score": 1.0,
                "feedback": "분석 결과 또는 텍스트가 없습니다.",
                "sample_answer": "AI는 인간의 삶의 질을 향상시켜주고 활용도가 높습니다."
            }
        initiative_score = min(5.0, 3.0 + analysis_result["confidence"])
        collaborative_score = min(5.0, 3.0 + (1.0 if "협력" in text else 0.0))
        communication_score = min(5.0, 3.0 + (1.0 if len(text) > 20 else 0.0))
        logic_score = min(5.0, 3.0 + (1.0 if "논리" in text or "근거" in text else 0.0))
        problem_solving_score = min(5.0, 3.0 + (1.0 if "해결" in text else 0.0))
        voice_score = min(5.0, 3.0 + analysis_result["confidence"] * 0.5)
        action_score = min(5.0, 3.0 - abs(analysis_result["gaze_angle_x"]) - abs(analysis_result["gaze_angle_y"]))
        
        feedback = (
            f"적극성: {'적극적' if initiative_score > 3 else '소극적'}. "
            f"협력: {'협력적' if collaborative_score > 3 else '개선 필요'}. "
            f"의사소통: {'명확' if communication_score > 3 else '불명확'}. "
            f"논리: {'논리적' if logic_score > 3 else '논리 부족'}. "
            f"문제해결: {'우수' if problem_solving_score > 3 else '개선 필요'}. "
            f"목소리: {'안정적' if voice_score > 3 else '불안정'}. "
            f"행동: {'안정적' if action_score > 3 else '시선 불안정'}."
        )
        
        return {
            "initiative_score": initiative_score,
            "collaborative_score": collaborative_score,
            "communication_score": communication_score,
            "logic_score": logic_score,
            "problem_solving_score": problem_solving_score,
            "voice_score": voice_score,
            "action_score": action_score,
            "feedback": feedback,
            "sample_answer": "AI는 인간의 삶의 질을 향상시켜주고 활용도가 높습니다."
        }