import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function DebateAiOpeningPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId
  const [aiOpeningText, setAiOpeningText] = useState("");

  // useEffect(() => {
  //   const fetchAiOpening = async () => {
  //     try {
  //       const res = await axios.post(`/ai/debate/${state.debateId}/ai-opening`, {
  //         topic: state.topic,
  //         position: state.position === "찬성" ? "CON" : "PRO", 
  //         debate_id: state.debateId,
  //       });
  //       setAiOpeningText(res.data.ai_opening_text);
  //     } catch (err) {
  //       console.error("AI 입론 가져오기 실패:", err);
  //     }
  //   };

  //   fetchAiOpening();
  // }, [state]);

  const handleNext = () => {
    navigate("/debate/user-rebuttal", { state });
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
      <div className="bg-gray-100 text-lg font-semibold px-6 py-4 rounded-lg shadow mb-6 w-full max-w-3xl text-center">
        Q. {state?.topic || "질문이 없습니다."}
      </div>

      {/* AI 입론 */}
      <div className="bg-gray-50 border px-6 py-6 text-gray-800 rounded-lg shadow w-full max-w-3xl mb-10 leading-relaxed whitespace-pre-line">
        <strong className="block mb-2 text-base text-black-700">AI 토론자의 입장:</strong>
        {aiOpeningText || "AI 입론 생성 중..."}
      </div>

      {/* 반론 시작 */}
      <button
        onClick={handleNext}
        className="bg-blue-600 text-white px-8 py-3 rounded text-lg hover:bg-blue-700 transition"
      >
        반론 시작
      </button>
    </div>
  );
}

export default DebateAiOpeningPage;
