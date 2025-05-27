"""
토론면접 테스트 통합 실행 모듈
LLM 미사용 환경에서 모든 기능의 통합 테스트를 수행
"""
import logging
import os
import tempfile
import time
from typing import Dict, Any, Optional

# 테스트 모듈 임포트
from .openface_module import OpenFaceTestModule
from .librosa_module import LibrosaTestModule
from .whisper_module import WhisperTestModule
from .tts_module import TTSTestModule
from .fixed_responses_module import FixedResponsesModule

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DebateTestMain:
    def __init__(self):
        """토론면접 테스트 메인 클래스 초기화"""
        logger.info("토론면접 테스트 시스템 초기화 시작")
        
        # 각 모듈 초기화
        self.openface_module = OpenFaceTestModule()
        self.librosa_module = LibrosaTestModule()
        self.whisper_module = WhisperTestModule()
        self.tts_module = TTSTestModule()
        self.responses_module = FixedResponsesModule()
        
        # 테스트 결과 저장
        self.test_results = {}
        
        logger.info("토론면접 테스트 시스템 초기화 완료")

    def run_connection_tests(self) -> Dict[str, Any]:
        """모든 모듈의 연결 테스트 실행"""
        logger.info("=== 모듈 연결 테스트 시작 ===")
        
        connection_results = {}
        
        # OpenFace 연결 테스트
        logger.info("OpenFace 연결 테스트...")
        connection_results["openface"] = self.openface_module.test_connection()
        
        # Librosa 연결 테스트
        logger.info("Librosa 연결 테스트...")
        connection_results["librosa"] = self.librosa_module.test_connection()
        
        # Whisper 연결 테스트
        logger.info("Whisper 연결 테스트...")
        connection_results["whisper"] = self.whisper_module.test_connection()
        
        # TTS 연결 테스트
        logger.info("TTS 연결 테스트...")
        connection_results["tts"] = self.tts_module.test_connection()
        
        # 고정 응답 모듈 테스트
        logger.info("고정 응답 모듈 테스트...")
        responses_status = self.responses_module.get_module_status()
        connection_results["fixed_responses"] = {
            "status": "available" if responses_status["is_available"] else "unavailable",
            "message": "고정 응답 모듈 정상 작동",
            "details": responses_status
        }
        
        logger.info("=== 모듈 연결 테스트 완료 ===")
        return connection_results

    def run_full_debate_simulation(self, video_path: Optional[str] = None, topic: str = "인공지능") -> Dict[str, Any]:
        """전체 토론 시뮬레이션 실행"""
        logger.info(f"=== 전체 토론 시뮬레이션 시작 - 주제: {topic} ===")
        
        simulation_results = {
            "topic": topic,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "phases": {}
        }
        
        # 1단계: AI 입론
        logger.info("1단계: AI 입론 생성")
        ai_opening = self.responses_module.get_debate_response("opening", topic)
        simulation_results["phases"]["ai_opening"] = {
            "text": ai_opening,
            "length": len(ai_opening)
        }
        
        # 2단계: 사용자 입론 처리 (비디오가 있는 경우)
        if video_path and os.path.exists(video_path):
            logger.info("2단계: 사용자 입론 영상 처리")
            user_opening_result = self._process_user_video(video_path, "opening")
            simulation_results["phases"]["user_opening"] = user_opening_result
            
            # AI 반론 생성
            ai_rebuttal = self.responses_module.get_debate_response("rebuttal", topic, user_opening_result.get("transcription", ""))
            simulation_results["phases"]["ai_rebuttal"] = {
                "text": ai_rebuttal,
                "length": len(ai_rebuttal)
            }
        else:
            logger.info("2단계: 비디오 없음 - 기본 시나리오 사용")
            default_user_text = "인공지능은 우리의 삶을 향상시키는 도구입니다."
            simulation_results["phases"]["user_opening"] = {
                "transcription": default_user_text,
                "facial_analysis": self.openface_module._get_default_result(),
                "audio_analysis": self.librosa_module._get_default_result()
            }
            
            ai_rebuttal = self.responses_module.get_debate_response("rebuttal", topic, default_user_text)
            simulation_results["phases"]["ai_rebuttal"] = {
                "text": ai_rebuttal,
                "length": len(ai_rebuttal)
            }
        
        # 3단계: 사용자 반론 및 AI 재반론
        logger.info("3단계: 토론 진행 시뮬레이션")
        ai_counter_rebuttal = self.responses_module.get_debate_response("counter_rebuttal", topic)
        simulation_results["phases"]["ai_counter_rebuttal"] = {
            "text": ai_counter_rebuttal,
            "length": len(ai_counter_rebuttal)
        }
        
        # 4단계: AI 최종 변론
        logger.info("4단계: AI 최종 변론")
        ai_closing = self.responses_module.get_debate_response("closing", topic)
        simulation_results["phases"]["ai_closing"] = {
            "text": ai_closing,
            "length": len(ai_closing)
        }
        
        # 5단계: TTS 테스트 (선택적)
        if self.tts_module.is_available:
            logger.info("5단계: TTS 변환 테스트")
            tts_results = self._test_tts_conversion([ai_opening, ai_rebuttal, ai_counter_rebuttal, ai_closing])
            simulation_results["tts_tests"] = tts_results
        
        logger.info("=== 전체 토론 시뮬레이션 완료 ===")
        return simulation_results

    def _process_user_video(self, video_path: str, phase: str) -> Dict[str, Any]:
        """사용자 비디오 처리"""
        logger.info(f"사용자 비디오 처리 시작: {phase}")
        
        result = {
            "phase": phase,
            "video_path": video_path
        }
        
        try:
            # Whisper 음성 인식
            if self.whisper_module.is_available:
                transcription_result = self.whisper_module.transcribe_video_file(video_path)
                result["transcription"] = transcription_result.get("text", "")
                result["transcription_confidence"] = transcription_result.get("confidence", 0.0)
            else:
                result["transcription"] = f"테스트 {phase} 텍스트입니다."
                result["transcription_confidence"] = 0.85
            
            # OpenFace 얼굴 분석
            if self.openface_module.is_available:
                facial_result = self.openface_module.analyze_video(video_path)
                result["facial_analysis"] = facial_result
                result["emotion"] = self.openface_module.evaluate_emotion(facial_result)
            else:
                result["facial_analysis"] = self.openface_module._get_default_result()
                result["emotion"] = "중립 (안정적)"
            
            # Librosa 오디오 분석
            if self.librosa_module.is_available:
                audio_result = self.librosa_module.analyze_video_audio(video_path)
                result["audio_analysis"] = audio_result
                result["voice_quality"] = self.librosa_module.evaluate_voice_quality(audio_result)
            else:
                result["audio_analysis"] = self.librosa_module._get_default_result()
                result["voice_quality"] = "양호한 음성 품질"
            
            # 점수 계산
            scores = self._calculate_comprehensive_scores(
                result.get("facial_analysis", {}),
                result.get("transcription", ""),
                result.get("audio_analysis", {})
            )
            result["scores"] = scores
            
            logger.info(f"비디오 처리 완료: {phase}")
            
        except Exception as e:
            logger.error(f"비디오 처리 오류: {str(e)}")
            result["error"] = str(e)
        
        return result

    def _calculate_comprehensive_scores(self, facial_data: Dict, text: str, audio_data: Dict) -> Dict[str, Any]:
        """종합 점수 계산"""
        scores = {
            "initiative_score": 3.0,
            "collaborative_score": 3.0,
            "communication_score": 3.0,
            "logic_score": 3.0,
            "problem_solving_score": 3.0,
            "voice_score": 3.0,
            "action_score": 3.0
        }
        
        try:
            # 얼굴 분석 기반 점수 조정
            if facial_data:
                confidence = facial_data.get("confidence", 0.5)
                gaze_stability = 1.0 - (abs(facial_data.get("gaze_angle_x", 0)) + abs(facial_data.get("gaze_angle_y", 0))) / 2
                
                scores["initiative_score"] = min(5.0, 3.0 + confidence)
                scores["action_score"] = min(5.0, 3.0 + gaze_stability)
            
            # 텍스트 분석 기반 점수 조정
            if text:
                text_length_bonus = min(1.0, len(text) / 100)
                scores["communication_score"] = min(5.0, 3.0 + text_length_bonus)
                
                # 키워드 기반 점수 조정
                logic_keywords = ["논리", "근거", "증명", "분석", "결과"]
                collaboration_keywords = ["협력", "팀워크", "함께", "공동", "상호"]
                problem_solving_keywords = ["해결", "개선", "방안", "전략", "대안"]
                
                if any(keyword in text for keyword in logic_keywords):
                    scores["logic_score"] = min(5.0, scores["logic_score"] + 0.5)
                
                if any(keyword in text for keyword in collaboration_keywords):
                    scores["collaborative_score"] = min(5.0, scores["collaborative_score"] + 0.5)
                
                if any(keyword in text for keyword in problem_solving_keywords):
                    scores["problem_solving_score"] = min(5.0, scores["problem_solving_score"] + 0.5)
            
            # 음성 분석 기반 점수 조정
            if audio_data and self.librosa_module.is_available:
                voice_scores = self.librosa_module.calculate_voice_scores(audio_data)
                scores["voice_score"] = voice_scores.get("voice_score", 3.0)
            
            # 피드백 생성
            feedback_comments = {}
            for score_type, score_value in scores.items():
                if score_type.endswith("_score"):
                    category = score_type.replace("_score", "")
                    feedback_comments[f"{category}_feedback"] = self.responses_module.get_feedback_comments(category, score_value)
            
            scores.update(feedback_comments)
            scores["overall_feedback"] = self._generate_overall_feedback(scores)
            
        except Exception as e:
            logger.error(f"점수 계산 오류: {str(e)}")
        
        return scores

    def _generate_overall_feedback(self, scores: Dict) -> str:
        """전체적인 피드백 생성"""
        try:
            score_values = [v for k, v in scores.items() if k.endswith("_score") and isinstance(v, (int, float))]
            if not score_values:
                return "점수 계산에 문제가 있어 피드백을 생성할 수 없습니다."
            
            average_score = sum(score_values) / len(score_values)
            
            if average_score >= 4.0:
                return "전반적으로 매우 우수한 수행을 보여주었습니다. 자신감 있는 태도와 논리적인 구성이 돋보입니다."
            elif average_score >= 3.5:
                return "전반적으로 좋은 수행을 보여주었습니다. 몇 가지 부분에서 더 발전시킬 여지가 있습니다."
            elif average_score >= 3.0:
                return "기본적인 수행은 양호합니다. 좀 더 적극적인 자세와 명확한 표현이 필요합니다."
            else:
                return "전반적인 개선이 필요합니다. 충분한 준비와 연습을 통해 발전시켜 보세요."
                
        except Exception as e:
            logger.error(f"전체 피드백 생성 오류: {str(e)}")
            return "피드백 생성 중 오류가 발생했습니다."

    def _test_tts_conversion(self, text_list: list) -> Dict[str, Any]:
        """TTS 변환 테스트"""
        logger.info("TTS 변환 테스트 시작")
        
        tts_results = {
            "total_texts": len(text_list),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "output_files": [],
            "errors": []
        }
        
        try:
            temp_dir = tempfile.mkdtemp(prefix="tts_test_")
            
            for i, text in enumerate(text_list):
                if not text or len(text.strip()) == 0:
                    continue
                
                output_path = os.path.join(temp_dir, f"tts_output_{i+1}.wav")
                
                try:
                    result_path = self.tts_module.text_to_speech(text[:100], output_path)  # 처음 100자만 변환
                    if result_path and os.path.exists(result_path):
                        tts_results["successful_conversions"] += 1
                        tts_results["output_files"].append({
                            "index": i+1,
                            "path": result_path,
                            "text_preview": text[:50] + "..." if len(text) > 50 else text
                        })
                        logger.info(f"TTS 변환 성공 ({i+1}/{len(text_list)})")
                    else:
                        tts_results["failed_conversions"] += 1
                        tts_results["errors"].append(f"TTS 변환 실패: 텍스트 {i+1}")
                
                except Exception as e:
                    tts_results["failed_conversions"] += 1
                    tts_results["errors"].append(f"TTS 오류 {i+1}: {str(e)}")
                    logger.error(f"TTS 변환 오류 ({i+1}): {str(e)}")
            
            logger.info(f"TTS 테스트 완료 - 성공: {tts_results['successful_conversions']}, 실패: {tts_results['failed_conversions']}")
            
        except Exception as e:
            logger.error(f"TTS 테스트 전체 오류: {str(e)}")
            tts_results["errors"].append(f"전체 테스트 오류: {str(e)}")
        
        return tts_results

    def run_individual_module_tests(self) -> Dict[str, Any]:
        """개별 모듈 상세 테스트"""
        logger.info("=== 개별 모듈 상세 테스트 시작 ===")
        
        detailed_results = {}
        
        # OpenFace 상세 테스트
        logger.info("OpenFace 상세 테스트...")
        detailed_results["openface"] = {
            "status": self.openface_module.get_module_status(),
            "connection": self.openface_module.test_connection(),
            "default_analysis": self.openface_module._get_default_result(),
            "emotion_evaluation": self.openface_module.evaluate_emotion(self.openface_module._get_default_result())
        }
        
        # Librosa 상세 테스트
        logger.info("Librosa 상세 테스트...")
        detailed_results["librosa"] = {
            "status": self.librosa_module.get_module_status(),
            "connection": self.librosa_module.test_connection(),
            "default_analysis": self.librosa_module._get_default_result(),
            "voice_quality": self.librosa_module.evaluate_voice_quality(self.librosa_module._get_default_result()),
            "voice_scores": self.librosa_module.calculate_voice_scores(self.librosa_module._get_default_result())
        }
        
        # Whisper 상세 테스트
        logger.info("Whisper 상세 테스트...")
        detailed_results["whisper"] = {
            "status": self.whisper_module.get_module_status(),
            "connection": self.whisper_module.test_connection(),
            "supported_languages": self.whisper_module.get_supported_languages(),
            "default_transcription": self.whisper_module._get_default_transcription("test")
        }
        
        # TTS 상세 테스트
        logger.info("TTS 상세 테스트...")
        detailed_results["tts"] = {
            "status": self.tts_module.get_module_status(),
            "connection": self.tts_module.test_connection(),
            "voice_settings": self.tts_module.get_voice_settings()
        }
        
        # 고정 응답 모듈 상세 테스트
        logger.info("고정 응답 모듈 상세 테스트...")
        detailed_results["fixed_responses"] = {
            "status": self.responses_module.get_module_status(),
            "test_all_responses": self.responses_module.test_all_responses()
        }
        
        logger.info("=== 개별 모듈 상세 테스트 완료 ===")
        return detailed_results

    def generate_test_report(self, save_path: Optional[str] = None) -> str:
        """종합 테스트 보고서 생성"""
        logger.info("종합 테스트 보고서 생성 시작")
        
        # 모든 테스트 실행
        connection_tests = self.run_connection_tests()
        detailed_tests = self.run_individual_module_tests()
        simulation_results = self.run_full_debate_simulation()
        
        # 보고서 내용 생성
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("토론면접 테스트 시스템 종합 보고서")
        report_lines.append("=" * 80)
        report_lines.append(f"생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 연결 테스트 결과
        report_lines.append("1. 모듈 연결 테스트 결과")
        report_lines.append("-" * 40)
        for module, result in connection_tests.items():
            status = result.get('status', 'unknown')
            message = result.get('message', 'No message')
            report_lines.append(f"  {module}: {status} - {message}")
        report_lines.append("")
        
        # 개별 모듈 상태
        report_lines.append("2. 개별 모듈 상태")
        report_lines.append("-" * 40)
        for module, details in detailed_tests.items():
            status = details.get('status', {})
            is_available = status.get('is_available', False)
            report_lines.append(f"  {module}: {'사용 가능' if is_available else '사용 불가'}")
            if 'functions' in status:
                report_lines.append(f"    기능: {', '.join(status['functions'])}")
        report_lines.append("")
        
        # 시뮬레이션 결과
        report_lines.append("3. 토론 시뮬레이션 결과")
        report_lines.append("-" * 40)
        phases = simulation_results.get('phases', {})
        for phase, data in phases.items():
            if isinstance(data, dict) and 'text' in data:
                text_preview = data['text'][:100] + "..." if len(data['text']) > 100 else data['text']
                report_lines.append(f"  {phase}: {text_preview}")
        report_lines.append("")
        
        # 추천 사항
        report_lines.append("4. 추천 사항")
        report_lines.append("-" * 40)
        unavailable_modules = [name for name, result in connection_tests.items() 
                              if result.get('status') != 'available']
        
        if unavailable_modules:
            report_lines.append("  다음 모듈의 설치/설정이 필요합니다:")
            for module in unavailable_modules:
                report_lines.append(f"    - {module}")
        else:
            report_lines.append("  모든 모듈이 정상 작동 중입니다.")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        report_content = "\n".join(report_lines)
        
        # 파일 저장 (선택적)
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"테스트 보고서 저장: {save_path}")
            except Exception as e:
                logger.error(f"보고서 저장 실패: {str(e)}")
        
        logger.info("종합 테스트 보고서 생성 완료")
        return report_content

    def cleanup_test_files(self):
        """테스트 중 생성된 임시 파일들 정리"""
        logger.info("테스트 파일 정리 시작")
        
        try:
            # TTS 임시 파일 정리
            if hasattr(self.tts_module, 'cleanup_temp_files'):
                temp_files = [result.get('path') for result in self.test_results.get('tts_outputs', []) 
                             if result.get('path')]
                cleaned_count = self.tts_module.cleanup_temp_files(temp_files)
                logger.info(f"TTS 임시 파일 {cleaned_count}개 정리")
            
            # 기타 임시 파일 정리
            temp_patterns = ['temp_video_*.mp4', 'temp_audio_*.wav', 'facial_output/temp_*']
            # 실제 파일 정리 로직은 필요시 추가
            
            logger.info("테스트 파일 정리 완료")
            
        except Exception as e:
            logger.error(f"파일 정리 오류: {str(e)}")


# 실행 예시 함수
def run_full_test_suite(video_path: Optional[str] = None):
    """전체 테스트 스위트 실행"""
    try:
        # 테스트 시스템 초기화
        test_system = DebateTestMain()
        
        # 연결 테스트
        print("모듈 연결 테스트 실행 중...")
        connection_results = test_system.run_connection_tests()
        
        # 상세 테스트
        print("개별 모듈 상세 테스트 실행 중...")
        detailed_results = test_system.run_individual_module_tests()
        
        # 토론 시뮬레이션
        print("전체 토론 시뮬레이션 실행 중...")
        if video_path:
            simulation_results = test_system.run_full_debate_simulation(video_path)
        else:
            simulation_results = test_system.run_full_debate_simulation()
        
        # 보고서 생성
        print("종합 보고서 생성 중...")
        report_path = f"debate_test_report_{int(time.time())}.txt"
        report_content = test_system.generate_test_report(report_path)
        
        print(f"테스트 완료! 보고서: {report_path}")
        print("\n" + "="*50)
        print("테스트 결과 요약:")
        print("="*50)
        
        # 간단한 요약 출력
        available_modules = []
        unavailable_modules = []
        
        for module, result in connection_results.items():
            if result.get('status') == 'available':
                available_modules.append(module)
            else:
                unavailable_modules.append(module)
        
        print(f"✅ 사용 가능한 모듈 ({len(available_modules)}개): {', '.join(available_modules)}")
        if unavailable_modules:
            print(f"❌ 사용 불가 모듈 ({len(unavailable_modules)}개): {', '.join(unavailable_modules)}")
        
        # 정리
        test_system.cleanup_test_files()
        
        return {
            "connection_results": connection_results,
            "detailed_results": detailed_results,
            "simulation_results": simulation_results,
            "report_path": report_path
        }
        
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    print("토론면접 테스트 시스템을 시작합니다...")
    
    # 비디오 파일 경로 (선택적)
    test_video_path = None  # 실제 비디오 파일 경로로 변경
    
    # 전체 테스트 실행
    results = run_full_test_suite(test_video_path)
    
    if results:
        print("모든 테스트가 완료되었습니다.")
    else:
        print("테스트 실행에 실패했습니다.")
