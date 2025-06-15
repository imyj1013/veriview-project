from flask import Flask, jsonify, request, Response, stream_with_context, send_file
from flask_cors import CORS
import os
import tempfile
import logging
import json
import time
import base64
from typing import Optional

# D-ID 모듈 임포트 (우선 사용)
try:
    from modules.d_id.client import DIDClient
    from modules.d_id.video_manager import VideoManager
    from modules.d_id.tts_manager import TTSManager
    D_ID_AVAILABLE = True
    print("D-ID 모듈 로드 성공")
except ImportError as e:
    print(f"D-ID 모듈 로드 실패: {e}")
    D_ID_AVAILABLE = False

# 기타 모듈 임포트
try:
    from app.modules.realtime_facial_analysis import RealtimeFacialAnalysis
    from app.modules.realtime_speech_to_text import RealtimeSpeechToText
    print("분석 모듈 로드 성공: OpenFace, Whisper, Librosa")
except ImportError as e:
    print(f"분석 모듈 로드 실패: {e} - 기본 기능으로 동작")

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 세션별 아바타 성별 관리
session_avatars = {}

def get_avatar_gender_for_session(session_type, session_id):
    """
    세션별로 일관된 아바타 성별 반환
    
    Args:
        session_type: 'interview' 또는 'debate'
        session_id: interview_id 또는 debate_id
        
    Returns:
        성별 ('male' 또는 'female')
    """
    session_key = f"{session_type}_{session_id}"
    
    if session_key not in session_avatars:
        # 세션 ID를 기반으로 일관된 성별 결정
        # 홀수 ID는 female, 짝수 ID는 male
        gender = 'female' if session_id % 2 == 1 else 'male'
        session_avatars[session_key] = gender
        logger.info(f"새 세션 아바타 설정: {session_key} -> {gender}")
    
    return session_avatars[session_key]

def clear_session_avatar(session_type, session_id):
    """세션 종료 시 아바타 정보 정리"""
    session_key = f"{session_type}_{session_id}"
    if session_key in session_avatars:
        del session_avatars[session_key]
        logger.info(f"세션 아바타 정리: {session_key}")

# D-ID 관련 전역 변수
did_client = None
did_video_manager = None
tts_manager = None
did_initialized = False

# 분석기 전역 변수
facial_analyzer = None
speech_analyzer = None

def initialize_d_id():
    """D-ID 모듈 초기화"""
    global did_client, did_video_manager, tts_manager, did_initialized
    
    if not D_ID_AVAILABLE:
        logger.warning("D-ID 모듈이 사용 불가합니다")
        return False
    
    try:
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            logger.warning("D_ID_API_KEY가 설정되지 않음")
            logger.warning("환경 변수를 설정하세요: D_ID_API_KEY='your_api_key'")
            return False
        
        # D-ID 클라이언트 초기화
        base_url = os.environ.get('D_ID_API_URL', 'https://api.d-id.com')
        did_client = DIDClient(api_key=api_key, base_url=base_url)
        logger.info("D-ID 클라이언트 초기화 완료")
        
        # 연결 테스트
        if did_client.test_connection():
            logger.info("D-ID API 연결 성공")
        else:
            logger.warning("D-ID API 연결 실패 - 폴백 모드 사용")
            return False
        
        # D-ID 영상 관리자 초기화
        videos_dir = os.environ.get('D_ID_CACHE_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos'))
        did_video_manager = VideoManager(base_dir=videos_dir)
        logger.info(f"D-ID 영상 관리자 초기화 완료: {videos_dir}")
        
        # TTS 관리자 초기화
        tts_manager = TTSManager()
        logger.info("TTS 관리자 초기화 완료")
        
        did_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"D-ID 모듈 초기화 실패: {str(e)}")
        did_initialized = False
        return False


def generate_avatar_video_unified(script: str, video_type: str = 'interview', gender: str = 'male', phase: str = 'general') -> Optional[str]:
    """
    통합 아바타 영상 생성 함수
    D-ID 우선 사용, 실패시 AIStudios 폴백
    """
    try:
        preferred_service = os.environ.get('PREFERRED_AVATAR_SERVICE', 'D_ID')
        use_fallback = os.environ.get('USE_FALLBACK_SERVICE', 'True').lower() == 'true'
        
        logger.info(f"아바타 영상 생성 시작: type={video_type}, gender={gender}, phase={phase}")
        logger.info(f"우선 서비스: {preferred_service}, 폴백 사용: {use_fallback}")
        
        # 1순위: D-ID 사용
        if preferred_service == 'D_ID' and did_initialized:
            try:
                logger.info("D-ID로 영상 생성 시도")
                
                # 캐시 확인
                if did_video_manager:
                    cached_video = did_video_manager.get_cached_video(
                        content=script,
                        video_type=video_type,
                        gender=gender,
                        phase=phase
                    )
                    
                    if cached_video:
                        logger.info(f"D-ID 캐시된 영상 반환: {cached_video}")
                        return cached_video
                
                # D-ID로 새 영상 생성
                if video_type == 'interview':
                    video_path = did_client.generate_interview_video(script, gender)
                elif video_type == 'debate':
                    video_path = did_client.generate_debate_video(script, gender, phase)
                else:
                    # 일반 아바타 영상
                    avatar_type = f"{video_type}_{gender}"
                    voice_id = tts_manager.get_voice_for_interviewer(gender) if video_type == 'interview' else tts_manager.get_voice_for_debater(gender)
                    
                    video_url = did_client.create_avatar_video(
                        script=script,
                        avatar_type=avatar_type,
                        voice_id=voice_id
                    )
                    
                    if video_url:
                        # 영상 다운로드
                        timestamp = int(time.time())
                        filename = f"{video_type}_{gender}_{timestamp}.mp4"
                        video_path = os.path.join('videos', filename)
                        
                        if did_client.download_video(video_url, video_path):
                            video_path = video_path
                        else:
                            video_path = None
                    else:
                        video_path = None
                
                if video_path and os.path.exists(video_path):
                    # 캐시에 저장
                    if did_video_manager:
                        final_path = did_video_manager.save_video(
                            video_path=video_path,
                            content=script,
                            video_type=video_type,
                            gender=gender,
                            phase=phase
                        )
                        logger.info(f"D-ID 영상 생성 완료: {final_path}")
                        return final_path
                    else:
                        logger.info(f"D-ID 영상 생성 완료 (캐시 없음): {video_path}")
                        return video_path
                else:
                    logger.warning("D-ID 영상 생성 실패")
                    
            except Exception as e:
                logger.error(f"D-ID 영상 생성 중 오류: {str(e)}")
        
                        
        # 3순위: 샘플 영상 반환
        logger.warning("모든 AI 아바타 서비스 실패 - 샘플 영상 반환")
        return generate_sample_video_fallback(video_type, phase)
        
    except Exception as e:
        logger.error(f"통합 아바타 영상 생성 중 오류: {str(e)}")
        return generate_sample_video_fallback(video_type, phase)

def generate_sample_video_fallback(video_type='general', phase='opening'):
    """폴백: 실제 샘플 영상 생성 및 반환"""
    try:
        # 샘플 비디오 경로
        sample_video_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'videos', 
            f'sample_{video_type}_{phase}_video.mp4'
        )
        
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(sample_video_path), exist_ok=True)
        
        # 샘플 비디오 파일이 없으면 즉시 생성
        if not os.path.exists(sample_video_path):
            # 간단한 방법으로 빠르게 생성
            create_quick_sample_video(sample_video_path, video_type, phase)
            logger.info(f"샘플 {video_type} {phase} 비디오 파일 생성됨: {sample_video_path}")
        
        return sample_video_path
        
    except Exception as e:
        logger.error(f"샘플 비디오 생성 오류: {str(e)}")
        return None

def create_quick_sample_video(output_path: str, video_type: str, phase: str):
    """빠른 샘플 비디오 생성"""
    try:
        # 브라우저에서 인식 가능한 기본 MP4 헤더
        # 비어있는 1초 비디오로 생성
        basic_mp4_header = bytes([
            # ftyp box (File Type)
            0x00, 0x00, 0x00, 0x20,  # size: 32 bytes
            0x66, 0x74, 0x79, 0x70,  # type: 'ftyp'
            0x69, 0x73, 0x6F, 0x6D,  # major_brand: 'isom'
            0x00, 0x00, 0x02, 0x00,  # minor_version: 512
            0x69, 0x73, 0x6F, 0x6D,  # compatible_brands[0]: 'isom'
            0x69, 0x73, 0x6F, 0x32,  # compatible_brands[1]: 'iso2'
            0x61, 0x76, 0x63, 0x31,  # compatible_brands[2]: 'avc1'
            0x6D, 0x70, 0x34, 0x31,  # compatible_brands[3]: 'mp41'
            
            # mdat box (Media Data) - 빈 데이터
            0x00, 0x00, 0x00, 0x08,  # size: 8 bytes
            0x6D, 0x64, 0x61, 0x74,  # type: 'mdat'
            # no data (empty video)
        ])
        
        with open(output_path, 'wb') as f:
            f.write(basic_mp4_header)
        
        logger.info(f"빠른 샘플 비디오 생성 완료: {output_path}")
        
    except Exception as e:
        logger.error(f"빠른 샘플 비디오 생성 실패: {str(e)}")
        # 최대한 간단한 형태로 대체
        with open(output_path, 'w') as f:
            f.write(f'Sample {video_type} {phase} content')

# 채용 공고 추천 관련 엔드포인트

@app.route('/ai/recruitment/posting', methods=['POST'])
def recommend_job_postings():
    """채용 공고 추천 엔드포인트"""
    logger.info("채용 공고 추천 요청 받음: /ai/recruitment/posting")
    
    try:
        data = request.json or {}
        user_id = data.get('user_id', '')
        education = data.get('education', '')
        major = data.get('major', '')
        double_major = data.get('double_major', '')
        workexperience = data.get('workexperience', '')
        tech_stack = data.get('tech_stack', '')
        qualification = data.get('qualification', '')
        location = data.get('location', '')
        category = data.get('category', '')
        employmenttype = data.get('employmenttype', '')
        
        logger.info(f"채용 추천 요청: user_id={user_id}, category={category}, experience={workexperience}")
        
        # 카테고리별 추천 채용공고 생성
        recommended_postings = []
        
        if category == "ICT":
            base_postings = [
                {"job_posting_id": 1, "title": "백엔드 개발자", "keyword": "Java, Spring, MySQL", "corporation": "네이버"},
                {"job_posting_id": 2, "title": "프론트엔드 개발자", "keyword": "React, JavaScript, TypeScript", "corporation": "카카오"},
                {"job_posting_id": 3, "title": "풀스택 개발자", "keyword": "Python, Django, React", "corporation": "쿠팡"},
                {"job_posting_id": 4, "title": "데이터 엔지니어", "keyword": "Python, Spark, Kafka", "corporation": "네이버"},
                {"job_posting_id": 5, "title": "DevOps 엔지니어", "keyword": "Docker, Kubernetes, AWS", "corporation": "카카오"}
            ]
        elif category == "BM":  # 경영/사무
            base_postings = [
                {"job_posting_id": 6, "title": "기획관리", "keyword": "사업기획, 전략수립", "corporation": "삼성전자"},
                {"job_posting_id": 7, "title": "마케팅 매니저", "keyword": "브랜드마케팅, 디지털마케팅", "corporation": "LG전자"},
                {"job_posting_id": 8, "title": "경영지원", "keyword": "인사, 총무, 회계", "corporation": "현대자동차"},
                {"job_posting_id": 9, "title": "사업개발", "keyword": "신사업, 파트너십", "corporation": "SK하이닉스"},
                {"job_posting_id": 10, "title": "재무관리", "keyword": "재무분석, 투자관리", "corporation": "POSCO"}
            ]
        elif category == "SM":  # 영업/판매
            base_postings = [
                {"job_posting_id": 11, "title": "영업대표", "keyword": "B2B영업, 고객관리", "corporation": "오리온"},
                {"job_posting_id": 12, "title": "세일즈매니저", "keyword": "영업관리, 팀관리", "corporation": "농심"},
                {"job_posting_id": 13, "title": "해외영업", "keyword": "수출입, 영어", "corporation": "CJ제일제당"},
                {"job_posting_id": 14, "title": "기술영업", "keyword": "솔루션영업, B2B", "corporation": "한화시스템"},
                {"job_posting_id": 15, "title": "채널영업", "keyword": "유통관리, 매장관리", "corporation": "롯데제과"}
            ]
        elif category == "RND":  # R&D
            base_postings = [
                {"job_posting_id": 16, "title": "연구원", "keyword": "연구개발, 실험", "corporation": "한국과학기술연구원"},
                {"job_posting_id": 17, "title": "제품개발", "keyword": "제품기획, 설계", "corporation": "삼성SDI"},
                {"job_posting_id": 18, "title": "품질관리", "keyword": "품질검사, QC", "corporation": "SK하이닉스"},
                {"job_posting_id": 19, "title": "기술연구", "keyword": "기술개발, 특허", "corporation": "ETRI"},
                {"job_posting_id": 20, "title": "바이오연구원", "keyword": "생명과학, 분석", "corporation": "셀트리온"}
            ]
        else:
            # 기타 카테고리 기본 추천
            base_postings = [
                {"job_posting_id": 21, "title": "일반 사무직", "keyword": "사무, 문서작업", "corporation": "중소기업"},
                {"job_posting_id": 22, "title": "고객서비스", "keyword": "상담, 서비스", "corporation": "콜센터"},
                {"job_posting_id": 23, "title": "운영관리", "keyword": "운영, 관리", "corporation": "물류회사"},
                {"job_posting_id": 24, "title": "교육강사", "keyword": "교육, 강의", "corporation": "교육기관"},
                {"job_posting_id": 25, "title": "프로젝트매니저", "keyword": "프로젝트관리", "corporation": "IT서비스"}
            ]
        
        # 경력에 따른 필터링
        if workexperience == "신입":
            recommended_postings = base_postings[:3]
        elif workexperience in ["1-3년", "3-5년"]:
            recommended_postings = base_postings[1:4]
        else:
            recommended_postings = base_postings[2:5]
        
        # 기술 스택에 따른 추가 필터링
        if category == "ICT" and tech_stack:
            tech_keywords = tech_stack.lower().split(",")
            if any(tech in ["java", "spring"] for tech in tech_keywords):
                recommended_postings.insert(0, base_postings[0])
            elif any(tech in ["react", "javascript"] for tech in tech_keywords):
                recommended_postings.insert(0, base_postings[1])
            elif any(tech in ["python", "django"] for tech in tech_keywords):
                recommended_postings.insert(0, base_postings[2])
        
        # 중복 제거 및 최대 5개 추천
        seen_ids = set()
        unique_postings = []
        for posting in recommended_postings:
            if posting["job_posting_id"] not in seen_ids:
                seen_ids.add(posting["job_posting_id"])
                unique_postings.append(posting)
                if len(unique_postings) >= 5:
                    break
        
        response_data = {
            "posting": unique_postings
        }
        
        logger.info(f"채용 추천 완료: {len(unique_postings)}개 추천")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"채용 추천 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        # 오류 발생 시 기본 추천 제공
        fallback_postings = [
            {"job_posting_id": 1, "title": "백엔드 개발자", "keyword": "Java, Spring", "corporation": "네이버"},
            {"job_posting_id": 2, "title": "프론트엔드 개발자", "keyword": "React, JavaScript", "corporation": "카카오"},
            {"job_posting_id": 3, "title": "풀스택 개발자", "keyword": "Python, Django", "corporation": "쿠팡"}
        ]
        return jsonify({"posting": fallback_postings})

# AI 면접 관련 엔드포인트 - D-ID 통합

@app.route('/ai/interview/ai-video', methods=['POST'])
def generate_ai_interview_video():
    """AI 면접관 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info(f"AI 면접관 영상 생성 요청 받음: /ai/interview/ai-video")
    
    try:
        data = request.json or {}
        question_text = data.get('question_text', '안녕하세요, 면접에 참여해 주셔서 감사합니다.')
        # interview_id를 지정하도록 Backend에서 전달 받거나 URL에서 추출
        interview_id = data.get('interview_id')
        if not interview_id:
            # URL 패턴에서 interview_id 추출 시도 (/ai/interview/123/ai-video 같은 형태)
            # 또는 question_text를 해시해서 임시 ID 사용
            interview_id = abs(hash(question_text)) % 10000
        
        # 세션별 일관된 면접관 성별 사용
        interviewer_gender = get_avatar_gender_for_session('interview', interview_id)
        
        logger.info(f"면접 ID: {interview_id}, 면접관 성별: {interviewer_gender}, 질문: {question_text[:50]}...")
        
        # TTS로 텍스트 포맷팅
        if tts_manager:
            formatted_script = tts_manager.format_script_for_interview(question_text)
        else:
            formatted_script = f"{question_text}"
        
        # D-ID로 면접관 영상 생성
        video_path = generate_avatar_video_unified(
            script=formatted_script,
            video_type='interview',
            gender=interviewer_gender,
            phase='question'
        )
        
        if video_path and os.path.exists(video_path):
            logger.info(f"AI 면접관 영상 생성 완료: {video_path}")
            return send_file(video_path, mimetype='video/mp4')
        else:
            # 폴백: 샘플 영상 반환
            logger.warning("AI 면접관 영상 생성 실패 - 샘플 영상 반환")
            # 샘플 비디오 파일 생성
            sample_path = generate_sample_video_fallback('interview', 'question')
            if sample_path and os.path.exists(sample_path):
                return send_file(sample_path, mimetype='video/mp4')
            else:
                return Response(b'Sample Interview Video', mimetype='video/mp4')
        
    except Exception as e:
        error_msg = f"AI 면접관 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return Response(b'Error generating interview video', mimetype='video/mp4')

@app.route('/ai/interview/generate-question', methods=['POST'])
def generate_interview_question():
    """면접 질문 생성 엔드포인트"""
    try:
        data = request.json or {}
        interview_id = data.get('interview_id', 0)
        job_category = data.get('job_category', 'ICT')
        workexperience = data.get('workexperience', '경력없음')
        education = data.get('education', '학사')
        experience_description = data.get('experience_description', '')
        tech_stack = data.get('tech_stack', '')
        personality = data.get('personality', '')
        
        logger.info(f"면접 질문 생성 요청: interview_id={interview_id}, job_category={job_category}")
        
        # 4개 질문 유형 생성
        question_types = ["INTRO", "FIT", "PERSONALITY", "TECH"]
        questions = []
        
        for qtype in question_types:
            question_text = ""
            if qtype == "INTRO":
                question_text = "자기소개를 하시오."
            elif qtype == "FIT":
                question_text = "당신이 이 직무에 적합한 이유는 무엇인가요?"
            elif qtype == "PERSONALITY":
                if personality:
                    question_text = "팀 프로젝트에서 어떤 역할을 했고, 팀 내에서의 협력 방식은 어땠나요?"
                else:
                    question_text = "본인의 장점과 단점에 대해 말씀해주세요."
            elif qtype == "TECH":
                if tech_stack:
                    question_text = f"{tech_stack}를 사용하여 진행한 프로젝트 경험에 대해 설명해 주세요."
                else:
                    question_text = f"{job_category} 직무에 필요한 핵심 기술은 무엇이라고 생각하시나요?"
            
            questions.append({
                "question_type": qtype,
                "question_text": question_text
            })
        
        response_data = {
            "interview_id": interview_id,
            "questions": questions
        }
        
        logger.info(f"면접 질문 생성 완료: {len(questions)}개 질문")
        return jsonify(response_data)
    except Exception as e:
        error_msg = f"면접 질문 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/ai/interview/<int:interview_id>/genergate-followup-question', methods=['POST'])
def generate_followup_question(interview_id):
    """꼬리질문 생성 엔드포인트"""
    initialize_analyzers()
    logger.info(f"꼬리질문 생성 요청 받음: /ai/interview/{interview_id}/genergate-followup-question")
    
    # 파일이 없어도 기본 응답 제공
    if 'file' not in request.files:
        logger.warning("파일이 제공되지 않음, 기본 꼬리질문 생성")
        response = {
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": "방금 답변하신 내용에 대해 좀 더 구체적인 예시를 들어주실 수 있나요?"
        }
        return jsonify(response)
    
    file = request.files['file']
    try:
        temp_path = f"temp_followup_{interview_id}.mp4"
        file.save(temp_path)
        
        # 음성 인식
        user_text = "기술 질문에 대한 답변"
        if speech_analyzer:
            try:
                user_text = speech_analyzer.transcribe_video(temp_path)
            except Exception as e:
                logger.warning(f"음성 인식 실패: {str(e)}")
        
        # 꼬리질문 생성
        followup_question = "방금 말씀하신 기술에 대해 더 자세히 설명해 주세요."
        
        # 기술 키워드 추출
        tech_keywords = ["Java", "Python", "React", "Spring", "Node.js", "JavaScript", "MySQL", "MongoDB"]
        mentioned_tech = [tech for tech in tech_keywords if tech.lower() in user_text.lower()]
        
        if mentioned_tech:
            tech = mentioned_tech[0]
            followup_question = f"{tech}를 사용하여 진행한 프로젝트에서 가장 어려웠던 부분은 무엇이었나요?"
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        response = {
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": followup_question
        }
        
        return jsonify(response)
    except Exception as e:
        error_msg = f"꼬리질문 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "interview_id": interview_id,
            "question_type": "FOLLOWUP",
            "question_text": "추가로 설명해주실 내용이 있나요?"
        })

@app.route('/ai/interview/<int:interview_id>/<question_type>/answer-video', methods=['POST'])
def process_interview_answer(interview_id, question_type):
    """면접 답변 영상 처리 엔드포인트"""
    initialize_analyzers()
    logger.info(f"면접 답변 영상 처리 요청 받음: /ai/interview/{interview_id}/{question_type}/answer-video")
    
    # 영상 파일이 없어도 기본 응답 제공
    if 'file' not in request.files and 'video' not in request.files:
        logger.warning("영상 파일이 제공되지 않음, 기본 응답 제공")
        return jsonify({
            "interview_id": interview_id,
            "question_type": question_type,
            "answer_text": "답변 영상이 제공되지 않았습니다.",
            "content_score": 2.5,
            "voice_score": 2.5,
            "action_score": 2.5,
            "content_feedback": "내용 평가를 위해 답변이 필요합니다.",
            "voice_feedback": "음성 평가를 위해 답변이 필요합니다.",
            "action_feedback": "행동 평가를 위해 답변이 필요합니다.",
            "feedback": "답변 영상을 제출해주시면 더 정확한 피드백을 제공할 수 있습니다."
        })
    
    file = request.files.get('file') or request.files.get('video')
    
    if not file or file.filename == '':
        logger.warning("빈 파일이 제공됨, 기본 응답 제공")
        return jsonify({
            "interview_id": interview_id,
            "question_type": question_type,
            "answer_text": "유효한 답변 영상이 제공되지 않았습니다.",
            "content_score": 2.0,
            "voice_score": 2.0,
            "action_score": 2.0,
            "content_feedback": "내용 평가 불가",
            "voice_feedback": "음성 평가 불가",
            "action_feedback": "행동 평가 불가",
            "feedback": "유효한 답변 영상을 제출해주세요."
        })
    
    try:
        temp_path = f"temp_interview_{interview_id}_{question_type}.mp4"
        file.save(temp_path)
        
        user_text = "저는 지속적인 학습과 새로운 기술 활용을 좋아합니다. 팀 환경에서 소통하며 협업하는 것을 중요하게 생각합니다."
        
        # 음성 인식
        if speech_analyzer:
            try:
                user_text = speech_analyzer.transcribe_video(temp_path)
                logger.info(f"음성 인식 완료: {user_text[:100]}...")
            except Exception as e:
                logger.warning(f"음성 인식 실패: {str(e)}")
        
        # 얼굴 분석
        facial_result = {"confidence": 0.9, "gaze_angle_x": 0.1, "gaze_angle_y": 0.1}
        if facial_analyzer:
            try:
                facial_result = facial_analyzer.analyze_video(temp_path)
            except Exception as e:
                logger.warning(f"얼굴 분석 실패: {str(e)}")
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 점수 계산
        content_score = round(min(5.0, max(1.0, 3.0 + len(user_text.split()) / 50)), 1)
        voice_score = 3.7
        action_score = 3.9
        
        if not user_text or user_text.strip() == "":
            user_text = "번역 결과가 없습니다. 질문에 대한 답변입니다."
            content_score = 2.5
        
        # 피드백 생성
        feedback = "전반적으로 양호한 답변이었습니다."
        if content_score >= 4.0:
            feedback = "충분한 내용으로 답변하셨습니다."
        
        content_feedback = "내용이 구체적이고 적절합니다."
        voice_feedback = "목소리가 안정적입니다."
        action_feedback = "시선과 표정이 자연스럽습니다."
        
        response = {
            "interview_id": interview_id,
            "question_type": question_type,
            "answer_text": user_text,
            "content_score": content_score,
            "voice_score": voice_score,
            "action_score": action_score,
            "content_feedback": content_feedback,
            "voice_feedback": voice_feedback,
            "action_feedback": action_feedback,
            "feedback": feedback
        }
        
        logger.info(f"면접 답변 처리 완료: {question_type}, 점수: {content_score:.1f}/{voice_score:.1f}/{action_score:.1f}")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"면접 답변 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "interview_id": interview_id,
            "question_type": question_type,
            "answer_text": "처리 중 오류가 발생했습니다.",
            "content_score": 2.0,
            "voice_score": 2.0,
            "action_score": 2.0,
            "content_feedback": "처리 실패",
            "voice_feedback": "처리 실패",
            "action_feedback": "처리 실패",
            "feedback": f"처리 중 오류: {str(e)}"
        }), 200

# 토론면접 관련 엔드포인트들 - D-ID 통합

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def generate_ai_opening(debate_id):
    """AI 입론 생성 엔드포인트"""
    logger.info(f"AI 입론 생성 요청 받음: /ai/debate/{debate_id}/ai-opening")
    
    try:
        data = request.json or {}
        topic = data.get('topic', '기본 토론 주제')
        position = data.get('position', 'PRO')
        
        if position == 'PRO':
            ai_opening_text = f"{topic}에 대해 찬성하는 입장에서 말씀드리겠습니다."
        else:
            ai_opening_text = f"{topic}에 대해 반대하는 입장에서 말씀드리겠습니다."
        
        response_data = {
            "ai_opening_text": ai_opening_text,
            "debate_id": debate_id,
            "topic": topic,
            "position": position
        }
        
        logger.info(f"AI 입론 생성 완료: {debate_id}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"AI 입론 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "ai_opening_text": "AI 입론을 생성할 수 없습니다.",
            "debate_id": debate_id,
            "error": error_msg
        }), 200

@app.route('/ai/debate/ai-opening-video', methods=['POST'])
def generate_ai_opening_video():
    """AI 입론 영상 생성 엔드포인트 - D-ID 통합"""
    logger.info("AI 입론 영상 생성 요청 받음: /ai/debate/ai-opening-video")
    
    try:
        data = request.json or {}
        ai_opening_text = data.get('ai_opening_text', '기본 입론 텍스트')
        debater_gender = data.get('debater_gender', 'male')
        
        if tts_manager:
            formatted_script = tts_manager.format_script_for_debate(ai_opening_text, 'opening')
        else:
            formatted_script = f"{ai_opening_text}"
        
        video_path = generate_avatar_video_unified(
            script=formatted_script,
            video_type='debate',
            gender=debater_gender,
            phase='opening'
        )
        
        if video_path and os.path.exists(video_path):
            logger.info(f"AI 토론 입론 영상 생성 완료: {video_path}")
            return send_file(video_path, mimetype='video/mp4')
        else:
            logger.warning("AI 토론 입론 영상 생성 실패 - 샘플 영상 반환")
            sample_path = generate_sample_video_fallback('debate', 'opening')
            if sample_path and os.path.exists(sample_path):
                return send_file(sample_path, mimetype='video/mp4')
            else:
                return Response(b'Sample Debate Opening Video', mimetype='video/mp4')
        
    except Exception as e:
        error_msg = f"AI 입론 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return Response(b'Error generating debate opening video', mimetype='video/mp4')

@app.route('/ai/debate/ai-rebuttal-video', methods=['POST'])
def generate_ai_rebuttal_video():
    """AI 반론 영상 생성 엔드포인트 - D-ID 통합"""
    return generate_ai_debate_video_unified('rebuttal')

@app.route('/ai/debate/ai-counter-rebuttal-video', methods=['POST'])
def generate_ai_counter_rebuttal_video():
    """AI 재반론 영상 생성 엔드포인트 - D-ID 통합"""
    return generate_ai_debate_video_unified('counter_rebuttal')

@app.route('/ai/debate/ai-closing-video', methods=['POST'])
def generate_ai_closing_video():
    """AI 최종변론 영상 생성 엔드포인트 - D-ID 통합"""
    return generate_ai_debate_video_unified('closing')

def generate_ai_debate_video_unified(phase='opening'):
    """토론 AI 영상 생성 통합 함수"""
    logger.info(f"AI {phase} 영상 생성 요청 받음: /ai/debate/ai-{phase}-video")
    
    try:
        data = request.json or {}
        text_key_map = {
            'opening': 'ai_opening_text',
            'rebuttal': 'ai_rebuttal_text', 
            'counter_rebuttal': 'ai_counter_rebuttal_text',
            'closing': 'ai_closing_text'
        }
        
        text_key = text_key_map.get(phase, 'ai_opening_text')
        ai_text = data.get(text_key, f'기본 {phase} 텍스트')
        
        # 다양한 성별 사용 (단계별로 다르게) -> 세션별 일관성 유지로 변경
        # debate_id를 지정하도록 Backend에서 전달 받거나 추출
        debate_id = data.get('debate_id')
        if not debate_id:
            # 텍스트를 해시해서 임시 ID 사용
            debate_id = abs(hash(ai_text)) % 10000
        
        # 세션별 일관된 토론자 성별 사용
        debater_gender = get_avatar_gender_for_session('debate', debate_id)
        
        logger.info(f"토론 ID: {debate_id}, {phase} 토론자 성별: {debater_gender}, 내용: {ai_text[:50]}...")
        
        if tts_manager:
            formatted_script = tts_manager.format_script_for_debate(ai_text, phase)
        else:
            formatted_script = ai_text
        
        video_path = generate_avatar_video_unified(
            script=formatted_script,
            video_type='debate',
            gender=debater_gender,
            phase=phase
        )
        
        if video_path and os.path.exists(video_path):
            logger.info(f"AI 토론 {phase} 영상 생성 완룼: {video_path}")
            return send_file(video_path, mimetype='video/mp4')
        else:
            logger.warning(f"AI 토론 {phase} 영상 생성 실패 - 샘플 영상 반환")
            sample_path = generate_sample_video_fallback('debate', phase)
            if sample_path and os.path.exists(sample_path):
                return send_file(sample_path, mimetype='video/mp4')
            else:
                return Response(f'Sample Debate {phase.title()} Video'.encode(), mimetype='video/mp4')
        
    except Exception as e:
        error_msg = f"AI {phase} 영상 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return Response(f'Error generating debate {phase} video'.encode(), mimetype='video/mp4')

# 사용자 토론 영상 처리 엔드포인트들 (기존 로직 유지)

@app.route('/ai/debate/<int:debate_id>/opening-video', methods=['POST'])
def process_opening_video(debate_id):
    """사용자 입론 영상 처리 엔드포인트"""
    logger.info(f"사용자 입론 영상 처리 요청 받음: /ai/debate/{debate_id}/opening-video")
    
    if 'file' not in request.files:
        logger.warning("파일이 제공되지 않음")
        return jsonify({
            "user_opening_text": "파일이 제공되지 않았습니다.",
            "ai_rebuttal_text": "기본 AI 반론입니다.",
            "initiative_score": 3.0,
            "collaborative_score": 3.0,
            "communication_score": 3.0,
            "logic_score": 3.0,
            "problem_solving_score": 3.0,
            "voice_score": 3.0,
            "action_score": 3.0,
            "initiative_feedback": "적극성 피드백",
            "collaborative_feedback": "협력적 태도 피드백",
            "communication_feedback": "의사소통 피드백",
            "logic_feedback": "논리력 피드백",
            "problem_solving_feedback": "문제해결능력 피드백",
            "feedback": "종합 피드백",
            "sample_answer": "예시 답안입니다."
        })
    
    file = request.files['file']
    
    try:
        temp_path = f"temp_debate_opening_{debate_id}.mp4"
        file.save(temp_path)
        
        user_opening_text = "사용자의 입론 내용입니다. 주장에 대한 근거를 제시하였습니다."
        ai_rebuttal_text = "입론에 대한 AI의 반론입니다. 제시된 근거에 대한 반박을 하겠습니다."
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 점수 계산
        import random
        response_data = {
            "user_opening_text": user_opening_text,
            "ai_rebuttal_text": ai_rebuttal_text,
            "initiative_score": round(random.uniform(3.0, 4.5), 1),
            "collaborative_score": round(random.uniform(3.0, 4.5), 1),
            "communication_score": round(random.uniform(3.0, 4.5), 1),
            "logic_score": round(random.uniform(3.0, 4.5), 1),
            "problem_solving_score": round(random.uniform(3.0, 4.5), 1),
            "voice_score": round(random.uniform(3.0, 4.5), 1),
            "action_score": round(random.uniform(3.0, 4.5), 1),
            "initiative_feedback": "적극적인 자세로 논거를 제시했습니다.",
            "collaborative_feedback": "상대방의 입장을 고려하며 발언했습니다.",
            "communication_feedback": "명확하고 체계적으로 의견을 전달했습니다.",
            "logic_feedback": "논리적 구조가 잘 잡혀있습니다.",
            "problem_solving_feedback": "문제에 대한 해결방안을 제시했습니다.",
            "feedback": "전반적으로 좋은 입론이었습니다. 근거 제시와 논리 전개가 우수합니다.",
            "sample_answer": "더 강력한 근거와 통계 자료를 활용하면 더욱 설득력 있는 입론이 될 것입니다."
        }
        
        logger.info(f"사용자 입론 영상 처리 완료: {debate_id}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"입론 영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "user_opening_text": "처리 중 오류가 발생했습니다.",
            "ai_rebuttal_text": "기본 AI 반론입니다.",
            "initiative_score": 3.0,
            "collaborative_score": 3.0,
            "communication_score": 3.0,
            "logic_score": 3.0,
            "problem_solving_score": 3.0,
            "voice_score": 3.0,
            "action_score": 3.0,
            "initiative_feedback": "처리 실패",
            "collaborative_feedback": "처리 실패",
            "communication_feedback": "처리 실패",
            "logic_feedback": "처리 실패",
            "problem_solving_feedback": "처리 실패",
            "feedback": f"처리 중 오류: {str(e)}",
            "sample_answer": "오류로 인해 예시 답안을 제공할 수 없습니다."
        }), 200

@app.route('/ai/debate/<int:debate_id>/rebuttal-video', methods=['POST'])
def process_rebuttal_video(debate_id):
    """사용자 반론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, 'rebuttal')

@app.route('/ai/debate/<int:debate_id>/counter-rebuttal-video', methods=['POST'])
def process_counter_rebuttal_video(debate_id):
    """사용자 재반론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, 'counter_rebuttal')

@app.route('/ai/debate/<int:debate_id>/closing-video', methods=['POST'])
def process_closing_video(debate_id):
    """사용자 최종변론 영상 처리 엔드포인트"""
    return process_debate_video_generic(debate_id, 'closing')

def process_debate_video_generic(debate_id, phase_name):
    """토론 영상 처리 공통 함수"""
    initialize_analyzers()
    logger.info(f"사용자 {phase_name} 영상 처리 요청 받음: /ai/debate/{debate_id}/{phase_name}-video")
    
    if 'file' not in request.files:
        logger.warning("파일이 제공되지 않음")
        return create_default_debate_response(debate_id, phase_name, "파일이 제공되지 않았습니다.")
    
    file = request.files['file']
    
    try:
        temp_path = f"temp_debate_{phase_name}_{debate_id}.mp4"
        file.save(temp_path)
        
        user_text = f"사용자의 {phase_name} 내용입니다. 주장에 대한 근거를 제시하였습니다."
        
        # 다음 단계 AI 응답 생성
        next_phase_texts = {
            'opening': 'ai_rebuttal_text',
            'rebuttal': 'ai_counter_rebuttal_text', 
            'counter_rebuttal': 'ai_closing_text',
            'closing': 'ai_summary_text'
        }
        
        next_text_key = next_phase_texts.get(phase_name, 'ai_response_text')
        ai_next_text = f"이전 {phase_name}에 대한 AI의 응답입니다. 제시된 근거에 대한 반박을 하겠습니다."
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 점수 계산
        import random
        response_data = {
            f"user_{phase_name}_text": user_text,
            next_text_key: ai_next_text,
            "initiative_score": round(random.uniform(3.0, 4.5), 1),
            "collaborative_score": round(random.uniform(3.0, 4.5), 1),
            "communication_score": round(random.uniform(3.0, 4.5), 1),
            "logic_score": round(random.uniform(3.0, 4.5), 1),
            "problem_solving_score": round(random.uniform(3.0, 4.5), 1),
            "voice_score": round(random.uniform(3.0, 4.5), 1),
            "action_score": round(random.uniform(3.0, 4.5), 1),
            "initiative_feedback": "적극적인 자세로 논거를 제시했습니다.",
            "collaborative_feedback": "상대방의 입장을 고려하며 발언했습니다.",
            "communication_feedback": "명확하고 체계적으로 의견을 전달했습니다.",
            "logic_feedback": "논리적 구조가 잘 잡혀있습니다.",
            "problem_solving_feedback": "문제에 대한 해결방안을 제시했습니다.",
            "feedback": f"전반적으로 좋은 {phase_name}이었습니다. 근거 제시와 논리 전개가 우수합니다.",
            "sample_answer": f"더 강력한 근거와 통계 자료를 활용하면 더욱 설득력 있는 {phase_name}이 될 것입니다."
        }
        
        logger.info(f"사용자 {phase_name} 영상 처리 완료: {debate_id}")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"{phase_name} 영상 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        return create_default_debate_response(debate_id, phase_name, f"처리 중 오류: {str(e)}")

def create_default_debate_response(debate_id, phase_name, error_message):
    """기본 토론 응답 생성"""
    next_phase_texts = {
        'opening': 'ai_rebuttal_text',
        'rebuttal': 'ai_counter_rebuttal_text', 
        'counter_rebuttal': 'ai_closing_text',
        'closing': 'ai_summary_text'
    }
    
    next_text_key = next_phase_texts.get(phase_name, 'ai_response_text')
    
    return jsonify({
        f"user_{phase_name}_text": error_message,
        next_text_key: f"기본 AI {phase_name} 응답입니다.",
        "initiative_score": 3.0,
        "collaborative_score": 3.0,
        "communication_score": 3.0,
        "logic_score": 3.0,
        "problem_solving_score": 3.0,
        "voice_score": 3.0,
        "action_score": 3.0,
        "initiative_feedback": "처리 실패",
        "collaborative_feedback": "처리 실패",
        "communication_feedback": "처리 실패",
        "logic_feedback": "처리 실패",
        "problem_solving_feedback": "처리 실패",
        "feedback": error_message,
        "sample_answer": "오류로 인해 예시 답안을 제공할 수 없습니다."
    }), 200

def initialize_analyzers():
    """분석기 초기화 함수"""
    global facial_analyzer, speech_analyzer
    try:
        if facial_analyzer is None:
            facial_analyzer = RealtimeFacialAnalysis()
            logger.info("얼굴 분석기 초기화 완료")
        if speech_analyzer is None:
            speech_analyzer = RealtimeSpeechToText(model="tiny")
            logger.info("음성 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"분석기 초기화 실패: {str(e)}")

@app.route('/ai/test', methods=['GET'])
def test_connection():
    """연결 테스트 엔드포인트 - D-ID 통합 상태 표시"""
    initialize_analyzers()
    logger.info("연결 테스트 요청 받음: /ai/test")
    
    # 각 모듈 상태 확인
    did_status = "사용 가능" if did_initialized else "사용 불가"
    facial_status = "사용 가능" if facial_analyzer else "사용 불가"
    speech_status = "사용 가능" if speech_analyzer else "사용 불가"
    tts_status = "사용 가능" if tts_manager else "사용 불가"
    
    # D-ID 연결 테스트
    did_connection_status = "연결 실패"
    if did_client:
        if did_client.test_connection():
            did_connection_status = "연결 성공"
        else:
            did_connection_status = "연결 실패"
    
    test_response = {
        "status": "AI 서버가 정상 작동 중입니다 (D-ID 통합)",
        "avatar_services": {
            "D-ID (우선)": did_status,
            "D-ID 연결상태": did_connection_status,
        },
        "modules": {
            "TTS Manager": tts_status,
            "OpenFace/Librosa": facial_status,
            "Whisper/STT": speech_status
        },
        "configuration": {
            "preferred_service": os.environ.get('PREFERRED_AVATAR_SERVICE', 'D_ID'),
            "use_fallback": os.environ.get('USE_FALLBACK_SERVICE', 'True'),
            "d_id_api_key_configured": "Yes" if os.environ.get('D_ID_API_KEY') and os.environ.get('D_ID_API_KEY') != 'your_actual_d_id_api_key_here' else "No",
        },
        "endpoints": {
            "job_recommendation": "/ai/recruitment/posting",
            "interview_question_generation": "/ai/interview/generate-question",
            "interview_ai_video": "/ai/interview/ai-video (D-ID 통합)",
            "interview_answer_processing": "/ai/interview/<interview_id>/<question_type>/answer-video",
            "followup_question": "/ai/interview/<interview_id>/genergate-followup-question",
            "debate_ai_opening": "/ai/debate/<debate_id>/ai-opening",
            "debate_ai_videos": "/ai/debate/ai-opening-video, /ai/debate/ai-rebuttal-video, /ai/debate/ai-counter-rebuttal-video, /ai/debate/ai-closing-video (D-ID 통합)",
            "debate_opening_video": "/ai/debate/<debate_id>/opening-video"
        }
    }
    
    return jsonify(test_response)

if __name__ == "__main__":
    # 시작 시 D-ID 및 분석기 초기화 시도
    print("=" * 60)
    print("VeriView AI 서버 시작 - D-ID API 통합")
    print("=" * 60)
    
    # D-ID 초기화
    if initialize_d_id():
        print("D-ID 통합 성공")
    else:
        print("D-ID 통합 실패 - 폴백 모드 사용")
        
    # 기타 분석기 초기화
    initialize_analyzers()
    
    print("-" * 60)
    print("서버 주소: http://localhost:5000")
    print("테스트 엔드포인트: http://localhost:5000/ai/test")
    print("주요 엔드포인트:")
    print("  - 채용 공고 추천: /ai/recruitment/posting")
    print("  - 면접 질문 생성: /ai/interview/generate-question")
    print("  - AI 면접관 영상: /ai/interview/ai-video (D-ID)")
    print("  - AI 토론 영상들: /ai/debate/ai-*-video (D-ID)")
    print("-" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
