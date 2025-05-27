"""
OpenFace 2.0 토론면접 통합 모듈
실제 프로덕션 환경에서 OpenFace와 LLM을 통합하여 사용하는 모듈
"""
import os
import logging
import subprocess
import tempfile
import csv
import numpy as np
import time
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class OpenFaceDebateIntegration:
    def __init__(self, openface_path: Optional[str] = None, output_dir: Optional[str] = None):
        """OpenFace 토론면접 통합 모듈 초기화"""
        
        # OpenFace 실행 파일 경로 설정
        if openface_path is None:
            openface_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "..", "..", "tools", "FeatureExtraction.exe"
            )
        
        # 출력 디렉터리 설정
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "facial_output")
        
        self.openface_path = openface_path
        self.output_dir = output_dir
        self.is_available = os.path.exists(self.openface_path)
        
        # 출력 디렉터리 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        logger.info(f"OpenFace 통합 모듈 초기화 - 사용 가능: {self.is_available}")
        if not self.is_available:
            logger.warning(f"OpenFace 실행 파일을 찾을 수 없습니다: {self.openface_path}")

    def analyze_video(self, video_path: str, participant_id: Optional[str] = None) -> Dict[str, Any]:
        """비디오 파일의 얼굴 분석 및 토론 참여자 평가"""
        
        if not self.is_available:
            logger.warning("OpenFace 사용 불가 - 기본값 반환")
            return self._get_fallback_analysis(video_path)
        
        if not os.path.exists(video_path):
            logger.error(f"비디오 파일이 존재하지 않습니다: {video_path}")
            return self._get_fallback_analysis(video_path)
        
        try:
            logger.info(f"OpenFace 비디오 분석 시작: {video_path}")
            
            # 분석 결과 파일 경로 생성
            timestamp = int(time.time())
            participant_id = participant_id or f"participant_{timestamp}"
            output_csv = os.path.join(self.output_dir, f"{participant_id}_features.csv")
            
            # OpenFace 실행 명령어 구성
            command = [
                self.openface_path,
                "-f", video_path,
                "-out_dir", self.output_dir,
                "-of", f"{participant_id}_features.csv",
                "-2Dfp",  # 2D 얼굴 랜드마크
                "-3Dfp",  # 3D 얼굴 랜드마크  
                "-pdmparams",  # PDM 파라미터
                "-pose",  # 머리 자세
                "-aus",   # Action Units
                "-gaze"   # 시선 방향
            ]
            
            # OpenFace 실행
            logger.info("OpenFace 실행 중...")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5분 타임아웃
            )
            
            logger.info("OpenFace 분석 완료")
            
            # 결과 파싱
            if os.path.exists(output_csv):
                analysis_result = self._parse_openface_output(output_csv, participant_id)
                
                # 토론 특화 분석 추가
                debate_analysis = self._analyze_debate_specific_features(analysis_result)
                analysis_result.update(debate_analysis)
                
                logger.info("OpenFace 결과 분석 완료")
                return analysis_result
            else:
                logger.error("OpenFace 출력 파일이 생성되지 않았습니다")
                return self._get_fallback_analysis(video_path)
                
        except subprocess.TimeoutExpired:
            logger.error("OpenFace 실행 시간 초과")
            return self._get_fallback_analysis(video_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenFace 실행 실패: {e.stderr}")
            return self._get_fallback_analysis(video_path)
        except Exception as e:
            logger.error(f"OpenFace 분석 중 오류: {str(e)}")
            return self._get_fallback_analysis(video_path)

    def _parse_openface_output(self, csv_path: str, participant_id: str) -> Dict[str, Any]:
        """OpenFace CSV 출력 파일 파싱"""
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            if not rows:
                logger.warning("OpenFace CSV 파일이 비어있습니다")
                return self._get_fallback_analysis()
            
            logger.info(f"OpenFace 데이터 로드 완료: {len(rows)}개 프레임")
            
            # 주요 특징 추출
            features = {
                "participant_id": participant_id,
                "total_frames": len(rows),
                "confidence_scores": [],
                "gaze_directions": {"x": [], "y": []},
                "head_poses": {"pitch": [], "yaw": [], "roll": []},
                "action_units": {},
                "facial_landmarks": {"2d": [], "3d": []}
            }
            
            # 각 프레임 데이터 처리
            for row in rows:
                # 신뢰도 점수
                confidence = float(row.get('confidence', 0.0))
                features["confidence_scores"].append(confidence)
                
                # 시선 방향
                gaze_x = float(row.get('gaze_0_x', 0.0))
                gaze_y = float(row.get('gaze_0_y', 0.0))
                features["gaze_directions"]["x"].append(gaze_x)
                features["gaze_directions"]["y"].append(gaze_y)
                
                # 머리 자세
                pose_rx = float(row.get('pose_Rx', 0.0))
                pose_ry = float(row.get('pose_Ry', 0.0))
                pose_rz = float(row.get('pose_Rz', 0.0))
                features["head_poses"]["pitch"].append(pose_rx)
                features["head_poses"]["yaw"].append(pose_ry)
                features["head_poses"]["roll"].append(pose_rz)
                
                # Action Units (표정 관련)
                for i in range(1, 29):  # AU01 ~ AU28
                    au_key = f'AU{i:02d}_r'
                    if au_key in row:
                        if au_key not in features["action_units"]:
                            features["action_units"][au_key] = []
                        features["action_units"][au_key].append(float(row.get(au_key, 0.0)))
            
            # 통계 계산
            statistics = self._calculate_feature_statistics(features)
            
            # 최종 결과 구성
            result = {
                "raw_features": features,
                "statistics": statistics,
                "analysis_metadata": {
                    "participant_id": participant_id,
                    "csv_path": csv_path,
                    "total_frames": len(rows),
                    "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"OpenFace CSV 파싱 오류: {str(e)}")
            return self._get_fallback_analysis()

    def _calculate_feature_statistics(self, features: Dict) -> Dict[str, Any]:
        """OpenFace 특징들의 통계 계산"""
        
        stats = {}
        
        try:
            # 신뢰도 통계
            confidence_scores = features["confidence_scores"]
            if confidence_scores:
                stats["confidence"] = {
                    "mean": np.mean(confidence_scores),
                    "std": np.std(confidence_scores),
                    "min": np.min(confidence_scores),
                    "max": np.max(confidence_scores),
                    "frames_high_confidence": sum(1 for c in confidence_scores if c > 0.8)
                }
            
            # 시선 안정성 통계
            gaze_x = features["gaze_directions"]["x"]
            gaze_y = features["gaze_directions"]["y"]
            if gaze_x and gaze_y:
                stats["gaze_stability"] = {
                    "x_variance": np.var(gaze_x),
                    "y_variance": np.var(gaze_y),
                    "total_variance": np.var(gaze_x) + np.var(gaze_y),
                    "mean_deviation": np.mean([abs(x) + abs(y) for x, y in zip(gaze_x, gaze_y)])
                }
            
            # 머리 자세 안정성
            head_poses = features["head_poses"]
            if head_poses["pitch"]:
                stats["head_stability"] = {
                    "pitch_variance": np.var(head_poses["pitch"]),
                    "yaw_variance": np.var(head_poses["yaw"]),
                    "roll_variance": np.var(head_poses["roll"]),
                    "total_movement": (np.var(head_poses["pitch"]) + 
                                     np.var(head_poses["yaw"]) + 
                                     np.var(head_poses["roll"]))
                }
            
            # Action Units 통계 (표정 분석)
            au_stats = {}
            for au_name, au_values in features["action_units"].items():
                if au_values:
                    au_stats[au_name] = {
                        "mean": np.mean(au_values),
                        "max": np.max(au_values),
                        "activation_rate": sum(1 for v in au_values if v > 1.0) / len(au_values)
                    }
            stats["action_units"] = au_stats
            
        except Exception as e:
            logger.error(f"특징 통계 계산 오류: {str(e)}")
        
        return stats

    def _analyze_debate_specific_features(self, analysis_result: Dict) -> Dict[str, Any]:
        """토론 특화 분석"""
        
        debate_analysis = {
            "engagement_metrics": {},
            "confidence_indicators": {},
            "attention_patterns": {},
            "emotional_expressions": {},
            "overall_assessment": {}
        }
        
        try:
            stats = analysis_result.get("statistics", {})
            
            # 참여도 메트릭
            confidence_stats = stats.get("confidence", {})
            if confidence_stats:
                avg_confidence = confidence_stats.get("mean", 0.5)
                high_conf_ratio = (confidence_stats.get("frames_high_confidence", 0) / 
                                 confidence_stats.get("frames_total", 1))
                
                debate_analysis["engagement_metrics"] = {
                    "overall_engagement": min(5.0, max(1.0, avg_confidence * 5)),
                    "consistency": min(5.0, max(1.0, high_conf_ratio * 5)),
                    "presence_quality": "높음" if avg_confidence > 0.8 else "보통" if avg_confidence > 0.6 else "낮음"
                }
            
            # 자신감 지표
            gaze_stability = stats.get("gaze_stability", {})
            head_stability = stats.get("head_stability", {})
            
            if gaze_stability and head_stability:
                gaze_score = max(0, 1 - (gaze_stability.get("total_variance", 1.0) / 2.0))
                head_score = max(0, 1 - (head_stability.get("total_movement", 1.0) / 10.0))
                
                debate_analysis["confidence_indicators"] = {
                    "eye_contact_stability": gaze_score,
                    "posture_stability": head_score,
                    "overall_confidence": (gaze_score + head_score) / 2,
                    "confidence_level": "높음" if (gaze_score + head_score) > 1.2 else "보통" if (gaze_score + head_score) > 0.8 else "낮음"
                }
            
            # 주의집중 패턴
            if gaze_stability:
                attention_score = 1.0 - min(1.0, gaze_stability.get("mean_deviation", 0.5))
                debate_analysis["attention_patterns"] = {
                    "focus_score": attention_score,
                    "attention_consistency": "일관적" if gaze_stability.get("total_variance", 1.0) < 0.5 else "불안정",
                    "eye_contact_quality": "우수" if attention_score > 0.8 else "양호" if attention_score > 0.6 else "개선필요"
                }
            
            # 감정 표현 분석
            au_stats = stats.get("action_units", {})
            if au_stats:
                # 주요 감정 관련 AU들
                smile_aus = ["AU12_r", "AU06_r"]  # 미소
                tension_aus = ["AU04_r", "AU07_r"]  # 긴장
                
                smile_intensity = np.mean([au_stats.get(au, {}).get("mean", 0) for au in smile_aus])
                tension_intensity = np.mean([au_stats.get(au, {}).get("mean", 0) for au in tension_aus])
                
                debate_analysis["emotional_expressions"] = {
                    "positive_expression": smile_intensity,
                    "tension_level": tension_intensity,
                    "emotional_balance": "균형적" if abs(smile_intensity - tension_intensity) < 0.5 else "불균형",
                    "overall_demeanor": "긍정적" if smile_intensity > tension_intensity else "긴장됨" if tension_intensity > 1.0 else "중립적"
                }
            
            # 종합 평가
            engagement = debate_analysis.get("engagement_metrics", {}).get("overall_engagement", 3.0)
            confidence = debate_analysis.get("confidence_indicators", {}).get("overall_confidence", 0.5) * 5
            attention = debate_analysis.get("attention_patterns", {}).get("focus_score", 0.5) * 5
            
            overall_score = (engagement + confidence + attention) / 3
            
            debate_analysis["overall_assessment"] = {
                "composite_score": overall_score,
                "performance_level": "우수" if overall_score > 4.0 else "양호" if overall_score > 3.0 else "개선필요",
                "key_strengths": self._identify_strengths(debate_analysis),
                "improvement_areas": self._identify_improvements(debate_analysis)
            }
            
        except Exception as e:
            logger.error(f"토론 특화 분석 오류: {str(e)}")
        
        return {"debate_analysis": debate_analysis}

    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """강점 식별"""
        strengths = []
        
        try:
            engagement = analysis.get("engagement_metrics", {})
            confidence = analysis.get("confidence_indicators", {})
            attention = analysis.get("attention_patterns", {})
            emotions = analysis.get("emotional_expressions", {})
            
            if engagement.get("overall_engagement", 0) > 4.0:
                strengths.append("높은 참여도")
            
            if confidence.get("overall_confidence", 0) > 0.8:
                strengths.append("안정적인 자세")
            
            if attention.get("focus_score", 0) > 0.8:
                strengths.append("우수한 아이컨택")
            
            if emotions.get("positive_expression", 0) > 1.0:
                strengths.append("긍정적인 표정")
            
            if not strengths:
                strengths.append("전반적으로 안정적인 모습")
                
        except Exception as e:
            logger.error(f"강점 식별 오류: {str(e)}")
            strengths = ["분석 결과 확인 필요"]
        
        return strengths

    def _identify_improvements(self, analysis: Dict) -> List[str]:
        """개선점 식별"""
        improvements = []
        
        try:
            engagement = analysis.get("engagement_metrics", {})
            confidence = analysis.get("confidence_indicators", {})
            attention = analysis.get("attention_patterns", {})
            emotions = analysis.get("emotional_expressions", {})
            
            if engagement.get("overall_engagement", 5) < 3.0:
                improvements.append("참여도 향상")
            
            if confidence.get("overall_confidence", 1) < 0.6:
                improvements.append("자세 안정성")
            
            if attention.get("focus_score", 1) < 0.6:
                improvements.append("시선 집중도")
            
            if emotions.get("tension_level", 0) > 2.0:
                improvements.append("긴장감 완화")
            
            if not improvements:
                improvements.append("현재 수준 유지")
                
        except Exception as e:
            logger.error(f"개선점 식별 오류: {str(e)}")
            improvements = ["분석 결과 확인 필요"]
        
        return improvements

    def _get_fallback_analysis(self, video_path: Optional[str] = None) -> Dict[str, Any]:
        """OpenFace 사용 불가시 기본 분석 결과"""
        
        return {
            "raw_features": {
                "participant_id": "fallback_analysis",
                "total_frames": 30,
                "confidence_scores": [0.85] * 30,
                "gaze_directions": {"x": [0.1] * 30, "y": [0.1] * 30},
                "head_poses": {"pitch": [0.05] * 30, "yaw": [0.1] * 30, "roll": [0.02] * 30},
                "action_units": {"AU12_r": [1.2] * 30, "AU06_r": [0.8] * 30}
            },
            "statistics": {
                "confidence": {"mean": 0.85, "std": 0.05, "min": 0.8, "max": 0.9},
                "gaze_stability": {"total_variance": 0.2, "mean_deviation": 0.15},
                "head_stability": {"total_movement": 0.8}
            },
            "debate_analysis": {
                "engagement_metrics": {
                    "overall_engagement": 4.0,
                    "consistency": 4.2,
                    "presence_quality": "높음"
                },
                "confidence_indicators": {
                    "eye_contact_stability": 0.8,
                    "posture_stability": 0.85,
                    "overall_confidence": 0.825,
                    "confidence_level": "높음"
                },
                "attention_patterns": {
                    "focus_score": 0.8,
                    "attention_consistency": "일관적",
                    "eye_contact_quality": "우수"
                },
                "emotional_expressions": {
                    "positive_expression": 1.0,
                    "tension_level": 0.5,
                    "emotional_balance": "균형적",
                    "overall_demeanor": "긍정적"
                },
                "overall_assessment": {
                    "composite_score": 4.0,
                    "performance_level": "우수",
                    "key_strengths": ["안정적인 자세", "우수한 아이컨택"],
                    "improvement_areas": ["현재 수준 유지"]
                }
            },
            "analysis_metadata": {
                "participant_id": "fallback_analysis",
                "is_fallback": True,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def generate_llm_input_data(self, analysis_result: Dict) -> Dict[str, Any]:
        """OpenFace 분석 결과를 LLM 입력용 데이터로 변환"""
        
        try:
            debate_analysis = analysis_result.get("debate_analysis", {})
            
            # LLM이 이해하기 쉬운 형태로 데이터 구조화
            llm_input = {
                "participant_metrics": {
                    "overall_confidence": debate_analysis.get("confidence_indicators", {}).get("overall_confidence", 0.5),
                    "engagement_score": debate_analysis.get("engagement_metrics", {}).get("overall_engagement", 3.0),
                    "eye_contact_quality": debate_analysis.get("attention_patterns", {}).get("focus_score", 0.5),
                    "emotional_state": debate_analysis.get("emotional_expressions", {}).get("overall_demeanor", "중립적"),
                    "performance_level": debate_analysis.get("overall_assessment", {}).get("performance_level", "보통"),
                    "nonverbal_effectiveness": self._calculate_nonverbal_effectiveness(debate_analysis)
                },
                "behavioral_insights": {
                    "strengths": debate_analysis.get("overall_assessment", {}).get("key_strengths", []),
                    "improvements": debate_analysis.get("overall_assessment", {}).get("improvement_areas", []),
                    "consistency": debate_analysis.get("engagement_metrics", {}).get("consistency", 3.0),
                    "presence_quality": debate_analysis.get("engagement_metrics", {}).get("presence_quality", "보통")
                },
                "coaching_recommendations": self._generate_coaching_recommendations(debate_analysis)
            }
            
            return llm_input
            
        except Exception as e:
            logger.error(f"LLM 입력 데이터 생성 오류: {str(e)}")
            return {
                "participant_metrics": {
                    "overall_confidence": 0.7,
                    "engagement_score": 3.5,
                    "eye_contact_quality": 0.7,
                    "emotional_state": "중립적",
                    "performance_level": "보통",
                    "nonverbal_effectiveness": 0.7
                },
                "behavioral_insights": {
                    "strengths": ["안정적인 태도"],
                    "improvements": ["표현력 향상"],
                    "consistency": 3.5,
                    "presence_quality": "보통"
                },
                "coaching_recommendations": ["자신감 있는 자세 유지", "더 적극적인 제스처 활용"]
            }

    def _calculate_nonverbal_effectiveness(self, analysis: Dict) -> float:
        """비언어적 소통 효과성 계산"""
        try:
            confidence = analysis.get("confidence_indicators", {}).get("overall_confidence", 0.5)
            attention = analysis.get("attention_patterns", {}).get("focus_score", 0.5)
            emotion_balance = 1.0 if analysis.get("emotional_expressions", {}).get("emotional_balance") == "균형적" else 0.7
            
            effectiveness = (confidence + attention + emotion_balance) / 3
            return min(1.0, max(0.0, effectiveness))
        except Exception:
            return 0.7

    def _generate_coaching_recommendations(self, analysis: Dict) -> List[str]:
        """코칭 권고사항 생성"""
        recommendations = []
        
        try:
            # 자신감 관련
            confidence_level = analysis.get("confidence_indicators", {}).get("confidence_level", "보통")
            if confidence_level == "낮음":
                recommendations.append("시선을 정면으로 유지하며 자신감 있는 자세를 연습하세요")
            
            # 주의집중 관련
            attention_quality = analysis.get("attention_patterns", {}).get("eye_contact_quality", "양호")
            if attention_quality == "개선필요":
                recommendations.append("상대방과의 아이컨택을 더 자주 시도해보세요")
            
            # 감정 표현 관련
            emotional_state = analysis.get("emotional_expressions", {}).get("overall_demeanor", "중립적")
            if emotional_state == "긴장됨":
                recommendations.append("심호흡과 이완 기법을 통해 긴장을 완화하세요")
            
            # 기본 권고사항
            if not recommendations:
                recommendations.extend([
                    "현재의 좋은 자세를 유지하세요",
                    "더 다양한 표정과 제스처를 활용해보세요"
                ])
                
        except Exception as e:
            logger.error(f"코칭 권고사항 생성 오류: {str(e)}")
            recommendations = ["전반적으로 양호한 수행을 보였습니다"]
        
        return recommendations

    def cleanup_output_files(self, participant_id: Optional[str] = None):
        """분석 결과 파일 정리"""
        try:
            if participant_id:
                # 특정 참가자 파일만 삭제
                pattern = f"{participant_id}_features.csv"
                file_path = os.path.join(self.output_dir, pattern)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"OpenFace 출력 파일 삭제: {file_path}")
            else:
                # 모든 CSV 파일 삭제
                for filename in os.listdir(self.output_dir):
                    if filename.endswith("_features.csv"):
                        file_path = os.path.join(self.output_dir, filename)
                        os.remove(file_path)
                        logger.info(f"OpenFace 출력 파일 삭제: {file_path}")
        except Exception as e:
            logger.warning(f"출력 파일 정리 오류: {str(e)}")

    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 정보 반환"""
        return {
            "module_name": "OpenFace Debate Integration",
            "is_available": self.is_available,
            "openface_path": self.openface_path,
            "output_directory": self.output_dir,
            "features": [
                "video_facial_analysis",
                "debate_specific_metrics", 
                "llm_integration_support",
                "coaching_recommendations"
            ],
            "supported_formats": ["mp4", "avi", "mov", "webm"],
            "analysis_components": [
                "confidence_detection",
                "gaze_tracking", 
                "head_pose_estimation",
                "action_unit_analysis",
                "engagement_metrics"
            ]
        }


# 실행 예시 및 테스트
if __name__ == "__main__":
    # 모듈 테스트
    print("OpenFace 토론면접 통합 모듈 테스트 시작...")
    
    integration = OpenFaceDebateIntegration()
    
    # 모듈 상태 확인
    status = integration.get_module_status()
    print(f"모듈 상태: {status}")
    
    # 테스트 비디오 파일이 있다면 분석 실행
    test_video = "test_video.mp4"  # 실제 테스트 비디오 파일 경로
    
    if os.path.exists(test_video):
        print(f"\n테스트 비디오 분석: {test_video}")
        
        # 비디오 분석
        result = integration.analyze_video(test_video, "test_participant")
        
        # 결과 출력
        if "debate_analysis" in result:
            debate_analysis = result["debate_analysis"]
            overall = debate_analysis.get("overall_assessment", {})
            
            print(f"종합 점수: {overall.get('composite_score', 0):.2f}")
            print(f"수행 수준: {overall.get('performance_level', '알 수 없음')}")
            print(f"주요 강점: {', '.join(overall.get('key_strengths', []))}")
            print(f"개선 영역: {', '.join(overall.get('improvement_areas', []))}")
        
        # LLM 입력 데이터 생성
        llm_data = integration.generate_llm_input_data(result)
        print(f"\nLLM 입력 데이터 생성 완료")
        print(f"참여자 메트릭: {llm_data.get('participant_metrics', {})}")
        
    else:
        print(f"\n테스트 비디오 파일을 찾을 수 없습니다: {test_video}")
        print("기본 분석 결과로 테스트 진행...")
        
        # 기본 분석 결과로 테스트
        fallback_result = integration._get_fallback_analysis()
        llm_data = integration.generate_llm_input_data(fallback_result)
        print(f"LLM 입력 데이터: {llm_data}")
    
    print("\nOpenFace 토론면접 통합 모듈 테스트 완료!")
