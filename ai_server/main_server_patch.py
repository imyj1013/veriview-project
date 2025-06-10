# main_server.py에 추가할 D-ID 통합 코드

# 1. 맨 위에 D-ID 모듈 import 추가
try:
    from modules.d_id.client import DIDClient
    from modules.d_id.video_manager import VideoManager
    D_ID_AVAILABLE = True
    print("✅ D-ID 모듈 로드 성공: AI 아바타 영상 생성 기능 사용 가능")
except ImportError as e:
    print(f"❌ D-ID 모듈 로드 실패: {e}")
    D_ID_AVAILABLE = False

# 2. 전역 변수에 D-ID 관련 변수 추가
d_id_client = None
d_id_video_manager = None

# 3. D-ID 초기화 함수 추가
def initialize_d_id():
    """D-ID 모듈 초기화"""
    global d_id_client, d_id_video_manager
    
    if not D_ID_AVAILABLE:
        logger.warning("D-ID 모듈이 사용 불가합니다")
        return False
    
    try:
        # 환경 변수에서 API 키 가져오기
        api_key = os.environ.get('D_ID_API_KEY')
        
        if not api_key or api_key == 'your_actual_d_id_api_key_here':
            logger.warning("D_ID_API_KEY가 설정되지 않음")
            return False
        
        # D-ID 클라이언트 초기화
        base_url = os.environ.get('D_ID_API_URL', 'https://api.d-id.com')
        d_id_client = DIDClient(api_key=api_key, base_url=base_url)
        logger.info("D-ID 클라이언트 초기화 완료")
        
        # 연결 테스트
        if d_id_client.test_connection():
            logger.info("D-ID API 연결 성공")
        else:
            logger.warning("D-ID API 연결 실패")
            return False
        
        # D-ID 영상 관리자 초기화
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
        d_id_video_manager = VideoManager(base_dir=videos_dir)
        logger.info(f"D-ID 영상 관리자 초기화 완료: {videos_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"D-ID 모듈 초기화 실패: {str(e)}")
        return False

# 4. initialize_ai_systems() 함수에 D-ID 초기화 추가
def initialize_ai_systems():
    # 기존 코드 유지...
    
    # D-ID 모듈 초기화 (새로 추가)
    if D_ID_AVAILABLE:
        if initialize_d_id():
            logger.info("✅ D-ID 모듈 초기화 완료")
        else:
            logger.warning("⚠️ D-ID 모듈 초기화 실패")

# 5. 새로운 D-ID 영상 생성 엔드포인트 추가

@app.route('/ai/debate/ai-opening-video', methods=['POST'])
def generate_ai_opening_video():
    """AI 입론 영상 생성 엔드포인트 - D-ID TTS 사용"""
    logger.info("AI 입론 영상 생성 요청: /ai/debate/ai-opening-video")
    
    try:
        data = request.json or {}
        ai_opening_text = data.get('ai_opening_text', '')
        debate_id = data.get('debate_id', int(time.time()))
        topic = data.get('topic', '인공지능')
        position = data.get('position', 'CON')
        
        # 텍스트가 없으면 기본 생성
        if not ai_opening_text:
            if position == 'PRO':
                ai_opening_text = f"'{topic}'에 대해 찬성하는 입장에서 말씀드리겠습니다."
            else:
                ai_opening_text = f"'{topic}'에 대해 반대하는 입장에서 말씀드리겠습니다. 이 주제의 문제점들을 지적하고자 합니다."
        
        logger.info(f"입론 텍스트: {ai_opening_text[:100]}...")
        
        # D-ID 클라이언트로 영상 생성
        if d_id_client:
            try:
                # 토론자 성별 설정 (찬성: 남성, 반대: 여성)
                debater_gender = 'male' if position == 'PRO' else 'female'
                
                video_path = d_id_client.generate_debate_video(
                    debate_text=ai_opening_text,
                    debater_gender=debater_gender,
                    debate_phase='opening'
                )
                
                if video_path and os.path.exists(video_path):
                    logger.info(f"D-ID 입론 영상 생성 성공: {video_path}")
                    
                    # 파일 크기 확인
                    file_size = os.path.getsize(video_path)
                    logger.info(f"생성된 영상 크기: {file_size} bytes")
                    
                    if file_size > 0:
                        return send_file(
                            video_path,
                            mimetype='video/mp4',
                            as_attachment=False,
                            download_name=f'ai_opening_{debate_id}.mp4'
                        )
                    else:
                        logger.error("생성된 영상 파일 크기가 0입니다")
                else:
                    logger.error("D-ID 영상 생성 실패")
                    
            except Exception as e:
                logger.error(f"D-ID 영상 생성 중 오류: {str(e)}")
        
        # 폴백: 에러 응답
        logger.warning("D-ID 사용 불가, 에러 응답 반환")
        return jsonify({
            "error": "D-ID 영상 생성 실패",
            "message": "TTS 서비스에 문제가 있습니다",
            "fallback_text": ai_opening_text
        }), 500
        
    except Exception as e:
        logger.error(f"AI 입론 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"영상 생성 실패: {str(e)}"}), 500

@app.route('/ai/debate/ai-rebuttal-video', methods=['POST'])
def generate_ai_rebuttal_video():
    """AI 반론 영상 생성"""
    return generate_ai_debate_video_generic('rebuttal')

@app.route('/ai/debate/ai-counter-rebuttal-video', methods=['POST'])
def generate_ai_counter_rebuttal_video():
    """AI 재반론 영상 생성"""
    return generate_ai_debate_video_generic('counter_rebuttal')

@app.route('/ai/debate/ai-closing-video', methods=['POST'])
def generate_ai_closing_video():
    """AI 최종 변론 영상 생성"""
    return generate_ai_debate_video_generic('closing')

def generate_ai_debate_video_generic(phase: str):
    """AI 토론 영상 생성 공통 함수"""
    logger.info(f"AI {phase} 영상 생성 요청")
    
    try:
        data = request.json or {}
        
        # 텍스트 키 매핑
        text_keys = {
            'rebuttal': 'ai_rebuttal_text',
            'counter_rebuttal': 'ai_counter_rebuttal_text', 
            'closing': 'ai_closing_text'
        }
        
        text_key = text_keys.get(phase, f'ai_{phase}_text')
        debate_text = data.get(text_key, '')
        debate_id = data.get('debate_id', int(time.time()))
        position = data.get('position', 'CON')
        
        # 기본 텍스트 생성
        if not debate_text:
            topic = data.get('topic', '인공지능')
            if phase == 'rebuttal':
                debate_text = f"상대측의 주장을 들었지만, {topic}에 대한 제 입장은 여전히 유효합니다."
            elif phase == 'counter_rebuttal':
                debate_text = f"추가로 말씀드리면, {topic}에 대해 더 깊이 고려해야 할 점들이 있습니다."
            elif phase == 'closing':
                debate_text = f"결론적으로 {topic}에 대한 제 입장을 정리하면 다음과 같습니다."
        
        # D-ID로 영상 생성
        if d_id_client:
            try:
                debater_gender = 'male' if position == 'PRO' else 'female'
                
                video_path = d_id_client.generate_debate_video(
                    debate_text=debate_text,
                    debater_gender=debater_gender,
                    debate_phase=phase
                )
                
                if video_path and os.path.exists(video_path):
                    logger.info(f"D-ID {phase} 영상 생성 성공: {video_path}")
                    return send_file(
                        video_path,
                        mimetype='video/mp4',
                        as_attachment=False,
                        download_name=f'ai_{phase}_{debate_id}.mp4'
                    )
                    
            except Exception as e:
                logger.error(f"D-ID {phase} 영상 생성 중 오류: {str(e)}")
        
        # 폴백
        return jsonify({
            "error": f"D-ID {phase} 영상 생성 실패",
            "fallback_text": debate_text
        }), 500
        
    except Exception as e:
        logger.error(f"{phase} 영상 생성 중 오류: {str(e)}")
        return jsonify({"error": f"{phase} 영상 생성 실패: {str(e)}"}), 500

# 6. 메인 실행 부분 수정
if __name__ == "__main__":
    # 시작 시 AI 시스템 초기화
    initialize_ai_systems()

    # AIStudios 라우트 통합
    setup_aistudios_integration()
    
    # 서버 시작 메시지에 D-ID 정보 추가
    print("🚀 VeriView AI 메인 서버 (D-ID + AIStudios 통합) 시작...")
    # ... 기존 출력 메시지들 ...
    
    if D_ID_AVAILABLE:
        print("🎬 D-ID 기능:")
        print("  - AI 아바타 영상 생성 (자체 TTS)")
        print("  - 토론 입론/반론/재반론/최종변론 영상")
        
        api_key_status = "✅ 설정됨" if os.environ.get('D_ID_API_KEY') else "❌ 미설정"
        print(f"  - API 키 상태: {api_key_status}")
        
        if d_id_client and d_id_client.test_connection():
            print("  - 연결 상태: ✅ 정상")
        else:
            print("  - 연결 상태: ❌ 실패")
        
        print("=" * 80)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
