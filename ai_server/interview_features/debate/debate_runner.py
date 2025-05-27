"""
토론면접 실행 모듈 (LLM 사용)
OpenFace, Librosa, Whisper, TTS, LLM을 통합하여 실제 토론면접을 실행
"""
import logging
import os
import time
import tempfile
from typing import Dict, Any, Optional, List
from flask import Flask, jsonify, request
import asyncio

# 통합 모듈 임포트
from .openface_integration import DebateOpenFaceIntegration
from .llm_module import DebateLLMModule

# 기존 모듈 임포트 (테스트 환경과 공유)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'test_features', 'debate'))

from librosa_module import LibrosaTestModule
from whisper_module import WhisperTestModule  
from tts_module import TTSTestModule

logger = logging.getLogger(__name__)

class DebateRunner:
    def __init__(self, llm_api_key: str = None, llm_provider: str = "openai"):
        """토론면접 실행기 초기화"""
        logger.info("토론면접 실행기 초기화 시작")
        
        # 각 모듈 초기화
        self.openface_integration = DebateOpenFaceIntegration()
        self.librosa_module = LibrosaTestModule()
        self.whisper_module = WhisperTestModule(model="base")  # 더 정확한 모델 사용
        self.tts_module = TTSTestModule()
        self.llm_module = DebateLLMModule(
            llm_provider=llm_provider,
            api_key=llm_api_key,
            model="gpt-4" if llm_provider == "openai" else "claude-3-sonnet-20240229"
        )
        
        # 토론 상태 관리
        self.debate_sessions = {}
        
        logger.info("토론면접 실행기 초기화 완료")

    def start_debate_session(self, debate_id: int, topic: str, user_position: str = "PRO") -> Dict[str, Any]:
        """토론 세션 시작"""
        logger.info(f"토론 세션 시작 - ID: {debate_id}, 주제: {topic}")
        
        try:
            # AI 입장 결정 (사용자 반대)
            ai_position = "CON" if user_position == "PRO" else "PRO"
            
            # LLM 컨텍스트 초기화
            self.llm_module.initialize_debate_context(topic, ai_position)
            
            # 세션 상태 초기화
            self.debate_sessions[debate_id] = {
                "topic": topic,
                "user_position": user_position,
                "ai_position": ai_position,
                "current_phase": "opening",
                "phase_history": [],
                "start_time": time.time(),
                "status": "active",
                "performance_data": {}
            }
            
            # AI 입론 생성
            ai_opening_result = self.llm_module.generate_ai_opening(topic, ai_position)
            
            # TTS로 AI 입론 음성 생성
            ai_audio_path = None
            if self.tts_module.is_available:
                ai_audio_path = self.tts_module.text_to_speech(
                    ai_opening_result["ai_response"],
                    f"ai_opening_{debate_id}.wav"
                )
            
            result = {
                "debate_id": debate_id,
                "topic": topic,
                "user_position": user_position,
                "ai_position": ai_position,
                "ai_opening_text": ai_opening_result["ai_response"],
                "ai_opening_audio": ai_audio_path,
                "status": "ready_for_user_opening",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"토론 세션 시작 완료 - ID: {debate_id}")
            return result
            
        except Exception as e:
            logger.error(f"토론 세션 시작 오류: {str(e)}")
            return {"error": str(e), "debate_id": debate_id}

    def process_user_response(self, debate_id: int, video_path: str, phase: str) -> Dict[str, Any]:
        """사용자 응답 처리 및 AI 반응 생성"""
        logger.info(f"사용자 응답 처리 시작 - 토론 ID: {debate_id}, 단계: {phase}")
        
        if debate_id not in self.debate_sessions:
            return {"error": "존재하지 않는 토론 세션", "debate_id": debate_id}
        
        try:
            session = self.debate_sessions[debate_id]
            
            # 1단계: 음성 인식 (Whisper)
            transcription_result = self._transcribe_user_video(video_path)
            
            # 2단계: 얼굴 분석 (OpenFace)
            facial_analysis = self._analyze_user_facial_behavior(video_path, phase)
            
            # 3단계: 음성 분석 (Librosa)
            audio_analysis = self._analyze_user_audio(video_path)
            
            # 4단계: LLM 분석 및 응답 생성
            llm_result = self.llm_module.analyze_user_response_and_generate_rebuttal(
                transcription_result["text"],
                facial_analysis,
                audio_analysis,
                phase
            )
            
            # 5단계: AI 응답 TTS 변환
            ai_audio_path = None
            if self.tts_module.is_available and llm_result.get("ai_response"):
                ai_audio_path = self.tts_module.text_to_speech(
                    llm_result["ai_response"],
                    f"ai_{phase}_{debate_id}.wav"
                )
            
            # 6단계: 결과 통합
            result = {
                "debate_id": debate_id,
                "phase": phase,
                "user_transcription": transcription_result["text"],
                "transcription_confidence": transcription_result.get("confidence", 0.0),
                "facial_analysis_summary": facial_analysis.get("phase_analysis", {}),
                "audio_analysis_summary": self._summarize_audio_analysis(audio_analysis),
                "ai_response_text": llm_result["ai_response"],
                "ai_response_audio": ai_audio_path,
                "performance_feedback": llm_result.get("performance_feedback", {}),
                "analysis_insights": llm_result.get("analysis_insights", {}),
                "next_phase": self._determine_next_phase(phase),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 세션 상태 업데이트
            session["phase_history"].append(result)
            session["current_phase"] = result["next_phase"]
            session["performance_data"][phase] = {
                "transcription": transcription_result,
                "facial_analysis": facial_analysis,
                "audio_analysis": audio_analysis,
                "llm_insights": llm_result
            }
            
            logger.info(f"사용자 응답 처리 완료 - 토론 ID: {debate_id}, 단계: {phase}")
            return result
            
        except Exception as e:
            logger.error(f"사용자 응답 처리 오류: {str(e)}")
            return {"error": str(e), "debate_id": debate_id, "phase": phase}

    def generate_final_feedback(self, debate_id: int) -> Dict[str, Any]:
        """최종 종합 피드백 생성"""
        logger.info(f"최종 피드백 생성 시작 - 토론 ID: {debate_id}")
        
        if debate_id not in self.debate_sessions:
            return {"error": "존재하지 않는 토론 세션", "debate_id": debate_id}
        
        try:
            session = self.debate_sessions[debate_id]
            
            # 토론 전체 데이터 수집
            debate_summary = {
                "topic": session["topic"],
                "duration": time.time() - session["start_time"],
                "phases_completed": len(session["phase_history"]),
                "performance_data": session["performance_data"]
            }
            
            # LLM을 통한 종합 피드백 생성
            comprehensive_feedback = self.llm_module.generate_comprehensive_feedback(debate_summary)
            
            # 정량적 분석 추가
            quantitative_analysis = self._calculate_quantitative_metrics(session)
            
            # 최종 결과 구성
            result = {
                "debate_id": debate_id,
                "topic": session["topic"],
                "total_duration_minutes": debate_summary["duration"] / 60,
                "phases_completed": debate_summary["phases_completed"],
                "comprehensive_feedback": comprehensive_feedback,
                "quantitative_analysis": quantitative_analysis,
                "detailed_phase_analysis": self._analyze_phase_progression(session),
                "improvement_recommendations": self._generate_improvement_recommendations(session),
                "final_score": comprehensive_feedback.get("overall_performance", 7.0),
                "certification_ready": comprehensive_feedback.get("overall_performance", 7.0) >= 8.0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 세션 완료 처리
            session["status"] = "completed"
            session["final_result"] = result
            
            logger.info(f"최종 피드백 생성 완료 - 토론 ID: {debate_id}")
            return result
            
        except Exception as e:
            logger.error(f"최종 피드백 생성 오류: {str(e)}")
            return {"error": str(e), "debate_id": debate_id}

    def _transcribe_user_video(self, video_path: str) -> Dict[str, Any]:
        """사용자 비디오 음성 인식"""
        if self.whisper_module.is_available:
            return self.whisper_module.transcribe_video_file(video_path)
        else:
            return {
                "text": "음성 인식을 사용할 수 없어 기본 텍스트를 반환합니다.",
                "confidence": 0.5,
                "language": "ko"
            }

    def _analyze_user_facial_behavior(self, video_path: str, phase: str) -> Dict[str, Any]:
        """사용자 얼굴 행동 분석"""
        if self.openface_integration.is_available:
            return self.openface_integration.analyze_debate_performance(video_path, phase)
        else:
            return self.openface_integration._get_default_debate_analysis(phase)

    def _analyze_user_audio(self, video_path: str) -> Dict[str, Any]:
        """사용자 음성 분석"""
        if self.librosa_module.is_available:
            return self.librosa_module.analyze_video_audio(video_path)
        else:
            return self.librosa_module._get_default_result()

    def _summarize_audio_analysis(self, audio_data: Dict) -> Dict[str, Any]:
        """음성 분석 요약"""
        return {
            "voice_stability": audio_data.get("pitch_std", 30) < 40,
            "speaking_pace": audio_data.get("tempo", 120),
            "volume_consistency": audio_data.get("rms_mean", 0.2),
            "overall_quality": "good" if audio_data.get("pitch_std", 30) < 40 else "needs_improvement"
        }

    def _determine_next_phase(self, current_phase: str) -> str:
        """다음 단계 결정"""
        phase_sequence = {
            "opening": "rebuttal",
            "rebuttal": "counter_rebuttal", 
            "counter_rebuttal": "closing",
            "closing": "completed"
        }
        return phase_sequence.get(current_phase, "completed")

    def _calculate_quantitative_metrics(self, session: Dict) -> Dict[str, Any]:
        """정량적 메트릭 계산"""
        performance_data = session["performance_data"]
        
        metrics = {
            "average_confidence": 0.0,
            "average_engagement": 0.0,
            "speech_consistency": 0.0,
            "total_speaking_time": 0.0,
            "phase_scores": {}
        }
        
        if performance_data:
            confidences = []
            engagements = []
            
            for phase, data in performance_data.items():
                # 얼굴 분석에서 자신감 지표 추출
                facial_data = data.get("facial_analysis", {})
                phase_analysis = facial_data.get("phase_analysis", {})
                
                confidence = phase_analysis.get("confidence_indicators", {}).get("overall_confidence", 0.5)
                engagement = phase_analysis.get("engagement_score", 2.5)
                
                confidences.append(confidence)
                engagements.append(engagement)
                
                metrics["phase_scores"][phase] = {
                    "confidence": confidence,
                    "engagement": engagement
                }
            
            if confidences:
                metrics["average_confidence"] = sum(confidences) / len(confidences)
            if engagements:
                metrics["average_engagement"] = sum(engagements) / len(engagements)
        
        return metrics

    def _analyze_phase_progression(self, session: Dict) -> Dict[str, Any]:
        """단계별 진행 분석"""
        phase_history = session["phase_history"]
        
        progression = {
            "improvement_trend": "stable",
            "consistency": "good",
            "peak_performance_phase": "opening",
            "areas_needing_attention": []
        }
        
        if len(phase_history) >= 2:
            # 간단한 트렌드 분석
            first_half_avg = 3.5  # 기본값
            second_half_avg = 3.5
            
            if first_half_avg < second_half_avg:
                progression["improvement_trend"] = "improving"
            elif first_half_avg > second_half_avg:
                progression["improvement_trend"] = "declining"
        
        return progression

    def _generate_improvement_recommendations(self, session: Dict) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = [
            "논리적 구조를 더욱 체계화하여 설득력을 높이세요",
            "구체적인 사례와 데이터를 활용하여 근거를 강화하세요",
            "상대방 논리의 핵심을 정확히 파악하고 반박하세요",
            "비언어적 소통(시선 접촉, 표정 등)을 더욱 활용하세요",
            "일관된 말하기 속도와 명확한 발음을 유지하세요"
        ]
        
        # 세션 데이터 기반으로 맞춤형 권고사항 필터링
        performance_data = session.get("performance_data", {})
        
        if performance_data:
            # 실제 성과 데이터 기반 권고사항 커스터마이징
            pass
        
        return recommendations[:3]  # 상위 3개 권고사항

    def get_debate_status(self, debate_id: int) -> Dict[str, Any]:
        """토론 상태 조회"""
        if debate_id not in self.debate_sessions:
            return {"error": "존재하지 않는 토론 세션", "debate_id": debate_id}
        
        session = self.debate_sessions[debate_id]
        
        return {
            "debate_id": debate_id,
            "status": session["status"],
            "current_phase": session["current_phase"],
            "topic": session["topic"],
            "phases_completed": len(session["phase_history"]),
            "elapsed_time": time.time() - session["start_time"],
            "is_active": session["status"] == "active"
        }

    def cleanup_session(self, debate_id: int) -> bool:
        """세션 정리"""
        try:
            if debate_id in self.debate_sessions:
                session = self.debate_sessions[debate_id]
                
                # 생성된 오디오 파일들 정리
                for phase_data in session.get("phase_history", []):
                    ai_audio = phase_data.get("ai_response_audio")
                    if ai_audio and os.path.exists(ai_audio):
                        os.remove(ai_audio)
                
                # 세션 데이터 삭제
                del self.debate_sessions[debate_id]
                
                logger.info(f"토론 세션 정리 완료 - ID: {debate_id}")
                return True
            
        except Exception as e:
            logger.error(f"세션 정리 오류: {str(e)}")
        
        return False

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 전체 상태 반환"""
        return {
            "debate_runner": "active",
            "active_sessions": len([s for s in self.debate_sessions.values() if s["status"] == "active"]),
            "total_sessions": len(self.debate_sessions),
            "modules": {
                "openface": self.openface_integration.is_available,
                "librosa": self.librosa_module.is_available,  
                "whisper": self.whisper_module.is_available,
                "tts": self.tts_module.is_available,
                "llm": self.llm_module.is_available
            },
            "capabilities": [
                "multimodal_analysis",
                "llm_powered_responses", 
                "real_time_feedback",
                "comprehensive_evaluation",
                "adaptive_difficulty"
            ]
        }

# Flask 애플리케이션 통합을 위한 함수들
def create_debate_api(llm_api_key: str = None) -> Flask:
    """토론 API Flask 앱 생성"""
    app = Flask(__name__)
    debate_runner = DebateRunner(llm_api_key=llm_api_key)
    
    @app.route('/api/debate/<int:debate_id>/start', methods=['POST'])
    def start_debate(debate_id):
        data = request.json or {}
        topic = data.get('topic', '인공지능의 사회적 영향')
        user_position = data.get('position', 'PRO')
        
        result = debate_runner.start_debate_session(debate_id, topic, user_position)
        return jsonify(result)
    
    @app.route('/api/debate/<int:debate_id>/process', methods=['POST'])
    def process_response(debate_id):
        if 'video' not in request.files:
            return jsonify({"error": "비디오 파일이 필요합니다"}), 400
        
        video_file = request.files['video']
        phase = request.form.get('phase', 'opening')
        
        # 임시 파일로 저장
        temp_path = f"temp_debate_{debate_id}_{phase}.mp4"
        video_file.save(temp_path)
        
        try:
            result = debate_runner.process_user_response(debate_id, temp_path, phase)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @app.route('/api/debate/<int:debate_id>/feedback', methods=['GET'])
    def get_final_feedback(debate_id):
        result = debate_runner.generate_final_feedback(debate_id)
        return jsonify(result)
    
    @app.route('/api/debate/<int:debate_id>/status', methods=['GET'])
    def get_status(debate_id):
        result = debate_runner.get_debate_status(debate_id)
        return jsonify(result)
    
    @app.route('/api/debate/system/status', methods=['GET'])
    def get_system_status():
        result = debate_runner.get_system_status()
        return jsonify(result)
    
    return app

if __name__ == "__main__":
    # 직접 실행 시 테스트 서버 시작
    app = create_debate_api()
    print("토론면접 LLM 통합 서버를 시작합니다...")
    print("엔드포인트:")
    print("  POST /api/debate/<id>/start - 토론 시작")
    print("  POST /api/debate/<id>/process - 사용자 응답 처리")
    print("  GET /api/debate/<id>/feedback - 최종 피드백")
    print("  GET /api/debate/<id>/status - 토론 상태")
    print("  GET /api/debate/system/status - 시스템 상태")
    
    app.run(host="0.0.0.0", port=5001, debug=True)
