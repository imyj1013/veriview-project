import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function AIClosingPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId
  const [aiFinalText, setAiFinalText] = useState("");

  useEffect(() => {
    const fetchAiFinal = async () => {
      try {
        const res = await axios.get(`/api/debate/${state.debateId}/ai-closing`);
        setAiFinalText(res.data.ai_closing_text);
      } catch (err) {
        console.error("AI 최종변론 불러오기 실패:", err);
        setAiFinalText("AI 최종변론을 불러오지 못했습니다.");
      }
    };

    if (state?.debateId) {
      fetchAiFinal();
    }
  }, [state?.debateId]);

  const handleNext = () => {
    navigate("/debate/feedback", { state });
  };

  if (!state?.topic || !aiFinalText) return null;

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
      <div className="bg-gray-100 px-6 py-4 rounded-lg shadow mb-4 text-center text-lg font-semibold w-full max-w-3xl">
        Q. {state.topic}
      </div>

      {/* AI 최종변론 */}
      <div className="bg-gray-50 border text-gray-800 px-6 py-6 rounded-lg shadow w-full max-w-3xl text-base mb-6 leading-relaxed whitespace-pre-line">
        <strong className="block mb-2">AI 토론자의 최종변론:</strong>
        {aiFinalText}
      </div>

      <button
        onClick={handleNext}
        className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition"
      >
        결과 피드백 보기
      </button>
    </div>
  );
}

export default AIClosingPage;
