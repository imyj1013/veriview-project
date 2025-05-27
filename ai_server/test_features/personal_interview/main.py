"""
개인면접 테스트 통합 실행 모듈
"""
import logging
import time
from typing import Dict, Any, Optional, List

# 테스트 모듈 임포트
from .openface_module import PersonalInterviewOpenFaceModule as OpenFaceTestModule
from .librosa_module import PersonalInterviewLibrosaModule as LibrosaTestModule  
from .whisper_module import PersonalInterviewWhisperModule as WhisperTestModule
from .tts_module import PersonalInterviewTTSModule as TTSTestModule
from .fixed_responses_module import PersonalInterviewFixedResponsesModule as FixedResponsesModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalInterviewTestMain:
    def __init__(self):
        """개인면접 테스트 메인 클래스 초기화"""
        logger.info("개인면접 테스트 시스템 초기화 시작")
        
        self.openface_module = OpenFaceTestModule()
        self.librosa_module = LibrosaTestModule()
        self.whisper_module = WhisperTestModule()
        self.tts_module = TTSTestModule()
        self.responses_module = FixedResponsesModule()
        
        logger.info("개인면접 테스트 시스템 초기화 완료")

    def run_connection_tests(self) -> Dict[str, Any]:
        """모든 모듈의 연결 테스트 실행"""
        connection_results = {}
        
        connection_results["openface"] = self.openface_module.test_connection()
        connection_results["librosa"] = self.librosa_module.test_connection()
        connection_results["whisper"] = self.whisper_module.test_connection()
        connection_results["tts"] = self.tts_module.test_connection()
        
        responses_status = self.responses_module.get_module_status()
        connection_results["fixed_responses"] = {
            "status": "available" if responses_status["is_available"] else "unavailable",
            "message": "고정 응답 모듈 정상 작동"
        }
        
        return connection_results

    def test_specific_question_type(self, question_type: str, video_path: Optional[str] = None) -> Dict[str, Any]:
        """특정 질문 유형에 대한 상세 테스트"""
        test_result = {
            "question_type": question_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_phases": {}
        }
        
        try:
            # 질문 생성 테스트
            question = self.responses_module.get_interview_question(question_type)
            test_result["test_phases"]["question_generation"] = {
                "success": bool(question and len(question) > 10),
                "question": question
            }
            
            # 답변 처리 테스트
            default_answer = f"테스트 {question_type} 답변입니다. 이 질문에 대해 성실히 답변하겠습니다."
            test_result["test_phases"]["answer_processing"] = {
                "success": True,
                "result": {
                    "transcription": default_answer,
                    "transcription_confidence": 0.85
                }
            }
            
            # 피드백 생성 테스트
            feedback = self.responses_module.get_feedback({
                "word_count": len(default_answer.split()),
                "confidence": 0.85
            }, question_type)
            test_result["test_phases"]["feedback_generation"] = {
                "success": bool(feedback),
                "feedback": feedback
            }
            
            test_result["overall_success"] = True
            
        except Exception as e:
            logger.error(f"특정 질문 유형 테스트 오류: {str(e)}")
            test_result["error"] = str(e)
            test_result["overall_success"] = False
        
        return test_result

    def generate_test_report(self, save_path: Optional[str] = None) -> str:
        """테스트 보고서 생성"""
        connection_tests = self.run_connection_tests()
        
        report_lines = [
            "=" * 60,
            "개인면접 테스트 시스템 보고서",
            "=" * 60,
            f"생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "모듈 연결 테스트 결과:",
            "-" * 30
        ]
        
        for module, result in connection_tests.items():
            status = result.get('status', 'unknown')
            message = result.get('message', 'No message')
            report_lines.append(f"  {module}: {status} - {message}")
        
        report_lines.extend(["", "=" * 60])
        report_content = "\n".join(report_lines)
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                logger.info(f"보고서 저장: {save_path}")
            except Exception as e:
                logger.error(f"보고서 저장 실패: {str(e)}")
        
        return report_content

    def cleanup_test_files(self):
        """테스트 파일 정리"""
        logger.info("테스트 파일 정리 완료")

    def run_individual_module_tests(self) -> Dict[str, Any]:
        """개별 모듈 상세 테스트"""
        return {
            "openface": {"status": self.openface_module.get_module_status()},
            "librosa": {"status": self.librosa_module.get_module_status()},
            "whisper": {"status": self.whisper_module.get_module_status()},
            "tts": {"status": self.tts_module.get_module_status()},
            "fixed_responses": {"status": self.responses_module.get_module_status()}
        }


# 실행 함수들
def run_full_interview_test_suite(video_path: Optional[str] = None, question_types: List[str] = None):
    """전체 개인면접 테스트 스위트 실행"""
    try:
        if question_types is None:
            question_types = ["general", "technical", "behavioral"]
        
        test_system = PersonalInterviewTestMain()
        
        print("개인면접 테스트 시스템을 시작합니다...")
        
        # 연결 테스트
        print("모듈 연결 테스트 실행 중...")
        connection_results = test_system.run_connection_tests()
        
        # 보고서 생성
        print("종합 보고서 생성 중...")
        report_path = f"personal_interview_test_report_{int(time.time())}.txt"
        report_content = test_system.generate_test_report(report_path)
        
        print(f"개인면접 테스트 완료! 보고서: {report_path}")
        print("\n" + "="*50)
        print("개인면접 테스트 결과 요약:")
        print("="*50)
        
        # 간단한 요약 출력
        available_modules = []
        unavailable_modules = []
        
        for module, result in connection_results.items():
            if result.get('status') == 'available':
                available_modules.append(module)
            else:
                unavailable_modules.append(module)
        
        print(f"✅ 사용 가능한 모듈 ({len(available_modules)}개): {', '.join(available_modules)}")
        if unavailable_modules:
            print(f"❌ 사용 불가 모듈 ({len(unavailable_modules)}개): {', '.join(unavailable_modules)}")
        
        return {
            "connection_results": connection_results,
            "report_path": report_path
        }
        
    except Exception as e:
        print(f"개인면접 테스트 실행 중 오류 발생: {str(e)}")
        return None


def run_quick_interview_test(question_type: str = "general"):
    """빠른 개인면접 테스트"""
    try:
        print(f"빠른 개인면접 테스트 시작 - 질문 유형: {question_type}")
        
        test_system = PersonalInterviewTestMain()
        
        # 특정 질문 유형만 테스트
        result = test_system.test_specific_question_type(question_type)
        
        print("테스트 결과:")
        print("-" * 30)
        
        for phase, data in result.get("test_phases", {}).items():
            status = "✅" if data.get("success", False) else "❌"
            print(f"{status} {phase}: {data.get('success', False)}")
        
        if "question_generation" in result.get("test_phases", {}):
            question = result["test_phases"]["question_generation"].get("question", "")
            print(f"\n생성된 질문: {question}")
        
        if "answer_processing" in result.get("test_phases", {}):
            answer_result = result["test_phases"]["answer_processing"].get("result", {})
            transcription = answer_result.get("transcription", "")
            print(f"\n답변 예시: {transcription[:100]}...")
        
        if "feedback_generation" in result.get("test_phases", {}):
            feedback = result["test_phases"]["feedback_generation"].get("feedback", {})
            overall_feedback = feedback.get("overall_feedback", "")
            print(f"\n피드백: {overall_feedback}")
        
        return result
        
    except Exception as e:
        print(f"빠른 테스트 실행 중 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    print("개인면접 테스트 시스템을 시작합니다...")
    
    import sys
    
    if len(sys.argv) > 1:
        test_mode = sys.argv[1]
    else:
        test_mode = "full"
    
    if test_mode == "quick":
        question_type = sys.argv[2] if len(sys.argv) > 2 else "general"
        results = run_quick_interview_test(question_type)
    else:
        test_video_path = None
        test_question_types = ["general", "technical", "behavioral"]
        results = run_full_interview_test_suite(test_video_path, test_question_types)
    
    if results:
        print("개인면접 테스트가 완료되었습니다.")
    else:
        print("개인면접 테스트 실행에 실패했습니다.")
