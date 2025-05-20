from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ai/test', methods=['GET'])
def test_connection():
    return jsonify({"status": "AI 서버가 정상 작동 중입니다."})

@app.route('/ai/debate/<int:debate_id>/ai-opening', methods=['POST'])
def ai_opening(debate_id):
    try:
        # 요청 데이터 로깅
        print(f"요청 받음: /ai/debate/{debate_id}/ai-opening")
        print(f"요청 데이터: {request.json}")
        
        # 고정된 AI 입론 응답
        ai_response = "인공지능은 인간의 일자리를 대체하는 위험을 내포하고 있습니다."
        
        response_data = {
            "ai_opening_text": ai_response
        }
        print(f"응답 데이터: {response_data}")
        
        return jsonify(response_data)
    except Exception as e:
        error_msg = f"AI 입론 생성 중 오류 발생: {str(e)}"
        print(f"오류: {error_msg}")
        return jsonify({"error": error_msg}), 500

if __name__ == "__main__":
    print("AI 서버 Flask 애플리케이션 시작...")
    print("서버 주소: http://localhost:5000")
    print("테스트 엔드포인트: http://localhost:5000/ai/test")
    print("API 엔드포인트: http://localhost:5000/ai/debate/<debate_id>/ai-opening")
    print("-" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)