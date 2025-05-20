import logging
import os
from realtime_speech_to_text import RealtimeSpeechToText
from realtime_facial_analysis import RealtimeFacialAnalysis
import sounddevice as sd
import scipy.io.wavfile as wavfile
import librosa
import soundfile as sf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DebateTester:
    def __init__(self):
        self.facial_analyzer = RealtimeFacialAnalysis()
        self.speech_analyzer = RealtimeSpeechToText(model="base")
        self.video_dir = os.path.join(os.getcwd(), "data", "debate_videos")
        self.audio_dir = os.path.join(os.getcwd(), "data", "debate_audios")
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        self.fixed_responses = {
            "ai_opening": "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다.",
            "ai_rebuttal": "AI는 발전하면서도 위험을 내포하고 있으며, 통제 방안을 논의해야 합니다.",
            "ai_counter_rebuttal": "AI는 자율성을 지나치게 부여받는 것이 위험하며, 인간의 제어를 유지해야 합니다.",
            "ai_closing": "AI는 인간을 대체하는 위험을 안고 있으며, 신중한 발전이 필요합니다."
        }
        self.session = {
            "user_id": "test_user",
            "topic": "인공지능은 인간의 일자리를 대체할 것인가에 대한 찬반토론",
            "user_position": "PRO",
            "ai_stance": "CON",
            "user_speeches": [],
            "user_emotions": [],
            "scores": []
        }

    def play_audio(self, audio_path):
        """음성 파일 재생"""
        if not os.path.exists(audio_path):
            logger.error(f"음성 파일이 없습니다: {audio_path}")
            return
        try:
            sample_rate, data = wavfile.read(audio_path)
            sd.play(data, sample_rate)
            sd.wait()
            logger.info(f"음성 재생 완료: {audio_path}")
        except Exception as e:
            logger.error(f"음성 재생 오류: {str(e)}")

    def process_video(self, video_path, phase, debate_id):
        """영상 처리 및 분석"""
        video_save_path = os.path.join(self.video_dir, f"{debate_id}_{phase}.mp4")
        audio_save_path = os.path.join(self.audio_dir, f"{debate_id}_{phase}.wav")
        
        # 영상 저장 (파일 복사 대신 실제 환경에서는 업로드로 대체)
        with open(video_path, 'rb') as src, open(video_save_path, 'wb') as dst:
            dst.write(src.read())

        # 오디오 추출
        try:
            audio, sr = librosa.load(video_path, sr=16000)
            sf.write(audio_save_path, audio, sr)
        except Exception as e:
            logger.error(f"오디오 추출 오류: {str(e)}")
            audio_save_path = None

        # 분석
        text = self.speech_analyzer.transcribe_video(video_path)
        facial_result = self.facial_analyzer.analyze_video(video_path)
        audio_result = self.facial_analyzer.analyze_audio(audio_save_path) if audio_save_path else {"pitch_std": 0, "rms_mean": 0, "tempo": 0}
        emotion = self.facial_analyzer.evaluate_emotion(facial_result)
        scores = self.facial_analyzer.calculate_scores(facial_result, text, audio_result)

        # AI 응답 및 TTS
        next_phase = {
            "opening": "rebuttal",
            "rebuttal": "counter_rebuttal",
            "counter-rebuttal": "closing",
            "closing": None
        }.get(phase)
        ai_response = self.fixed_responses.get(f"ai_{next_phase}") if next_phase else None
        ai_audio_path = None
        if ai_response:
            ai_audio_path = os.path.join(self.audio_dir, f"{debate_id}_ai_{next_phase}.wav")
            self.speech_analyzer.text_to_speech(ai_response, ai_audio_path)
            if ai_audio_path:
                self.play_audio(ai_audio_path)

        # 세션 업데이트
        self.session["user_speeches"].append(text)
        self.session["user_emotions"].append(emotion)
        self.session["scores"].append(scores)

        return {
            "text": text,
            "facial_analysis": facial_result,
            "audio_analysis": audio_result,
            "emotion": emotion,
            "initiative_score": scores["initiative_score"],
            "collaborative_score": scores["collaborative_score"],
            "communication_score": scores["communication_score"],
            "logic_score": scores["logic_score"],
            "problem_solving_score": scores["problem_solving_score"],
            "voice_score": scores["voice_score"],
            "action_score": scores["action_score"],
            "initiative_feedback": scores["initiative_feedback"],
            "collaborative_feedback": scores["collaborative_feedback"],
            "communication_feedback": scores["communication_feedback"],
            "logic_feedback": scores["logic_feedback"],
            "problem_solving_feedback": scores["problem_solving_feedback"],
            "voice_feedback": scores["voice_feedback"],
            "action_feedback": scores["action_feedback"],
            "feedback": scores["feedback"],
            "sample_answer": scores["sample_answer"],
            "ai_response": ai_response,
            "ai_audio": ai_audio_path
        }

    def run_test(self, video_path, debate_id=12345):
        """테스트 실행"""
        logger.info("토론 시작")
        logger.info(f"주제: {self.session['topic']}")
        logger.info(f"사용자 입장: {self.session['user_position']}")
        logger.info(f"AI 입론: {self.fixed_responses['ai_opening']}")
        
        # AI 입론 TTS
        ai_opening_audio = os.path.join(self.audio_dir, f"{debate_id}_ai_opening.wav")
        self.speech_analyzer.text_to_speech(self.fixed_responses["ai_opening"], ai_opening_audio)
        if ai_opening_audio:
            self.play_audio(ai_opening_audio)

        phases = ["opening", "rebuttal", "counter-rebuttal", "closing"]
        for phase in phases:
            logger.info(f"\n[{phase}]")
            result = self.process_video(video_path, phase, debate_id)
            logger.info(f"사용자 발언: {result['text']}")
            logger.info(f"피드백: {result['feedback']}")
            logger.info(f"모범답변: {result['sample_answer']}")
            logger.info(f"점수: 적극성({result['initiative_score']}), 협력({result['collaborative_score']}), "
                        f"의사소통({result['communication_score']}), 논리({result['logic_score']}), "
                        f"문제해결({result['problem_solving_score']}), 목소리({result['voice_score']}), "
                        f"행동({result['action_score']})")
            if result["ai_response"]:
                logger.info(f"AI 응답: {result['ai_response']}")

        # 최종 피드백
        logger.info("\n[최종 피드백]")
        phase_names = ["입론", "반론", "재반론", "최종 변론"]
        for i, (speech, scores) in enumerate(zip(self.session["user_speeches"], self.session["scores"])):
            logger.info(f"{phase_names[i]} 발언: {speech}")
            logger.info(f"피드백: {scores['feedback']}")
            logger.info(f"모범답변: {scores['sample_answer']}")
            logger.info(f"점수: 적극성({scores['initiative_score']}), 협력({scores['collaborative_score']}), "
                        f"의사소통({scores['communication_score']}), 논리({scores['logic_score']}), "
                        f"문제해결({scores['problem_solving_score']})")

if __name__ == "__main__":
    tester = DebateTester()
    test_video = "path_to_test_video.mp4"  # 실제 영상 경로로 수정
    tester.run_test(test_video)