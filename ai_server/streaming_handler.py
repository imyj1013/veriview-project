# -*- coding: utf-8 -*-
"""
스트리밍 핸들러 모듈
main_server.py와 test_server.py에서 공통으로 사용하는 스트리밍 기능
"""
from flask import Response, stream_with_context
import json
import time
import logging
import os
import base64
from typing import Generator, Dict, Any, Optional

logger = logging.getLogger(__name__)

class StreamingHandler:
    """스트리밍 응답 처리 클래스"""
    
    def __init__(self, tts_model=None, llm_module=None):
        self.tts_model = tts_model
        self.llm_module = llm_module
        self.tts_available = tts_model is not None
        self.llm_available = llm_module is not None
    
    def create_streaming_response(self, debate_id: int, stage: str, topic: str, 
                                position: str, user_text: str) -> Response:
        """스트리밍 응답 생성"""
        def generate():
            try:
                sentence_buffer = ""
                full_text = ""
                
                # LLM 사용 가능한 경우
                if self.llm_available:
                    for token in self._generate_llm_tokens(stage, topic, position, user_text):
                        sentence_buffer += token
                        full_text += token
                        
                        # 문장 완성 시 처리
                        if any(punct in token for punct in '.!?'):
                            # TTS 처리
                            audio_data = self._process_tts(sentence_buffer, debate_id)
                            if audio_data:
                                yield f"data: {json.dumps({'type': 'audio', 'data': audio_data})}\n\n"
                            
                            # 텍스트 전송
                            yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                            sentence_buffer = ""
                
                else:
                    # 폴백 모드 (고정 응답)
                    fallback_response = self._get_fallback_response(stage, topic, position, user_text)
                    
                    # 단어 단위로 스트리밍
                    words = fallback_response.split()
                    for i, word in enumerate(words):
                        if i > 0:
                            word = " " + word
                        sentence_buffer += word
                        full_text += word
                        
                        # 문장 완성 체크
                        if any(punct in word for punct in '.!?'):
                            # TTS 처리
                            audio_data = self._process_tts(sentence_buffer, debate_id)
                            if audio_data:
                                yield f"data: {json.dumps({'type': 'audio', 'data': audio_data})}\n\n"
                            
                            # 텍스트 전송
                            yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                            sentence_buffer = ""
                        
                        time.sleep(0.05)  # 자연스러운 속도
                
                # 남은 텍스트 처리
                if sentence_buffer:
                    yield f"data: {json.dumps({'type': 'text', 'data': sentence_buffer})}\n\n"
                
                # 완료 신호
                yield f"data: {json.dumps({'type': 'complete', 'full_text': full_text})}\n\n"
                
            except Exception as e:
                logger.error(f"스트리밍 생성 중 오류: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    def _generate_llm_tokens(self, stage: str, topic: str, position: str, 
                           user_text: str) -> Generator[str, None, None]:
        """LLM 토큰 생성"""
        if not self.llm_available:
            return
        
        try:
            # 실제 LLM 모듈의 스트리밍 메서드 호출
            prompt = self._create_prompt(stage, topic, position, user_text)
            
            # 여기서는 예시로 단어 단위 생성
            # 실제로는 LLM 모듈의 스트리밍 API를 사용해야 함
            response = self._get_llm_response(stage, topic, position, user_text)
            for word in response.split():
                yield word + " "
                
        except Exception as e:
            logger.error(f"LLM 토큰 생성 오류: {str(e)}")
    
    def _process_tts(self, text: str, debate_id: int) -> Optional[str]:
        """TTS 처리 및 base64 인코딩"""
        if not self.tts_available or not text.strip():
            return None
        
        try:
            # 임시 파일 경로
            temp_audio = f"temp_stream_{debate_id}_{int(time.time())}.wav"
            
            # TTS 변환
            self.tts_model.tts_to_file(text=text, file_path=temp_audio)
            
            # 파일을 base64로 인코딩
            with open(temp_audio, 'rb') as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # 임시 파일 삭제
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"TTS 처리 오류: {str(e)}")
            return None
    
    def _create_prompt(self, stage: str, topic: str, position: str, user_text: str) -> str:
        """프롬프트 생성"""
        prompts = {
            "opening": f"토론 주제 '{topic}'에 대해 {position} 입장에서 입론을 작성하세요.",
            "rebuttal": f"상대방의 의견 '{user_text}'에 대해 반박하세요.",
            "counter_rebuttal": f"상대방의 반론 '{user_text}'에 대해 재반박하세요.",
            "closing": f"토론 주제 '{topic}'에 대한 최종 변론을 작성하세요."
        }
        return prompts.get(stage, prompts["opening"])
    
    def _get_llm_response(self, stage: str, topic: str, position: str, user_text: str) -> str:
        """LLM 응답 생성 (실제 구현 필요)"""
        # 실제로는 LLM 모듈을 사용해야 함
        return self._get_fallback_response(stage, topic, position, user_text)
    
    def _get_fallback_response(self, stage: str, topic: str, position: str, user_text: str) -> str:
        """폴백 응답"""
        responses = {
            "opening": {
                "PRO": f"{topic}의 발전은 인류에게 긍정적인 영향을 미칠 것입니다. 효율성 증대와 새로운 가능성을 제공하기 때문입니다.",
                "CON": f"{topic}에 대해서는 신중한 접근이 필요합니다. 여러 부작용과 위험성을 고려해야 합니다."
            },
            "rebuttal": f"말씀하신 의견을 경청했습니다. 하지만 {topic}의 다른 측면도 고려해야 합니다.",
            "counter_rebuttal": f"제기하신 점들을 이해했습니다. 그러나 {topic}의 장기적 영향을 고려하면 신중한 접근이 필요합니다.",
            "closing": f"결론적으로 {topic}에 대한 균형잡힌 시각이 중요합니다. 다양한 관점을 고려해야 합니다."
        }
        
        if stage == "opening":
            return responses["opening"].get(position, responses["opening"]["CON"])
        return responses.get(stage, f"{topic}에 대한 의견을 나눠주셔서 감사합니다.")

class InterviewStreamingHandler:
    """면접 스트리밍 처리 클래스"""
    
    def __init__(self, whisper_model=None, openface_module=None, librosa_available=False):
        self.whisper_model = whisper_model
        self.openface_module = openface_module
        self.librosa_available = librosa_available
    
    def create_streaming_response(self, interview_id: int, video_path: str) -> Response:
        """면접 영상 실시간 분석 스트리밍"""
        def generate():
            try:
                # 1. 처리 시작 알림
                yield f"data: {json.dumps({'type': 'status', 'message': '영상 분석을 시작합니다...'})}\n\n"
                
                # 2. 음성 추출
                audio_path = self._extract_audio(video_path)
                if audio_path:
                    yield f"data: {json.dumps({'type': 'status', 'message': '음성 추출 완료'})}\n\n"
                
                # 3. 음성 인식
                if self.whisper_model and audio_path:
                    transcription = self._transcribe_audio(audio_path)
                    if transcription:
                        yield f"data: {json.dumps({'type': 'transcription', 'data': transcription})}\n\n"
                
                # 4. 음성 분석
                if self.librosa_available and audio_path:
                    audio_analysis = self._analyze_audio(audio_path)
                    if audio_analysis:
                        yield f"data: {json.dumps({'type': 'audio_analysis', 'data': audio_analysis})}\n\n"
                
                # 5. 얼굴 분석
                if self.openface_module:
                    facial_analysis = self._analyze_facial(video_path)
                    if facial_analysis:
                        yield f"data: {json.dumps({'type': 'facial_analysis', 'data': facial_analysis})}\n\n"
                
                # 6. 종합 점수 계산
                scores = self._calculate_scores(transcription, audio_analysis, facial_analysis)
                yield f"data: {json.dumps({'type': 'scores', 'data': scores})}\n\n"
                
                # 7. 피드백 생성
                feedback = self._generate_feedback(transcription, audio_analysis, facial_analysis, scores)
                yield f"data: {json.dumps({'type': 'feedback', 'data': feedback})}\n\n"
                
                # 8. 완료
                yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                
                # 임시 파일 정리
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
                
            except Exception as e:
                logger.error(f"면접 스트리밍 처리 오류: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    def _extract_audio(self, video_path: str) -> Optional[str]:
        """비디오에서 오디오 추출"""
        try:
            import subprocess
            audio_path = video_path.replace('.mp4', '_audio.wav').replace('.webm', '_audio.wav')
            
            command = [
                'ffmpeg', '-i', video_path, '-acodec', 'pcm_s16le', 
                '-ac', '1', '-ar', '16000', audio_path, '-y'
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            
            if os.path.exists(audio_path):
                return audio_path
            return None
        except Exception as e:
            logger.error(f"오디오 추출 오류: {str(e)}")
            return None
    
    def _transcribe_audio(self, audio_path: str) -> Optional[str]:
        """음성 인식"""
        try:
            result = self.whisper_model.transcribe(audio_path, language="ko")
            return result.get("text", "")
        except Exception as e:
            logger.error(f"음성 인식 오류: {str(e)}")
            return None
    
    def _analyze_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """오디오 분석"""
        try:
            import librosa
            y, sr = librosa.load(audio_path)
            
            # 기본 분석
            return {
                "voice_stability": 0.8,
                "speaking_rate": 120,
                "fluency": 0.85
            }
        except Exception as e:
            logger.error(f"오디오 분석 오류: {str(e)}")
            return None
    
    def _analyze_facial(self, video_path: str) -> Optional[Dict[str, Any]]:
        """얼굴 분석"""
        try:
            # 실제 OpenFace 분석
            return {
                "confidence": 0.8,
                "emotion": "중립",
                "gaze_stability": 0.75
            }
        except Exception as e:
            logger.error(f"얼굴 분석 오류: {str(e)}")
            return None
    
    def _calculate_scores(self, transcription: str, audio_analysis: Dict, 
                         facial_analysis: Dict) -> Dict[str, float]:
        """점수 계산"""
        return {
            "content_score": min(5.0, 3.0 + len(transcription.split()) / 50) if transcription else 3.0,
            "voice_score": min(5.0, audio_analysis.get("voice_stability", 0.7) * 5) if audio_analysis else 3.5,
            "action_score": min(5.0, facial_analysis.get("confidence", 0.7) * 5) if facial_analysis else 3.5
        }
    
    def _generate_feedback(self, transcription: str, audio_analysis: Dict, 
                          facial_analysis: Dict, scores: Dict) -> str:
        """피드백 생성"""
        feedback_parts = []
        
        if scores["content_score"] >= 4.0:
            feedback_parts.append("충분한 내용으로 답변하셨습니다.")
        else:
            feedback_parts.append("더 구체적인 답변이 필요합니다.")
        
        if scores["voice_score"] >= 4.0:
            feedback_parts.append("안정적인 음성으로 전달하셨습니다.")
        
        if scores["action_score"] >= 4.0:
            feedback_parts.append("자신감 있는 태도를 보이셨습니다.")
        
        return " ".join(feedback_parts)
