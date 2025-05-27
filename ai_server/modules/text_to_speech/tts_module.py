"""
TTS (Text-to-Speech) 모듈
음성 합성 기능을 제공하는 모듈

지원 엔진:
1. gTTS: Google Text-to-Speech API를 이용한 경량 TTS
2. pyttsx3: 오프라인 TTS 엔진 (선택적)
3. Zonos TTS: Zonos 한국어 TTS 엔진 (미래 확장용)
"""
import os
import io
import tempfile
import logging
import time
import hashlib
import base64
from enum import Enum
from typing import Optional, Generator, Union, Dict, Any, List, BinaryIO

# 로깅 설정
logger = logging.getLogger(__name__)

class TTSEngine(Enum):
    """TTS 엔진 유형"""
    GTTS = "gtts"          # Google TTS
    PYTTSX3 = "pyttsx3"    # 오프라인 TTS
    ZONOS = "zonos"        # Zonos TTS (미래 확장용)

class TTSModule:
    """
    TTS 모듈 클래스
    텍스트를 음성으로 변환하는 기능 제공
    """
    
    def __init__(self, engine: Union[TTSEngine, str] = TTSEngine.GTTS, language: str = "ko", 
                 slow: bool = False, chunk_size: int = 4096, cache_dir: Optional[str] = None):
        """
        TTS 모듈 초기화
        
        Args:
            engine: TTS 엔진 유형 (기본값: GTTSEngine.GTTS)
            language: 언어 코드 (기본값: "ko")
            slow: 느린 발화 여부 (기본값: False)
            chunk_size: 오디오 스트리밍 청크 크기 (기본값: 4096)
            cache_dir: 캐시 디렉토리 (기본값: None - 임시 디렉토리 사용)
        """
        self.engine = engine if isinstance(engine, TTSEngine) else TTSEngine(engine)
        self.language = language
        self.slow = slow
        self.chunk_size = chunk_size
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "tts_cache")
        
        # 캐시 디렉토리 생성
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 엔진별 초기화
        self._initialize_engine()
        
        logger.info(f"TTS 모듈 초기화 완료 (엔진: {self.engine.value}, 언어: {self.language})")
    
    def _initialize_engine(self):
        """엔진별 초기화 작업 수행"""
        self.engine_instance = None
        
        if self.engine == TTSEngine.GTTS:
            try:
                # gTTS 임포트
                from gtts import gTTS
                # 임시 초기화 테스트
                _ = gTTS(text="안녕하세요", lang=self.language, slow=self.slow)
                self.is_available = True
                logger.info("gTTS 엔진 초기화 성공")
            except ImportError as e:
                logger.error(f"gTTS 패키지를 찾을 수 없습니다: {e}")
                self.is_available = False
            except Exception as e:
                logger.error(f"gTTS 엔진 초기화 실패: {e}")
                self.is_available = False
                
        elif self.engine == TTSEngine.PYTTSX3:
            try:
                # pyttsx3 임포트
                import pyttsx3
                self.engine_instance = pyttsx3.init()
                
                # 속성 설정
                voices = self.engine_instance.getProperty('voices')
                # 가용한 음성 중 한국어 또는 여성 음성 선택
                for voice in voices:
                    if self.language in voice.languages or self.language[:2] in voice.id.lower():
                        self.engine_instance.setProperty('voice', voice.id)
                        break
                
                # 속도 설정
                rate = self.engine_instance.getProperty('rate')
                self.engine_instance.setProperty('rate', rate - 50 if self.slow else rate)
                
                self.is_available = True
                logger.info("pyttsx3 엔진 초기화 성공")
            except ImportError as e:
                logger.error(f"pyttsx3 패키지를 찾을 수 없습니다: {e}")
                self.is_available = False
            except Exception as e:
                logger.error(f"pyttsx3 엔진 초기화 실패: {e}")
                self.is_available = False
                
        elif self.engine == TTSEngine.ZONOS:
            try:
                # Zonos TTS 패키지 임포트 시도
                from ZonosTTS import ZonosTTS
                self.engine_instance = ZonosTTS()
                self.is_available = True
                logger.info("Zonos TTS 엔진 초기화 성공")
            except ImportError as e:
                logger.error(f"Zonos TTS 패키지를 찾을 수 없습니다: {e}")
                self.is_available = False
            except Exception as e:
                logger.error(f"Zonos TTS 엔진 초기화 실패: {e}")
                self.is_available = False
                
        else:
            logger.error(f"지원하지 않는 TTS 엔진: {self.engine.value}")
            self.is_available = False
            
    def _generate_cache_key(self, text: str) -> str:
        """
        텍스트에 대한 캐시 키 생성
        
        Args:
            text: TTS 변환할 텍스트
            
        Returns:
            캐시 파일 이름
        """
        # SHA-256 해시 기반 캐시 키 생성
        hash_obj = hashlib.sha256(f"{text}_{self.language}_{self.slow}_{self.engine.value}".encode('utf-8'))
        hash_digest = hash_obj.digest()
        # 해시를 base64로 인코딩 (파일명으로 사용 가능하도록)
        hash_b64 = base64.urlsafe_b64encode(hash_digest).decode('ascii').rstrip('=')
        
        # 엔진별 파일 확장자 설정
        if self.engine == TTSEngine.GTTS:
            ext = "mp3"
        else:
            ext = "wav"
            
        return f"tts_{hash_b64}.{ext}"
    
    def synthesize_text(self, text: str, output_path: Optional[str] = None, 
                        use_cache: bool = True) -> Optional[Union[str, bytes]]:
        """
        텍스트를 음성으로 변환
        
        Args:
            text: 변환할 텍스트
            output_path: 출력 파일 경로 (기본값: None - 바이트 데이터 반환)
            use_cache: 캐시 사용 여부 (기본값: True)
            
        Returns:
            출력 파일 경로 또는 오디오 바이트 데이터
        """
        if not self.is_available:
            logger.warning("TTS 엔진을 사용할 수 없습니다.")
            return None
            
        if not text or not text.strip():
            logger.warning("변환할 텍스트가 비어있습니다.")
            return None
            
        # 텍스트 정제
        text = text.strip()
        
        # 캐시 키 생성
        cache_key = self._generate_cache_key(text)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        # 캐시 확인
        if use_cache and os.path.exists(cache_path):
            logger.info(f"캐시된 TTS 결과 사용: {cache_path}")
            if output_path:
                # 캐시 파일 복사
                import shutil
                shutil.copy2(cache_path, output_path)
                return output_path
            else:
                # 캐시 파일 읽기
                with open(cache_path, 'rb') as f:
                    return f.read()
                    
        # 엔진별 TTS 실행
        try:
            if self.engine == TTSEngine.GTTS:
                from gtts import gTTS
                tts = gTTS(text=text, lang=self.language, slow=self.slow)
                
                # 출력 경로가 지정된 경우
                if output_path:
                    tts.save(output_path)
                    
                    # 캐시 저장
                    if use_cache:
                        tts.save(cache_path)
                        
                    return output_path
                else:
                    # 메모리에 저장
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    audio_data = fp.getvalue()
                    
                    # 캐시 저장
                    if use_cache:
                        with open(cache_path, 'wb') as f:
                            f.write(audio_data)
                            
                    return audio_data
                    
            elif self.engine == TTSEngine.PYTTSX3:
                if not self.engine_instance:
                    logger.error("pyttsx3 엔진이 초기화되지 않았습니다.")
                    return None
                    
                # 출력 경로 설정
                temp_path = output_path or os.path.join(self.cache_dir, f"temp_tts_{int(time.time())}.wav")
                
                # TTS 실행 및 저장
                self.engine_instance.save_to_file(text, temp_path)
                self.engine_instance.runAndWait()
                
                # 출력 경로가 지정된 경우
                if output_path:
                    # 캐시 저장
                    if use_cache:
                        import shutil
                        shutil.copy2(temp_path, cache_path)
                        
                    return output_path
                else:
                    # 파일 읽기 후 삭제
                    with open(temp_path, 'rb') as f:
                        audio_data = f.read()
                        
                    os.remove(temp_path)
                    
                    # 캐시 저장
                    if use_cache:
                        with open(cache_path, 'wb') as f:
                            f.write(audio_data)
                            
                    return audio_data
                    
            elif self.engine == TTSEngine.ZONOS:
                if not self.engine_instance:
                    logger.error("Zonos TTS 엔진이 초기화되지 않았습니다.")
                    return None
                
                # 출력 경로 설정
                temp_path = output_path or os.path.join(self.cache_dir, f"temp_zonos_{int(time.time())}.wav")
                
                # TTS 실행
                self.engine_instance.synthesize(text, temp_path)
                
                # 출력 경로가 지정된 경우
                if output_path:
                    # 캐시 저장
                    if use_cache:
                        import shutil
                        shutil.copy2(temp_path, cache_path)
                        
                    return output_path
                else:
                    # 파일 읽기 후 삭제
                    with open(temp_path, 'rb') as f:
                        audio_data = f.read()
                        
                    os.remove(temp_path)
                    
                    # 캐시 저장
                    if use_cache:
                        with open(cache_path, 'wb') as f:
                            f.write(audio_data)
                            
                    return audio_data
                    
            else:
                logger.error(f"지원하지 않는 TTS 엔진: {self.engine.value}")
                return None
                
        except Exception as e:
            logger.error(f"TTS 변환 오류: {e}")
            return None
            
    def stream_audio(self, audio_data: Union[str, bytes, io.BytesIO, BinaryIO]) -> Generator[bytes, None, None]:
        """
        오디오 데이터를 스트리밍 형식으로 반환
        
        Args:
            audio_data: 오디오 데이터 (파일 경로 또는 바이트 데이터)
            
        Yields:
            오디오 데이터 청크
        """
        if isinstance(audio_data, str) and os.path.exists(audio_data):
            # 파일 경로인 경우
            with open(audio_data, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        elif isinstance(audio_data, bytes):
            # 바이트 데이터인 경우
            for i in range(0, len(audio_data), self.chunk_size):
                yield audio_data[i:i+self.chunk_size]
        elif isinstance(audio_data, io.BytesIO):
            # BytesIO 객체인 경우
            audio_data.seek(0)
            while True:
                chunk = audio_data.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
        elif hasattr(audio_data, 'read'):
            # 파일 객체인 경우
            while True:
                chunk = audio_data.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
        else:
            logger.error(f"지원하지 않는 오디오 데이터 형식: {type(audio_data)}")
            yield b''
    
    def flask_stream_response(self, text: str) -> Generator[bytes, None, None]:
        """
        텍스트를 Flask 스트리밍 응답으로 변환
        
        Args:
            text: TTS 변환할 텍스트
            
        Yields:
            오디오 데이터 청크 (Flask 스트리밍 응답용)
        """
        try:
            # 텍스트를 오디오로 변환
            audio_data = self.synthesize_text(text)
            
            if not audio_data:
                logger.warning("TTS 변환 실패")
                yield b''
                return
                
            # 오디오 데이터 스트리밍
            for chunk in self.stream_audio(audio_data):
                yield chunk
                
        except Exception as e:
            logger.error(f"Flask 스트리밍 응답 생성 오류: {e}")
            yield b''
    
    def get_content_type(self) -> str:
        """
        현재 TTS 엔진의 오디오 콘텐츠 타입 반환
        
        Returns:
            MIME 타입 문자열
        """
        if self.engine == TTSEngine.GTTS:
            return "audio/mpeg"
        else:
            return "audio/wav"
    
    def get_module_status(self) -> Dict[str, Any]:
        """
        모듈 상태 정보 반환
        
        Returns:
            상태 정보 딕셔너리
        """
        return {
            "module_name": "TTS (Text-to-Speech)",
            "engine": self.engine.value,
            "language": self.language,
            "is_available": self.is_available,
            "cache_dir": self.cache_dir,
            "content_type": self.get_content_type()
        }
    
    def cleanup_cache(self, max_age_days: int = 7) -> int:
        """
        오래된 캐시 파일 정리
        
        Args:
            max_age_days: 최대 보관 기간 (일)
            
        Returns:
            삭제된 파일 수
        """
        if not os.path.exists(self.cache_dir):
            return 0
            
        count = 0
        max_age_seconds = max_age_days * 86400  # 일 -> 초 변환
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            
            # 파일인지 확인
            if not os.path.isfile(file_path):
                continue
                
            # TTS 캐시 파일인지 확인
            if not filename.startswith("tts_"):
                continue
                
            # 파일 수정 시간 확인
            file_age = current_time - os.path.getmtime(file_path)
            
            # 오래된 파일 삭제
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    logger.warning(f"캐시 파일 삭제 실패: {file_path} - {e}")
                    
        logger.info(f"오래된 캐시 파일 {count}개 삭제됨 (최대 보관 기간: {max_age_days}일)")
        return count
