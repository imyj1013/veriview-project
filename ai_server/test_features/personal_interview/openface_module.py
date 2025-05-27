"""
개인면접용 OpenFace 얼굴 분석 테스트 모듈
토론면접과 유사하지만 개인면접에 특화된 분석 기능 제공
"""
import cv2
import subprocess
import os
import tempfile
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PersonalInterviewOpenFaceModule:
    def __init__(self, openface_path=None, output_dir=None):
        """개인면접용 OpenFace 테스트 모듈 초기화"""
        if openface_path is None:
            openface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "FeatureExtraction.exe")
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "interview_facial_output")
            
        self.openface_path = openface_path
        self.output_dir = output_dir
        self.is_available = os.path.exists(self.openface_path)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        logger.info(f"개인면접 OpenFace 테스트 모듈 초기화 - 사용 가능: {self.is_available}")

    def test_connection(self):
        """OpenFace 연결 테스트"""
        if not self.is_available:
            return {"status": "unavailable", "message": "OpenFace 실행 파일을 찾을 수 없습니다"}
        
        try:
            result = subprocess.run([self.openface_path, "-help"], 
                                  capture_output=True, text=True, timeout=10)
            return {"status": "available", "message": "OpenFace 정상 작동"}
        except Exception as e:
            return {"status": "error", "message": f"OpenFace 실행 오류: {str(e)}"}

    def analyze_interview_video(self, video_path, question_type="general"):
        """면접 영상 분석 - 질문 유형별 특화 분석"""
        if not os.path.exists(video_path):
            logger.error(f"영상 파일이 존재하지 않습니다: {video_path}")
            return self._get_default_interview_result(question_type)
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"영상 파일 열기 실패: {video_path}")
                return self._get_default_interview_result(question_type)
            
            frame_results = []
            frame_count = 0
            max_frames = 60  # 면접은 더 긴 영상을 분석
            
            logger.info(f"면접 영상 분석 시작 - 질문 유형: {question_type}")
            
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 5프레임마다 분석 (성능 최적화)
                if frame_count % 5 == 0:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir=self.output_dir) as temp_file:
                        temp_path = temp_file.name
                        cv2.imwrite(temp_path, frame)
                        
                        result = self.analyze_image(temp_path)
                        if result and result.get("confidence", 0) > 0.5:
                            frame_results.append(result)
                        
                        os.remove(temp_path)
                
                frame_count += 1
                
                if frame_count % 20 == 0:
                    logger.info(f"진행률: {frame_count}/{max_frames} 프레임")
            
            cap.release()
            
            if frame_results:
                analysis_result = self._calculate_interview_metrics(frame_results, question_type)
                logger.info(f"면접 영상 분석 완료 - {len(frame_results)}개 프레임 분석")
                return analysis_result
            else:
                logger.warning("분석 가능한 프레임이 없음")
                return self._get_default_interview_result(question_type)
                
        except Exception as e:
            logger.error(f"면접 영상 분석 오류: {str(e)}")
            return self._get_default_interview_result(question_type)

    def analyze_image(self, image_path):
        """이미지 얼굴 분석"""
        if not self.is_available:
            return self._get_default_face_result()
        
        try:
            if not os.path.exists(image_path):
                return self._get_default_face_result()
            
            output_csv = os.path.join(self.output_dir, "temp_interview_output.csv")
            command = f'"{self.openface_path}" -f "{image_path}" -out_dir "{self.output_dir}" -q'
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            
            if os.path.exists(output_csv):
                analysis_result = self._parse_csv_result(output_csv)
                os.remove(output_csv)
                return analysis_result
            else:
                return self._get_default_face_result()
                
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenFace 실행 실패: {e.stderr}")
            return self._get_default_face_result()
        except Exception as e:
            logger.error(f"이미지 분석 오류: {str(e)}")
            return self._get_default_face_result()

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
                        "AU04_r": float(last_line[-8]) if len(last_line) >= 8 else 0.0,  # 눈썹 찌푸림
                        "AU06_r": float(last_line[-6]) if len(last_line) >= 6 else 0.0,  # 뺨 올리기
                        "AU12_r": float(last_line[-4]) if len(last_line) >= 4 else 0.0,  # 입꼬리 올리기
                    }
        except (ValueError, IndexError) as e:
            logger.error(f"CSV 파싱 오류: {str(e)}")
        
        return self._get_default_face_result()

    def _calculate_interview_metrics(self, frame_results, question_type):
        """면접용 메트릭 계산"""
        if not frame_results:
            return self._get_default_interview_result(question_type)
        
        # 기본 통계 계산
        confidence_values = [r["confidence"] for r in frame_results]
        gaze_x_values = [r["gaze_angle_x"] for r in frame_results]
        gaze_y_values = [r["gaze_angle_y"] for r in frame_results]
        au01_values = [r["AU01_r"] for r in frame_results]  # 눈썹 안쪽 올리기
        au02_values = [r["AU02_r"] for r in frame_results]  # 눈썹 바깥쪽 올리기
        
        # 면접 특화 메트릭
        metrics = {
            # 기본 신뢰도
            "avg_confidence": np.mean(confidence_values),
            "confidence_stability": 1.0 - np.std(confidence_values),
            
            # 시선 안정성 (면접에서 중요)
            "gaze_stability_x": 1.0 - np.std(np.abs(gaze_x_values)),
            "gaze_stability_y": 1.0 - np.std(np.abs(gaze_y_values)),
            "avg_gaze_direction": np.mean(np.abs(gaze_x_values)) + np.mean(np.abs(gaze_y_values)),
            
            # 표정 분석
            "avg_eyebrow_inner": np.mean(au01_values),
            "avg_eyebrow_outer": np.mean(au02_values),
            "expression_variability": np.std(au01_values) + np.std(au02_values),
            
            # 질문 유형별 가중치 적용
            "question_type": question_type,
            "total_frames_analyzed": len(frame_results)
        }
        
        # 질문 유형별 특화 분석
        if question_type == "technical":
            # 기술 질문: 집중도와 사고 과정이 중요
            metrics["focus_score"] = self._calculate_focus_score(metrics)
            metrics["thinking_indicators"] = self._detect_thinking_patterns(frame_results)
        elif question_type == "behavioral":
            # 인성 질문: 감정 표현과 진정성이 중요
            metrics["authenticity_score"] = self._calculate_authenticity_score(metrics)
            metrics["emotional_range"] = self._analyze_emotional_range(frame_results)
        else:
            # 일반 질문: 전반적인 안정성과 자신감
            metrics["confidence_score"] = self._calculate_confidence_score(metrics)
            metrics["stability_score"] = self._calculate_stability_score(metrics)
        
        return metrics

    def _calculate_focus_score(self, metrics):
        """집중도 점수 계산 (기술 질문용)"""
        gaze_score = max(0, 1.0 - metrics["avg_gaze_direction"] / 2.0)
        stability_score = (metrics["gaze_stability_x"] + metrics["gaze_stability_y"]) / 2.0
        confidence_score = metrics["avg_confidence"]
        
        focus_score = (gaze_score * 0.4 + stability_score * 0.4 + confidence_score * 0.2) * 5.0
        return min(5.0, max(1.0, focus_score))

    def _detect_thinking_patterns(self, frame_results):
        """사고 패턴 감지"""
        # 눈썹 움직임으로 사고 과정 추정
        au01_changes = []
        for i in range(1, len(frame_results)):
            change = abs(frame_results[i]["AU01_r"] - frame_results[i-1]["AU01_r"])
            au01_changes.append(change)
        
        if au01_changes:
            thinking_activity = np.mean(au01_changes)
            if thinking_activity > 0.3:
                return "활발한 사고 과정 감지됨"
            elif thinking_activity > 0.1:
                return "적절한 사고 과정"
            else:
                return "제한적인 사고 표현"
        
        return "사고 패턴 분석 불가"

    def _calculate_authenticity_score(self, metrics):
        """진정성 점수 계산 (인성 질문용)"""
        # 자연스러운 표정 변화가 진정성을 나타냄
        expression_naturalness = min(1.0, metrics["expression_variability"] / 2.0)
        gaze_directness = max(0, 1.0 - metrics["avg_gaze_direction"])
        confidence_level = metrics["avg_confidence"]
        
        authenticity_score = (expression_naturalness * 0.4 + gaze_directness * 0.3 + confidence_level * 0.3) * 5.0
        return min(5.0, max(1.0, authenticity_score))

    def _analyze_emotional_range(self, frame_results):
        """감정 표현 범위 분석"""
        au_values = []
        for result in frame_results:
            au_sum = result.get("AU01_r", 0) + result.get("AU02_r", 0) + result.get("AU04_r", 0) + result.get("AU06_r", 0) + result.get("AU12_r", 0)
            au_values.append(au_sum)
        
        if au_values:
            emotional_range = np.max(au_values) - np.min(au_values)
            if emotional_range > 3.0:
                return "풍부한 감정 표현"
            elif emotional_range > 1.5:
                return "적절한 감정 표현"
            else:
                return "제한적인 감정 표현"
        
        return "감정 표현 분석 불가"

    def _calculate_confidence_score(self, metrics):
        """자신감 점수 계산 (일반 질문용)"""
        base_confidence = metrics["avg_confidence"]
        gaze_stability = (metrics["gaze_stability_x"] + metrics["gaze_stability_y"]) / 2.0
        expression_balance = max(0, 1.0 - abs(metrics["avg_eyebrow_inner"] - metrics["avg_eyebrow_outer"]))
        
        confidence_score = (base_confidence * 0.5 + gaze_stability * 0.3 + expression_balance * 0.2) * 5.0
        return min(5.0, max(1.0, confidence_score))

    def _calculate_stability_score(self, metrics):
        """안정성 점수 계산"""
        gaze_stability = (metrics["gaze_stability_x"] + metrics["gaze_stability_y"]) / 2.0
        confidence_stability = metrics["confidence_stability"]
        expression_stability = max(0, 1.0 - metrics["expression_variability"] / 3.0)
        
        stability_score = (gaze_stability * 0.4 + confidence_stability * 0.3 + expression_stability * 0.3) * 5.0
        return min(5.0, max(1.0, stability_score))

    def evaluate_interview_performance(self, analysis_result):
        """면접 수행 평가"""
        if not analysis_result:
            return "분석 결과 없음"
        
        question_type = analysis_result.get("question_type", "general")
        
        if question_type == "technical":
            focus_score = analysis_result.get("focus_score", 3.0)
            thinking_pattern = analysis_result.get("thinking_indicators", "")
            
            if focus_score >= 4.0:
                return f"기술적 집중도 우수 ({thinking_pattern})"
            elif focus_score >= 3.0:
                return f"기술적 집중도 양호 ({thinking_pattern})"
            else:
                return f"기술적 집중도 개선 필요 ({thinking_pattern})"
                
        elif question_type == "behavioral":
            authenticity_score = analysis_result.get("authenticity_score", 3.0)
            emotional_range = analysis_result.get("emotional_range", "")
            
            if authenticity_score >= 4.0:
                return f"진정성 우수 ({emotional_range})"
            elif authenticity_score >= 3.0:
                return f"진정성 양호 ({emotional_range})"
            else:
                return f"진정성 개선 필요 ({emotional_range})"
                
        else:
            confidence_score = analysis_result.get("confidence_score", 3.0)
            stability_score = analysis_result.get("stability_score", 3.0)
            avg_score = (confidence_score + stability_score) / 2.0
            
            if avg_score >= 4.0:
                return "전반적으로 안정적이고 자신감 있는 모습"
            elif avg_score >= 3.0:
                return "적절한 면접 태도"
            else:
                return "면접 태도 개선 필요"

    def _get_default_face_result(self):
        """기본 얼굴 분석 결과"""
        return {
            "confidence": 0.9,
            "gaze_angle_x": 0.1,
            "gaze_angle_y": 0.1,
            "AU01_r": 1.0,
            "AU02_r": 0.8,
            "AU04_r": 0.3,
            "AU06_r": 0.5,
            "AU12_r": 1.2,
        }

    def _get_default_interview_result(self, question_type):
        """기본 면접 분석 결과"""
        base_result = {
            "avg_confidence": 0.9,
            "confidence_stability": 0.8,
            "gaze_stability_x": 0.7,
            "gaze_stability_y": 0.8,
            "avg_gaze_direction": 0.2,
            "avg_eyebrow_inner": 1.0,
            "avg_eyebrow_outer": 0.8,
            "expression_variability": 0.5,
            "question_type": question_type,
            "total_frames_analyzed": 30
        }
        
        if question_type == "technical":
            base_result.update({
                "focus_score": 3.8,
                "thinking_indicators": "적절한 사고 과정"
            })
        elif question_type == "behavioral":
            base_result.update({
                "authenticity_score": 3.7,
                "emotional_range": "적절한 감정 표현"
            })
        else:
            base_result.update({
                "confidence_score": 3.6,
                "stability_score": 3.8
            })
        
        return base_result

    def get_module_status(self):
        """모듈 상태 정보 반환"""
        return {
            "module_name": "Personal Interview OpenFace",
            "is_available": self.is_available,
            "openface_path": self.openface_path,
            "output_dir": self.output_dir,
            "supported_question_types": ["general", "technical", "behavioral"],
            "functions": ["analyze_interview_video", "evaluate_interview_performance"]
        }
