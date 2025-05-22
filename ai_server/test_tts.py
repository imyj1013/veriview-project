#!/usr/bin/env python3
"""
TTS 기능 테스트 스크립트
"""

import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_tts_basic():
    """기본 TTS 테스트"""
    try:
        logger.info("=== TTS 기본 테스트 시작 ===")
        
        # TTS 임포트 테스트
        from TTS.api import TTS
        import TTS as TTS_module
        
        logger.info(f"TTS 버전: {TTS_module.__version__}")
        
        # 1. 기본 TTS 객체 생성
        logger.info("1. 기본 TTS 객체 생성 시도...")
        tts = TTS()
        logger.info("✓ 기본 TTS 객체 생성 성공")
        
        # 2. 간단한 텍스트 변환 테스트
        logger.info("2. 텍스트-음성 변환 테스트...")
        test_text = "Hello, this is a TTS test."
        wav = tts.tts(test_text)
        
        if wav is not None and len(wav) > 0:
            logger.info(f"✓ TTS 변환 성공 - 오디오 길이: {len(wav)}")
        else:
            logger.error("✗ TTS 변환 실패 - 빈 결과")
            return False
        
        # 3. 파일 저장 테스트
        logger.info("3. 파일 저장 테스트...")
        output_file = "test_output.wav"
        try:
            if hasattr(tts, 'save_wav'):
                tts.save_wav(wav, output_file)
                logger.info("✓ TTS 내장 저장 방법 사용")
            else:
                import soundfile as sf
                sf.write(output_file, wav, 22050)
                logger.info("✓ soundfile 저장 방법 사용")
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"✓ 파일 저장 성공: {output_file} ({os.path.getsize(output_file)} bytes)")
                os.remove(output_file)  # 테스트 파일 삭제
            else:
                logger.error("✗ 파일 저장 실패")
                return False
                
        except Exception as save_error:
            logger.error(f"✗ 파일 저장 중 오류: {save_error}")
            return False
        
        logger.info("=== TTS 기본 테스트 완료 (성공) ===")
        return True
        
    except Exception as e:
        logger.error(f"TTS 기본 테스트 실패: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_tts_models():
    """TTS 모델 목록 테스트"""
    try:
        logger.info("=== TTS 모델 목록 테스트 시작 ===")
        
        from TTS.api import TTS
        
        # TTS 객체 생성
        tts = TTS()
        
        # 모델 목록 가져오기 테스트
        logger.info("사용 가능한 모델 확인 시도...")
        try:
            models = tts.list_models()
            logger.info(f"Models 객체 타입: {type(models)}")
            
            # 모델 정보 추출 시도
            model_names = []
            try:
                if hasattr(models, 'models_dict'):
                    model_names = list(models.models_dict.keys())
                elif hasattr(models, 'models'):
                    model_names = list(models.models.keys())
                else:
                    # 직접 반복 시도
                    model_names = list(models)
            except Exception as extract_error:
                logger.warning(f"모델 목록 추출 실패: {extract_error}")
                # 기본 모델들로 대체
                model_names = [
                    "tts_models/en/ljspeech/tacotron2-DDC",
                    "tts_models/multilingual/multi-dataset/xtts_v2"
                ]
            
            logger.info(f"발견된 모델 수: {len(model_names)}")
            
            if model_names:
                logger.info("사용 가능한 모델들 (상위 5개):")
                for i, model in enumerate(model_names[:5]):
                    logger.info(f"  {i+1}. {model}")
            
            logger.info("=== TTS 모델 목록 테스트 완료 ===")
            return True
            
        except Exception as models_error:
            logger.error(f"모델 목록 확인 실패: {models_error}")
            return False
            
    except Exception as e:
        logger.error(f"TTS 모델 테스트 실패: {str(e)}")
        return False

def test_specific_models():
    """특정 모델들 테스트"""
    logger.info("=== 특정 TTS 모델 테스트 시작 ===")
    
    from TTS.api import TTS
    
    # 테스트할 모델들
    test_models = [
        "tts_models/en/ljspeech/tacotron2-DDC",
        "tts_models/en/ljspeech/speedy-speech", 
        "tts_models/multilingual/multi-dataset/xtts_v2",
    ]
    
    successful_models = []
    
    for model_name in test_models:
        try:
            logger.info(f"모델 테스트: {model_name}")
            tts = TTS(model_name=model_name)
            
            # 간단한 변환 테스트
            wav = tts.tts("Test sentence.")
            if wav is not None and len(wav) > 0:
                logger.info(f"✓ {model_name} 성공")
                successful_models.append(model_name)
            else:
                logger.warning(f"✗ {model_name} 변환 실패")
                
        except Exception as model_error:
            logger.warning(f"✗ {model_name} 로드 실패: {model_error}")
    
    logger.info(f"=== 특정 모델 테스트 완료 - 성공: {len(successful_models)}/{len(test_models)} ===")
    
    if successful_models:
        logger.info("성공한 모델들:")
        for model in successful_models:
            logger.info(f"  ✓ {model}")
        return True
    else:
        logger.error("성공한 모델이 없습니다.")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("========================================")
    logger.info("TTS 전체 테스트 시작")
    logger.info("========================================")
    
    results = []
    
    # 1. 기본 테스트
    results.append(("기본 TTS 테스트", test_tts_basic()))
    
    # 2. 모델 목록 테스트
    results.append(("모델 목록 테스트", test_tts_models()))
    
    # 3. 특정 모델 테스트
    results.append(("특정 모델 테스트", test_specific_models()))
    
    # 결과 요약
    logger.info("========================================")
    logger.info("TTS 테스트 결과 요약")
    logger.info("========================================")
    
    success_count = 0
    for test_name, result in results:
        status = "성공" if result else "실패"
        logger.info(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    logger.info(f"전체 테스트: {success_count}/{len(results)} 성공")
    
    if success_count == len(results):
        logger.info("🎉 모든 TTS 테스트 성공! 서버에서 TTS 기능을 사용할 수 있습니다.")
    elif success_count > 0:
        logger.info("⚠️  일부 TTS 테스트 성공. 기본 기능은 작동할 것입니다.")
    else:
        logger.error("❌ 모든 TTS 테스트 실패. 서버에서 TTS 기능이 비활성화됩니다.")

if __name__ == "__main__":
    main()
