from flask import Blueprint, request, jsonify
import sys
import os
import random
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/generate-question', methods=['POST'])
def generate_interview_question():
    """인터뷰 질문 생성 API"""
    try:
        data = request.json
        job_category = data.get('job_category', '')
        tech_stack = data.get('tech_stack', '')
        education = data.get('education', '')
        personality = data.get('personality', '')
        workexperience = data.get('workexperience', '')
        experience_description = data.get('experience_description', '')
        
        logger.info(f"인터뷰 질문 생성 요청 받음: {job_category}, {tech_stack}")
        
        # 카테고리별 질문 생성
        common_questions = [
            "자기소개를 해주세요.",
            "지원자의 주요 강점과 약점에 대해 말씀해주세요.",
            "5년 후 자신의 모습을 어떻게 그리고 있나요?",
            "왜 저희 회사/포지션에 지원하셨나요?",
            "팀에서 갈등 상황이 발생했을 때 어떻게 대처하시나요?"
        ]
        
        # 직무 관련 질문
        job_questions = []
        if job_category == 'RND':
            job_questions = [
                "최근에 진행한 프로젝트에서 마주친 가장 큰 기술적 도전은 무엇이었고, 어떻게 해결했나요?",
                "신기술 학습에 대한 접근 방식은 어떠한가요?",
                "팀원들과 기술적 의견 충돌이 있을 때 어떻게 합의점을 찾나요?"
            ]
        elif job_category == 'ICT':
            job_questions = [
                "클라우드 환경에서의 개발 경험이 있으신가요?",
                "대규모 시스템 아키텍처를 설계해 본 경험이 있으신가요?",
                "데이터 보안에 관한 경험이나 지식이 있으신가요?"
            ]
        else:
            job_questions = [
                "관련 업무 경험에 대해 설명해주세요.",
                "이 분야에서 성공하기 위한 핵심 역량은 무엇이라고 생각하시나요?",
                "관련 분야의 최신 트렌드에 대해 어떻게 생각하시나요?"
            ]
        
        # 기술 스택 관련 질문
        tech_questions = []
        if tech_stack and '파이썬' in tech_stack:
            tech_questions = [
                "파이썬에서 메모리 관리는 어떻게 이루어지나요?",
                "파이썬의 GIL(Global Interpreter Lock)에 대해 설명해주세요.",
                "파이썬에서 비동기 프로그래밍을 구현하는 방법에 대해 설명해주세요."
            ]
        elif tech_stack and '자바' in tech_stack:
            tech_questions = [
                "자바의 가비지 컬렉션에 대해 설명해주세요.",
                "자바에서 스레드 관리는 어떻게 하나요?",
                "자바의 인터페이스와 추상 클래스의 차이점은 무엇인가요?"
            ]
        else:
            tech_questions = [
                "주로 사용하는 기술 스택에 대해 설명해주세요.",
                "새로운 기술을 배울 때 어떤 접근 방식을 사용하시나요?",
                "이전 프로젝트에서 어떤 기술적 문제를 해결했나요?"
            ]
        
        # 질문 선택
        selected_common = random.sample(common_questions, min(2, len(common_questions)))
        selected_job = random.sample(job_questions, min(2, len(job_questions)))
        selected_tech = random.sample(tech_questions, min(1, len(tech_questions)))
        
        all_questions = []
        
        # COMMON 유형 질문
        for q in selected_common:
            all_questions.append({
                "question_text": q,
                "question_type": "COMMON"
            })
        
        # JOB 유형 질문
        for q in selected_job:
            all_questions.append({
                "question_text": q,
                "question_type": "JOB"
            })
        
        # TECH 유형 질문
        for q in selected_tech:
            all_questions.append({
                "question_text": q,
                "question_type": "TECH"
            })
        
        logger.info(f"생성된 질문 수: {len(all_questions)}")
        
        # 질문이 없는 경우 기본 질문 제공
        if not all_questions:
            all_questions = [
                {"question_text": "자기소개를 해주세요.", "question_type": "COMMON"},
                {"question_text": "지원자의 주요 강점과 약점에 대해 말씀해주세요.", "question_type": "COMMON"},
                {"question_text": "왜 저희 회사/포지션에 지원하셨나요?", "question_type": "JOB"},
                {"question_text": "주로 사용하는 기술 스택에 대해 설명해주세요.", "question_type": "TECH"},
                {"question_text": "5년 후 자신의 모습을 어떻게 그리고 있나요?", "question_type": "COMMON"}
            ]
        
        return jsonify({"questions": all_questions})
        
    except Exception as e:
        logger.error(f"인터뷰 질문 생성 오류: {str(e)}")
        # 오류 발생 시에도 기본 질문 제공
        default_questions = [
            {"question_text": "자기소개를 해주세요.", "question_type": "COMMON"},
            {"question_text": "지원자의 주요 강점과 약점에 대해 말씀해주세요.", "question_type": "COMMON"},
            {"question_text": "왜 저희 회사/포지션에 지원하셨나요?", "question_type": "JOB"},
            {"question_text": "주로 사용하는 기술 스택에 대해 설명해주세요.", "question_type": "TECH"},
            {"question_text": "5년 후 자신의 모습을 어떻게 그리고 있나요?", "question_type": "COMMON"}
        ]
        return jsonify({"questions": default_questions})
