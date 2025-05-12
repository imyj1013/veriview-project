import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

function AICounterPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId

  const [aiCounterText, setAiCounterText] = useState("");

  useEffect(() => {
    const fetchAICounter = async () => {
      try {
        const res = await axios.get(`/api/debate/${state.debateId}/ai-counter-rebuttal`);
        setAiCounterText(res.data.ai_counter_rebuttal_text);
      } catch (err) {
        console.error("AI 재반론 가져오기 실패:", err);
        setAiCounterText("AI의 재반론을 불러오지 못했습니다.");
      }
    };

    fetchAICounter();
  }, [state]);

  const handleNext = () => {
    navigate("/debate/user-closing", { state });
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
      {/* 로고, 나가기 */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-6">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[240px] cursor-pointer"
          onClick={() => navigate("/")}
        />
        <button
          onClick={() => navigate("/")}
          className="bg-gray-100 px-4 py-1 rounded hover:bg-gray-200"
        >
          나가기
        </button>
      </div>

      {/* 질문 */}
      <div className="bg-gray-100 px-6 py-4 rounded-lg shadow mb-6 text-center text-lg font-semibold w-full max-w-3xl">
        Q. {state?.topic || "질문이 없습니다."}
      </div>

      {/* AI 재반론 */}
      <div className="bg-gray-50 border px-6 py-6 text-gray-800 rounded-lg shadow w-full max-w-3xl mb-10 leading-relaxed whitespace-pre-line">
        <strong className="block mb-2">AI 토론자의 재반론:</strong>
        {aiCounterText || "AI 재반론 생성 중..."}
      </div>

      {/* 최종변론 시작 */}
      <button
        onClick={handleNext}
        className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition"
      >
        최종변론 시작
      </button>
    </div>
  );
}

export default AICounterPage;
