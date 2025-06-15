#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenFace 모듈 - 얼굴 표정 및 행동 분석
OpenFace 2.0을 사용한 실시간 얼굴 분석 및 감정 인식
"""
import logging
import os
import subprocess
import tempfile
import time
import csv
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

class OpenFaceModule:
    def __init__(self, openface_path: str = None):
        """
        OpenFace 모듈 초기화
        
        Args:
            openface_path: OpenFace 실행 파일 경로
        """
        self.openface_path = openface_path or self._find_openface_executable()
        self.available = False
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            self._verify_openface_installation()
            self.available = True
            logger.info(f"OpenFace 모듈 초기화 성공: {self.openface_path}")
        except Exception as e:
            logger.error(f"OpenFace 모듈 초기화 실패: {str(e)}")
            self.available = False
    
    def _find_openface_executable(self) -> str:
        """OpenFace 실행 파일 찾기"""
        possible_paths = [
            "./tools/FeatureExtraction.exe",
            "../tools/FeatureExtraction.exe",
            "FeatureExtraction.exe",
            "/usr/local/bin/FeatureExtraction",
            "/opt/OpenFace/build/bin/FeatureExtraction"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # 현재 프로젝트의 tools 디렉토리에서 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tools_path = os.path.join(os.path.dirname(current_dir), "tools", "FeatureExtraction.exe")
        if os.path.exists(tools_path):
            return tools_path
        
        raise FileNotFoundError("OpenFace FeatureExtraction 실행 파일을 찾을 수 없습니다.")
    
    def _verify_openface_installation(self):
        """OpenFace 설치 및 실행 가능 여부 확인"""
        if not os.path.exists(self.openface_path):
            raise FileNotFoundError(f"OpenFace 실행 파일이 존재하지 않습니다: {self.openface_path}")
        
        # 간단한 테스트 실행
        try:
            result = subprocess.run([self.openface_path, "-help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0 and "help" not in result.stdout.lower():
                raise RuntimeError("OpenFace 실행 파일이 정상적으로 작동하지 않습니다.")
        except subprocess.TimeoutExpired:
            # help 명령이 타임아웃되는 것은 정상일 수 있음
            pass
        except Exception as e:
            raise RuntimeError(f"OpenFace 실행 테스트 실패: {str(e)}")
    
    def is_available(self) -> bool:
        """OpenFace 모듈 사용 가능 여부 확인"""
        return self.available
    
    def analyze_video(self, video_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        비디오 파일의 얼굴 분석
        
        Args:
            video_path: 분석할 비디오 파일 경로
            output_dir: 출력 디렉토리 (None이면 임시 디렉토리 사용)
            
        Returns:
            Dict containing facial analysis results
        """
        if not self.available:
            return {"error": "OpenFace 모듈을 사용할 수 없습니다."}
        
        if not os.path.exists(video_path):
            return {"error": f"비디오 파일이 존재하지 않습니다: {video_path}"}
        
        try:
            # 출력 디렉토리 설정
            if output_dir is None:
                output_dir = os.path.join(self.temp_dir, f"analysis_{int(time.time())}")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # OpenFace 실행
            analysis_result = self._run_openface_analysis(video_path, output_dir)
            
            if analysis_result["success"]:
                # 결과 파일 파싱
                facial_data = self._parse_openface_output(output_dir)
                
                # 종합 분석 결과 생성
                summary = self._create_analysis_summary(facial_data)
                
                return {
                    "success": True,
                    "video_path": video_path,
                    "analysis_summary": summary,
                    "detailed_data": facial_data[:10],  # 처음 10프레임만 포함
                    "output_directory": output_dir,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {
                    "success": False,
                    "error": analysis_result.get("error", "OpenFace 분석 실패"),
                    "video_path": video_path
                }
                
        except Exception as e:
            logger.error(f"비디오 분석 오류: {str(e)}")
            return {"error": f"분석 중 오류 발생: {str(e)}"}
    
    def analyze_image(self, image_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        이미지 파일의 얼굴 분석
        
        Args:
            image_path: 분석할 이미지 파일 경로
            output_dir: 출력 디렉토리
            
        Returns:
            Dict containing facial analysis results
        """
        if not self.available:
            return {"error": "OpenFace 모듈을 사용할 수 없습니다."}
        
        if not os.path.exists(image_path):
            return {"error": f"이미지 파일이 존재하지 않습니다: {image_path}"}
        
        try:
            if output_dir is None:
                output_dir = os.path.join(self.temp_dir, f"image_analysis_{int(time.time())}")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # OpenFace 실행 (이미지 모드)
            analysis_result = self._run_openface_analysis(image_path, output_dir, image_mode=True)
            
            if analysis_result["success"]:
                facial_data = self._parse_openface_output(output_dir)
                summary = self._create_analysis_summary(facial_data)
                
                return {
                    "success": True,
                    "image_path": image_path,
                    "analysis_summary": summary,
                    "facial_landmarks": facial_data[0] if facial_data else {},
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {
                    "success": False,
                    "error": analysis_result.get("error", "OpenFace 이미지 분석 실패")
                }
                
        except Exception as e:
            logger.error(f"이미지 분석 오류: {str(e)}")
            return {"error": f"분석 중 오류 발생: {str(e)}"}
    
    def _run_openface_analysis(self, input_path: str, output_dir: str, image_mode: bool = False) -> Dict[str, Any]:
        """OpenFace 분석 실행"""
        try:
            # OpenFace 명령어 구성
            cmd = [
                self.openface_path,
                "-f" if not image_mode else "-fdir",
                input_path,
                "-out_dir", output_dir,
                "-aus",  # Action Units 추출
                "-pose",  # Head pose 추출
                "-gaze",  # Gaze direction 추출
                "-2Dfp",  # 2D facial landmarks
                "-3Dfp",  # 3D facial landmarks
            ]
            
            # 비디오 분석의 경우 추가 옵션
            if not image_mode:
                cmd.extend([
                    "-format_aligned",  # 정렬된 얼굴 이미지 저장
                    "-simscale", "0.7",  # 유사성 스케일
                    "-simsize", "112"    # 출력 이미지 크기
                ])
            
            logger.info(f"OpenFace 실행: {' '.join(cmd)}")
            
            # OpenFace 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                cwd=os.path.dirname(self.openface_path)
            )
            
            if result.returncode == 0:
                return {"success": True, "stdout": result.stdout}
            else:
                error_msg = result.stderr or result.stdout or "알 수 없는 오류"
                logger.error(f"OpenFace 실행 실패: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = "OpenFace 분석 시간 초과 (5분)"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"OpenFace 실행 중 오류: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _parse_openface_output(self, output_dir: str) -> List[Dict[str, Any]]:
        """OpenFace 출력 결과 파싱"""
        facial_data = []
        
        try:
            # CSV 파일 찾기
            csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
            
            if not csv_files:
                logger.warning(f"OpenFace 출력 CSV 파일을 찾을 수 없습니다: {output_dir}")
                return facial_data
            
            # 첫 번째 CSV 파일 읽기
            csv_path = os.path.join(output_dir, csv_files[0])
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    frame_data = self._extract_frame_features(row)
                    facial_data.append(frame_data)
            
            logger.info(f"OpenFace 데이터 파싱 완료: {len(facial_data)} 프레임")
            
        except Exception as e:
            logger.error(f"OpenFace 출력 파싱 오류: {str(e)}")
        
        return facial_data
    
    def _extract_frame_features(self, row: Dict[str, str]) -> Dict[str, Any]:
        """프레임별 특징 추출"""
        try:
            # 기본 정보
            frame_data = {
                "frame": int(row.get("frame", 0)),
                "timestamp": float(row.get("timestamp", 0.0)),
                "confidence": float(row.get("confidence", 0.0)),
                "success": int(row.get("success", 0)) == 1
            }
            
            # Head pose (머리 자세)
            frame_data["head_pose"] = {
                "pose_Rx": float(row.get("pose_Rx", 0.0)),
                "pose_Ry": float(row.get("pose_Ry", 0.0)),
                "pose_Rz": float(row.get("pose_Rz", 0.0))
            }
            
            # Gaze direction (시선 방향)
            frame_data["gaze"] = {
                "gaze_0_x": float(row.get("gaze_0_x", 0.0)),
                "gaze_0_y": float(row.get("gaze_0_y", 0.0)),
                "gaze_0_z": float(row.get("gaze_0_z", 0.0)),
                "gaze_1_x": float(row.get("gaze_1_x", 0.0)),
                "gaze_1_y": float(row.get("gaze_1_y", 0.0)),
                "gaze_1_z": float(row.get("gaze_1_z", 0.0))
            }
            
            # Action Units (표정 움직임)
            frame_data["action_units"] = {}
            for key, value in row.items():
                if key.startswith("AU") and "_r" in key:  # AU intensity values
                    au_name = key.replace("_r", "")
                    frame_data["action_units"][au_name] = float(value)
            
            return frame_data
            
        except Exception as e:
            logger.error(f"프레임 특징 추출 오류: {str(e)}")
            return {"frame": 0, "confidence": 0.0, "success": False}
    
    def _create_analysis_summary(self, facial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """얼굴 분석 데이터의 종합 요약 생성"""
        if not facial_data:
            return self._get_default_summary()
        
        try:
            # 성공적으로 분석된 프레임만 필터링
            valid_frames = [frame for frame in facial_data if frame.get("success", False)]
            
            if not valid_frames:
                return self._get_default_summary()
            
            # 신뢰도 계산
            confidences = [frame["confidence"] for frame in valid_frames]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            # 머리 자세 안정성 계산
            head_stability = self._calculate_head_stability(valid_frames)
            
            # 시선 안정성 계산
            gaze_stability = self._calculate_gaze_stability(valid_frames)
            
            # 감정 분석 (Action Units 기반)
            emotion_analysis = self._analyze_emotions(valid_frames)
            
            # 전반적인 행동 평가
            behavior_assessment = self._assess_behavior(valid_frames)
            
            summary = {
                "total_frames": len(facial_data),
                "valid_frames": len(valid_frames),
                "average_confidence": round(avg_confidence, 3),
                "head_stability": round(head_stability, 3),
                "gaze_stability": round(gaze_stability, 3),
                "emotion": emotion_analysis["dominant_emotion"],
                "emotion_confidence": emotion_analysis["confidence"],
                "behavior_score": behavior_assessment["score"],
                "behavior_notes": behavior_assessment["notes"],
                "facial_expression_intensity": emotion_analysis["intensity"],
                "overall_assessment": self._generate_overall_assessment(
                    avg_confidence, head_stability, gaze_stability, emotion_analysis
                )
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"분석 요약 생성 오류: {str(e)}")
            return self._get_default_summary()
    
    def _calculate_head_stability(self, frames: List[Dict[str, Any]]) -> float:
        """머리 자세 안정성 계산"""
        try:
            if len(frames) < 2:
                return 0.5
            
            # 머리 회전 각도 변화량 계산
            pose_changes = []
            for i in range(1, len(frames)):
                prev_pose = frames[i-1]["head_pose"]
                curr_pose = frames[i]["head_pose"]
                
                rx_change = abs(curr_pose["pose_Rx"] - prev_pose["pose_Rx"])
                ry_change = abs(curr_pose["pose_Ry"] - prev_pose["pose_Ry"])
                rz_change = abs(curr_pose["pose_Rz"] - prev_pose["pose_Rz"])
                
                total_change = (rx_change + ry_change + rz_change) / 3
                pose_changes.append(total_change)
            
            # 변화량의 평균을 기반으로 안정성 점수 계산
            avg_change = np.mean(pose_changes)
            stability = max(0.0, min(1.0, 1.0 - (avg_change / 30.0)))  # 30도 이상 변경시 불안정
            
            return stability
            
        except Exception as e:
            logger.error(f"머리 안정성 계산 오류: {str(e)}")
            return 0.5
    
    def _calculate_gaze_stability(self, frames: List[Dict[str, Any]]) -> float:
        """시선 안정성 계산"""
        try:
            if len(frames) < 2:
                return 0.5
            
            # 시선 방향 변화량 계산
            gaze_changes = []
            for i in range(1, len(frames)):
                prev_gaze = frames[i-1]["gaze"]
                curr_gaze = frames[i]["gaze"]
                
                # 양쪽 눈의 시선 변화 평균
                left_change = np.sqrt(
                    (curr_gaze["gaze_0_x"] - prev_gaze["gaze_0_x"])**2 +
                    (curr_gaze["gaze_0_y"] - prev_gaze["gaze_0_y"])**2 +
                    (curr_gaze["gaze_0_z"] - prev_gaze["gaze_0_z"])**2
                )
                
                right_change = np.sqrt(
                    (curr_gaze["gaze_1_x"] - prev_gaze["gaze_1_x"])**2 +
                    (curr_gaze["gaze_1_y"] - prev_gaze["gaze_1_y"])**2 +
                    (curr_gaze["gaze_1_z"] - prev_gaze["gaze_1_z"])**2
                )
                
                avg_change = (left_change + right_change) / 2
                gaze_changes.append(avg_change)
            
            # 안정성 점수 계산
            avg_change = np.mean(gaze_changes)
            stability = max(0.0, min(1.0, 1.0 - (avg_change / 0.5)))  # 0.5 단위 이상 변경시 불안정
            
            return stability
            
        except Exception as e:
            logger.error(f"시선 안정성 계산 오류: {str(e)}")
            return 0.5
    
    def _analyze_emotions(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Action Units 기반 감정 분석"""
        try:
            if not frames:
                return {"dominant_emotion": "중립", "confidence": 0.5, "intensity": 0.3}
            
            # Action Units 평균값 계산
            au_averages = {}
            for frame in frames:
                action_units = frame.get("action_units", {})
                for au, value in action_units.items():
                    if au not in au_averages:
                        au_averages[au] = []
                    au_averages[au].append(value)
            
            # 각 AU의 평균 계산
            au_means = {}
            for au, values in au_averages.items():
                au_means[au] = np.mean(values)
            
            # 감정 매핑 (간단한 버전)
            emotion_scores = {
                "기쁨": self._calculate_joy_score(au_means),
                "슬픔": self._calculate_sadness_score(au_means),
                "화남": self._calculate_anger_score(au_means),
                "놀람": self._calculate_surprise_score(au_means),
                "중립": self._calculate_neutral_score(au_means)
            }
            
            # 가장 높은 점수의 감정 선택
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant_emotion]
            
            # 전체적인 표정 강도 계산
            intensity = np.mean(list(au_means.values())) / 5.0 if au_means else 0.3
            
            return {
                "dominant_emotion": dominant_emotion,
                "confidence": round(confidence, 3),
                "intensity": round(min(1.0, intensity), 3),
                "emotion_scores": emotion_scores
            }
            
        except Exception as e:
            logger.error(f"감정 분석 오류: {str(e)}")
            return {"dominant_emotion": "중립", "confidence": 0.5, "intensity": 0.3}
    
    def _calculate_joy_score(self, au_means: Dict[str, float]) -> float:
        """기쁨 점수 계산"""
        # AU6 (볼 올리기), AU12 (입꼬리 올리기) 등을 기반으로 계산
        joy_aus = ["AU06", "AU12", "AU25"]
        score = 0.0
        count = 0
        
        for au in joy_aus:
            if au in au_means:
                score += au_means[au] / 5.0  # 0-1 범위로 정규화
                count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_sadness_score(self, au_means: Dict[str, float]) -> float:
        """슬픔 점수 계산"""
        # AU1 (눈썹 안쪽 올리기), AU4 (눈썹 내리기), AU15 (입꼬리 내리기) 등
        sadness_aus = ["AU01", "AU04", "AU15"]
        score = 0.0
        count = 0
        
        for au in sadness_aus:
            if au in au_means:
                score += au_means[au] / 5.0
                count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_anger_score(self, au_means: Dict[str, float]) -> float:
        """화남 점수 계산"""
        # AU4 (눈썹 내리기), AU5 (위 눈꺼풀 올리기), AU7 (아래 눈꺼풀 올리기) 등
        anger_aus = ["AU04", "AU05", "AU07", "AU23"]
        score = 0.0
        count = 0
        
        for au in anger_aus:
            if au in au_means:
                score += au_means[au] / 5.0
                count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_surprise_score(self, au_means: Dict[str, float]) -> float:
        """놀람 점수 계산"""
        # AU1+2 (눈썹 올리기), AU5 (위 눈꺼풀 올리기), AU26 (입 벌리기) 등
        surprise_aus = ["AU01", "AU02", "AU05", "AU26"]
        score = 0.0
        count = 0
        
        for au in surprise_aus:
            if au in au_means:
                score += au_means[au] / 5.0
                count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_neutral_score(self, au_means: Dict[str, float]) -> float:
        """중립 점수 계산 (다른 감정이 낮을 때 높음)"""
        if not au_means:
            return 0.8
        
        # 전체 AU 활성도가 낮으면 중립적
        total_intensity = sum(au_means.values()) / len(au_means)
        neutral_score = max(0.0, 1.0 - (total_intensity / 3.0))
        
        return min(1.0, neutral_score + 0.3)  # 기본 중립 점수 추가
    
    def _assess_behavior(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """전반적인 행동 평가"""
        try:
            if not frames:
                return {"score": 0.5, "notes": ["분석 데이터 부족"]}
            
            # 신뢰도 기반 점수
            avg_confidence = np.mean([f["confidence"] for f in frames])
            confidence_score = min(1.0, avg_confidence)
            
            # 안정성 점수들 가중 평균
            head_stability = self._calculate_head_stability(frames)
            gaze_stability = self._calculate_gaze_stability(frames)
            
            # 종합 점수 계산
            behavior_score = (confidence_score * 0.4 + head_stability * 0.3 + gaze_stability * 0.3)
            
            # 평가 노트 생성
            notes = []
            if confidence_score > 0.8:
                notes.append("높은 얼굴 인식 신뢰도")
            elif confidence_score < 0.5:
                notes.append("얼굴 인식 품질 개선 필요")
            
            if head_stability > 0.7:
                notes.append("안정적인 자세 유지")
            elif head_stability < 0.4:
                notes.append("머리 움직임이 많음")
            
            if gaze_stability > 0.7:
                notes.append("일정한 시선 방향")
            elif gaze_stability < 0.4:
                notes.append("시선 움직임이 산만함")
            
            if not notes:
                notes.append("보통 수준의 행동 패턴")
            
            return {
                "score": round(behavior_score, 3),
                "notes": notes
            }
            
        except Exception as e:
            logger.error(f"행동 평가 오류: {str(e)}")
            return {"score": 0.5, "notes": ["평가 중 오류 발생"]}
    
    def _generate_overall_assessment(self, confidence: float, head_stability: float, 
                                   gaze_stability: float, emotion_analysis: Dict) -> str:
        """전반적인 평가 텍스트 생성"""
        try:
            assessment_parts = []
            
            # 신뢰도 평가
            if confidence > 0.8:
                assessment_parts.append("얼굴 인식이 명확하게 이루어졌습니다")
            elif confidence > 0.6:
                assessment_parts.append("적절한 얼굴 인식 품질을 보였습니다")
            else:
                assessment_parts.append("얼굴 인식 품질 개선이 필요합니다")
            
            # 안정성 평가
            stability_avg = (head_stability + gaze_stability) / 2
            if stability_avg > 0.7:
                assessment_parts.append("안정적인 자세와 시선을 유지했습니다")
            elif stability_avg > 0.5:
                assessment_parts.append("보통 수준의 자세 안정성을 보였습니다")
            else:
                assessment_parts.append("자세와 시선의 안정성 개선이 필요합니다")
            
            # 감정 평가
            emotion = emotion_analysis.get("dominant_emotion", "중립")
            emotion_confidence = emotion_analysis.get("confidence", 0.5)
            
            if emotion_confidence > 0.6:
                assessment_parts.append(f"주로 {emotion}적인 표정을 보였습니다")
            else:
                assessment_parts.append("다양한 표정 변화를 보였습니다")
            
            return ". ".join(assessment_parts) + "."
            
        except Exception as e:
            logger.error(f"전체 평가 생성 오류: {str(e)}")
            return "전반적으로 무난한 얼굴 분석 결과를 보였습니다."
    
    def _get_default_summary(self) -> Dict[str, Any]:
        """기본 분석 요약 반환"""
        return {
            "total_frames": 0,
            "valid_frames": 0,
            "average_confidence": 0.5,
            "head_stability": 0.5,
            "gaze_stability": 0.5,
            "emotion": "중립",
            "emotion_confidence": 0.5,
            "behavior_score": 0.5,
            "behavior_notes": ["분석 데이터 없음"],
            "facial_expression_intensity": 0.3,
            "overall_assessment": "얼굴 분석을 수행할 수 없었습니다."
        }
    
    def cleanup(self):
        """임시 파일 정리"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("OpenFace 임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 오류: {str(e)}")

# 편의를 위한 함수들
def create_openface_module(openface_path: str = None) -> OpenFaceModule:
    """OpenFace 모듈 생성 팩토리 함수"""
    return OpenFaceModule(openface_path)

def is_openface_available() -> bool:
    """OpenFace 모듈 사용 가능 여부 확인"""
    try:
        test_module = OpenFaceModule()
        return test_module.is_available()
    except Exception:
        return False
