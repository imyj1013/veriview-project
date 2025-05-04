import React from "react";
import { useNavigate } from "react-router-dom";

function DebateIntroPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F5F5F5] flex flex-col items-center justify-center px-4 py-10">
      {/* 로고 */}
      <img
        src="/images/Logo_image.png"
        alt="logo"
        className="w-[200px] mb-6"
      />

      {/* 제목 */}
      <h1 className="text-2xl font-bold text-gray-800 mb-4">
        AI 토론면접 시작 전 안내
      </h1>

      {/* 설명 텍스트 */}
      <div className="max-w-xl text-center text-gray-700 mb-8 leading-relaxed">
        <p className="mb-3">
          이 면접은 실제 토론 상황을 가정하여 AI가 진행하는 시뮬레이션입니다.
        </p>
        <p className="mb-3">
          주제에 대한 찬성과 반대 입장을 생각하고, 논리적인 의견을 표현해주세요.
        </p>
        <p>
          준비가 완료되면 아래 <strong>‘토론 시작하기’</strong> 버튼을 눌러주세요.
        </p>
      </div>

      {/* 시작 버튼 */}
      <button
        onClick={() => navigate("/debate")}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
      >
        토론 시작하기
      </button>
    </div>
  );
}

export default DebateIntroPage;
