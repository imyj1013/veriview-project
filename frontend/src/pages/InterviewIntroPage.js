import React from "react";
import { useNavigate } from "react-router-dom";

function InterviewIntroPage() {
  const navigate = useNavigate();

  const handleStartInterview = () => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("로그인이 필요합니다.");
      navigate("/login");
      return;
    }
    navigate("/interview/InterviewPortfolioPage"); 
  };

  return (
    <div className="min-h-screen bg-white px-4 py-10 flex flex-col items-center">
      {/* 로고 */}
      <img
        src="/images/Logo_image.png"
        alt="logo"
        className="w-[400px] mb-6 cursor-pointer"
        onClick={() => navigate("/")}
      />

      {/* 설명 헤드라인 */}
      <div className="text-center mb-6">
        <h1 className="text-2xl font-semibold leading-relaxed">
          합격을 결정짓는 <br />
          <span className="text-blue-800 font-bold">veriview의 AI 모의면접</span>
        </h1>
      </div>

      {/* 설명 아이콘 */}
      <img
        src="/images/image20.png"
        alt="면접 설명 이미지"
        className="w-[120px] mb-6"
      />

      {/* 문구 설명 */}
      <div className="text-center text-gray-700 mb-6 space-y-2">
        <p>“AI 면접관과 면접을 진행합니다.”</p>
        <p>“발화 버튼을 눌러 의견을 말할 수 있습니다.”</p>
        <p>“실전과 비슷한 모의 연습을 할 수 있습니다.”</p>
      </div>

      {/* 기능 소개 박스 */}
      <div className="bg-blue-100 w-full max-w-2xl p-6 rounded-xl text-center mb-10">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          면접 고민, 한번에 해결하세요!
        </h2>
        <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-700">
          <span className="bg-white px-4 py-2 rounded shadow">순발력과 즉흥적 대처 능력</span>
          <span className="bg-white px-4 py-2 rounded shadow">토론면접 완벽 대비</span>
          <span className="bg-white px-4 py-2 rounded shadow">발표력과 자신감 향상</span>
          <span className="bg-white px-4 py-2 rounded shadow">실전과 비슷한 모의 연습</span>
        </div>

        {/* 면접 예시 이미지 */}
        <img
          src="/images/image19.png"
          alt="개인면접 예시"
          className="w-full max-w-2xl mt-6 rounded shadow"
        />
      </div>

      {/* 시작 버튼 */}
      <button
        onClick={handleStartInterview}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
      >
        AI 개인면접 시작하기
      </button>
    </div>
  );
}

export default InterviewIntroPage;
