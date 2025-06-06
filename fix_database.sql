-- VeriView 데이터베이스 수정 스크립트
USE veriview_db;

-- 1. 기존 NULL 질문들을 실제 질문으로 업데이트
UPDATE interview_question SET question_text = '자기소개를 해주세요.' WHERE question_type = 'INTRO' AND question_text IS NULL;
UPDATE interview_question SET question_text = '이 직무에 지원한 이유는 무엇인가요?' WHERE question_type = 'FIT' AND question_text IS NULL;
UPDATE interview_question SET question_text = '본인의 성격과 장단점에 대해 말씀해주세요.' WHERE question_type = 'PERSONALITY' AND question_text IS NULL;
UPDATE interview_question SET question_text = '보유하고 있는 기술 스택에 대해 설명해주세요.' WHERE question_type = 'TECH' AND question_text IS NULL;
UPDATE interview_question SET question_text = '앞서 답변한 내용에 대해 더 자세히 설명해주시겠어요?' WHERE question_type = 'FOLLOWUP' AND question_text IS NULL;

-- 2. 면접 답변 테이블이 없다면 생성 (피드백을 위해 필요)
CREATE TABLE IF NOT EXISTS interview_answer (
    answer_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    interview_question_id BIGINT NOT NULL,
    answer_text TEXT,
    content_score DECIMAL(3,1) DEFAULT 0.0,
    voice_score DECIMAL(3,1) DEFAULT 0.0,
    action_score DECIMAL(3,1) DEFAULT 0.0,
    content_feedback TEXT,
    voice_feedback TEXT,
    action_feedback TEXT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_question_id) REFERENCES interview_question(interview_question_id)
);

-- 3. 테스트용 답변 데이터 삽입 (interview_id = 1에 대해)
INSERT INTO interview_answer (interview_question_id, answer_text, content_score, voice_score, action_score, content_feedback, voice_feedback, action_feedback, feedback)
SELECT 
    iq.interview_question_id,
    '안녕하세요. 저는 열정적이고 성실한 지원자입니다.' as answer_text,
    4.1 as content_score,
    4.3 as voice_score, 
    3.7 as action_score,
    '내용이 구체적이고 좋습니다.' as content_feedback,
    '목소리가 안정적입니다.' as voice_feedback,
    '시선과 자세가 자연스럽습니다.' as action_feedback,
    '전반적으로 좋은 답변이었습니다.' as feedback
FROM interview_question iq 
WHERE iq.interview_id = 1 
AND NOT EXISTS (
    SELECT 1 FROM interview_answer ia 
    WHERE ia.interview_question_id = iq.interview_question_id
);

-- 4. 데이터 확인
SELECT '=== 수정된 질문 확인 ===' as info;
SELECT interview_question_id, question_type, question_text, interview_id 
FROM interview_question 
WHERE interview_id IN (1, 2, 3, 4) 
ORDER BY interview_id, interview_question_id;

SELECT '=== 답변 데이터 확인 ===' as info;
SELECT COUNT(*) as answer_count FROM interview_answer;

SELECT '=== 면접 데이터 확인 ===' as info;
SELECT interview_id, job_category, workexperience, education FROM interview LIMIT 5;
