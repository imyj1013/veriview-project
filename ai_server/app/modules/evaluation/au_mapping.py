"""
OpenFace Action Unit (AU) 매핑 및 감정/태도 분석 모듈
Ekman의 FACS(Facial Action Coding System) 기반
"""

# Action Unit 정의 및 의미
AU_DEFINITIONS = {
    # 상부 얼굴
    "AU01": "Inner Brow Raiser (눈썹 안쪽 올리기) - 놀람, 관심",
    "AU02": "Outer Brow Raiser (눈썹 바깥쪽 올리기) - 놀람, 의문",
    "AU04": "Brow Lowerer (눈썹 내리기) - 집중, 화남",
    "AU05": "Upper Lid Raiser (윗눈꺼풀 올리기) - 놀람, 주의",
    "AU06": "Cheek Raiser (뺨 올리기) - 진정한 미소",
    "AU07": "Lid Tightener (눈꺼풀 조이기) - 의심, 집중",
    
    # 중부 얼굴
    "AU09": "Nose Wrinkler (코 주름) - 혐오",
    "AU10": "Upper Lip Raiser (윗입술 올리기) - 혐오, 경멸",
    "AU12": "Lip Corner Puller (입꼬리 올리기) - 미소",
    "AU14": "Dimpler (보조개) - 경멸, 의심",
    
    # 하부 얼굴
    "AU15": "Lip Corner Depressor (입꼬리 내리기) - 슬픔, 실망",
    "AU17": "Chin Raiser (턱 올리기) - 의심, 생각",
    "AU20": "Lip Stretcher (입술 늘리기) - 두려움",
    "AU23": "Lip Tightener (입술 조이기) - 화남, 결단",
    "AU25": "Lips Part (입술 벌리기) - 놀람, 말하기",
    "AU26": "Jaw Drop (턱 내리기) - 놀람, 충격",
    "AU28": "Lip Suck (입술 빨기) - 불안, 고민"
}

# 감정별 AU 조합
EMOTION_AU_PATTERNS = {
    "genuine_smile": {
        "required": ["AU06", "AU12"],
        "optional": ["AU25"],
        "name": "진정한 미소",
        "score_weight": 1.5
    },
    "polite_smile": {
        "required": ["AU12"],
        "optional": ["AU25"],
        "name": "사회적 미소",
        "score_weight": 1.0
    },
    "concentration": {
        "required": ["AU04"],
        "optional": ["AU07", "AU23"],
        "name": "집중",
        "score_weight": 1.2
    },
    "interest": {
        "required": ["AU01", "AU05"],
        "optional": ["AU02"],
        "name": "관심/호기심",
        "score_weight": 1.3
    },
    "confusion": {
        "required": ["AU04", "AU07"],
        "optional": ["AU09", "AU17"],
        "name": "혼란/의문",
        "score_weight": 0.8
    },
    "stress": {
        "required": ["AU07", "AU23"],
        "optional": ["AU04", "AU17"],
        "name": "스트레스/긴장",
        "score_weight": 0.7
    }
}

# 평가 항목별 관련 AU
EVALUATION_AU_MAPPING = {
    "initiative": {
        "positive": ["AU01", "AU02", "AU05", "AU12", "AU25"],
        "negative": ["AU15", "AU28"],
        "description": "적극성 관련 표정"
    },
    "collaborative": {
        "positive": ["AU06", "AU12"],
        "negative": ["AU09", "AU10", "AU14"],
        "description": "협력적 태도 관련 표정"
    },
    "confidence": {
        "positive": ["AU12", "AU23", "AU25"],
        "negative": ["AU04", "AU07", "AU15", "AU17", "AU28"],
        "description": "자신감 관련 표정"
    },
    "engagement": {
        "positive": ["AU01", "AU02", "AU05", "AU06", "AU12"],
        "negative": ["AU07", "AU09"],
        "description": "참여도 관련 표정"
    }
}

def analyze_au_patterns(au_data):
    """AU 데이터에서 감정 패턴 분석"""
    detected_emotions = []
    
    for emotion, pattern in EMOTION_AU_PATTERNS.items():
        # 필수 AU 확인
        required_match = all(
            au_data.get(f"{au}_r", 0) > 0.5 
            for au in pattern["required"]
        )
        
        # 선택적 AU 확인
        optional_match = any(
            au_data.get(f"{au}_r", 0) > 0.5 
            for au in pattern.get("optional", [])
        )
        
        if required_match:
            confidence = 1.0 if optional_match else 0.8
            detected_emotions.append({
                "emotion": emotion,
                "name": pattern["name"],
                "confidence": confidence,
                "weight": pattern["score_weight"]
            })
    
    return detected_emotions

def calculate_evaluation_scores_from_au(au_data):
    """AU 데이터로부터 평가 점수 계산"""
    scores = {}
    
    for eval_item, mapping in EVALUATION_AU_MAPPING.items():
        positive_score = sum(
            au_data.get(f"{au}_r", 0) 
            for au in mapping["positive"]
        ) / len(mapping["positive"])
        
        negative_score = sum(
            au_data.get(f"{au}_r", 0) 
            for au in mapping["negative"]
        ) / len(mapping["negative"]) if mapping["negative"] else 0
        
        # 긍정적 AU는 더하고, 부정적 AU는 빼기
        final_score = max(0, min(1, positive_score - negative_score))
        scores[eval_item] = final_score
    
    return scores

def get_au_feedback(au_data):
    """AU 분석 기반 구체적 피드백 생성"""
    feedback_points = []
    
    # 미소 분석
    au06 = au_data.get("AU06_r", 0)
    au12 = au_data.get("AU12_r", 0)
    
    if au06 > 0.5 and au12 > 0.5:
        feedback_points.append("진정한 미소가 감지되어 호감도가 높습니다.")
    elif au12 > 0.5:
        feedback_points.append("미소를 짓고 있지만, 더 자연스러운 미소를 지어보세요.")
    else:
        feedback_points.append("미소가 부족합니다. 입꼬리를 살짝 올려보세요.")
    
    # 눈썹 분석
    au01 = au_data.get("AU01_r", 0)
    au02 = au_data.get("AU02_r", 0)
    au04 = au_data.get("AU04_r", 0)
    
    if au01 > 0.5 or au02 > 0.5:
        feedback_points.append("적극적인 관심을 보이는 표정이 좋습니다.")
    elif au04 > 0.5:
        feedback_points.append("눈썹이 찌푸려져 있습니다. 더 밝은 표정을 지어보세요.")
    
    # 입술/턱 분석
    au23 = au_data.get("AU23_r", 0)
    au25 = au_data.get("AU25_r", 0)
    au28 = au_data.get("AU28_r", 0)
    
    if au23 > 0.5:
        feedback_points.append("입술이 긴장되어 있습니다. 편안하게 이완시켜보세요.")
    if au28 > 0.5:
        feedback_points.append("불안한 모습이 보입니다. 자신감 있게 대답해보세요.")
    
    return feedback_points
