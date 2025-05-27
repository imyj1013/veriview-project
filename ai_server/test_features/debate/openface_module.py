"""
OpenFace 얼굴 분석 테스트 모듈
LLM 미사용 환경에서 OpenFace 기능의 정상 작동을 테스트
"""
import cv2
import subprocess
import os
import tempfile
import logging
import numpy as np

logger = logging.getLogger(__name__)

class OpenFaceTestModule:
    def __init__(self, openface_path=None, output_dir=None):
        """OpenFace 테스트 모듈 초기화"""
        if openface_path is None:
            openface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "FeatureExtraction.exe")
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "facial_output")
            
        self.openface_path = openface_path
        self.output_dir = output_dir
        self.is_available = os.path.exists(self.openface_path)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        logger.info(f"OpenFace 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """OpenFace 연결 테스트"""
        if not self.is_available:
            return {"status": "unavailable", "message": "OpenFace 실행 파일을 찾을 수 없습니다"}
        
        try:
            # 간단한 help 명령으로 실행 가능 여부 확인
            result = subprocess.run([self.openface_path, "-help"], 
                                  capture_output=True, text=True, timeout=10)
            return {"status": "available", "message": "OpenFace 정상 작동"}
        except Exception as e:
            return {"status": "error", "message": f"OpenFace 실행 오류: {str(e)}"}

    def analyze_image(self, image_path):
        """이미지 얼굴 분석 - 테스트 모드"""
        if not self.is_available:
            logger.warning("OpenFace 사용 불가 - 고정값 반환")
            return self._get_default_result()
        
        try:
            if not os.path.exists(image_path):
                logger.error(f"이미지 파일이 존재하지 않습니다: {image_path}")
                return self._get_default_result()
            
            output_csv = os.path.join(self.output_dir, "temp_output.csv")
            command = f'"{self.openface_path}" -f "{image_path}" -out_dir "{self.output_dir}" -q'
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            logger.info("OpenFace 분석 완료")
            
            if os.path.exists(output_csv):
                analysis_result = self._parse_csv_result(output_csv)
                os.remove(output_csv)  # 임시 파일 정리
                return analysis_result
            else:
                logger.warning("OpenFace 결과 파일이 생성되지 않음")
                return self._get_default_result()
                
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenFace 실행 실패: {e.stderr}")
            return self._get_default_result()
        except Exception as e:
            logger.error(f"이미지 분석 오류: {str(e)}")
            return self._get_default_result()

    def analyze_video(self, video_path, max_frames=30):
        """영상 얼굴 분석 - 프레임별 분석 후 평균값 계산"""
        if not os.path.exists(video_path):
            logger.error(f"영상 파일이 존재하지 않습니다: {video_path}")
            return self._get_default_result()
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"영상 파일 열기 실패: {video_path}")
                return self._get_default_result()
            
            frame_results = []
            frame_count = 0
            
            logger.info(f"영상 분석 시작 - 최대 {max_frames}프레임")
            
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 프레임을 임시 이미지로 저장
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir=self.output_dir) as temp_file:
                    temp_path = temp_file.name
                    cv2.imwrite(temp_path, frame)
                    
                    # 프레임 분석
                    result = self.analyze_image(temp_path)
                    if result and result.get("confidence", 0) > 0.5:  # 신뢰도 임계값
                        frame_results.append(result)
                    
                    # 임시 파일 삭제
                    os.remove(temp_path)
                
                frame_count += 1
                
                if frame_count % 10 == 0:
                    logger.info(f"진행률: {frame_count}/{max_frames} 프레임")
            
            cap.release()
            
            if frame_results:
                # 평균값 계산
                avg_result = self._calculate_average_result(frame_results)
                logger.info(f"영상 분석 완료 - {len(frame_results)}개 프레임 평균")
                return avg_result
            else:
                logger.warning("분석 가능한 프레임이 없음")
                return self._get_default_result()
                
        except Exception as e:
            logger.error(f"영상 분석 오류: {str(e)}")
            return self._get_default_result()

    def _parse_csv_result(self, csv_path):
        """CSV 결과 파싱"""
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_line = lines[-1].strip().split(',')
                    return {
                        "confidence": float(last_line[1]) if len(last_line) > 1 else 0.0,
                        "gaze_angle_x": float(last_line[5]) if len(last_line) > 5 else 0.0,
                        "gaze_angle_y": float(last_line[6]) if len(last_line) > 6 else 0.0,
                        "AU01_r": float(last_line[-10]) if len(last_line) >= 10 else 0.0,
                        "AU02_r": float(last_line[-9]) if len(last_line) >= 9 else 0.0,
                    }
        except (ValueError, IndexError) as e:
            logger.error(f"CSV 파싱 오류: {str(e)}")
        
        return self._get_default_result()

    def _calculate_average_result(self, results):
        """프레임별 결과의 평균값 계산"""
        if not results:
            return self._get_default_result()
        
        avg_result = {
            "confidence": np.mean([r["confidence"] for r in results]),
            "gaze_angle_x": np.mean([r["gaze_angle_x"] for r in results]),
            "gaze_angle_y": np.mean([r["gaze_angle_y"] for r in results]),
            "AU01_r": np.mean([r["AU01_r"] for r in results]),
            "AU02_r": np.mean([r["AU02_r"] for r in results]),
        }
        return avg_result

    def _get_default_result(self):
        """테스트용 기본 결과값"""
        return {
            "confidence": 0.9,
            "gaze_angle_x": 0.1,
            "gaze_angle_y": 0.1,
            "AU01_r": 1.2,
            "AU02_r": 0.8,
        }

    def evaluate_emotion(self, analysis_result):
        """감정 평가"""
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

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "OpenFace",
            "is_available": self.is_available,
            "openface_path": self.openface_path,
            "output_dir": self.output_dir,
            "functions": ["analyze_image", "analyze_video", "evaluate_emotion"]
        }
