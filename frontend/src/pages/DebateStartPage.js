import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function DebateStartPage() {
  const navigate = useNavigate();
  const [topic, setTopic] = useState("");
  const [position, setPosition] = useState(""); 
  const [debateId, setDebateId] = useState(null);
  const [aiOpeningText, setAiOpeningText] = useState("");
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("로그인이 필요합니다.");
      navigate("/login");
      return;
    }

    const fetchDebate = async () => {
      try {
        const res = await axios.post("/api/debate/start", {
          user_id: userId,
        });

        setTopic(res.data.topic);
        setPosition(res.data.position === "PRO" ? "찬성" : "반대");
        setDebateId(res.data.debate_id);
        setAiOpeningText(res.data.ai_opening_text);
      } catch (err) {
        alert("토론 시작에 실패했습니다.");
        console.error(err);
      }
    };

    fetchDebate();
  }, [navigate]);

  useEffect(() => {
    if (debateId && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }

    if (countdown === 0 && debateId) {
      navigate("/debate/opening", {
        state: {
          topic,
          position,
          debateId,
          aiOpeningText,
        },
      });
    }
  }, [countdown, debateId, navigate, topic, position, aiOpeningText]);

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-6 py-10">
      {/* 상단 로고 + 나가기 */}
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

      {topic && (
        <>
          {/* 질문 박스 */}
          <div className="bg-gray-100 text-lg font-semibold px-6 py-4 rounded-lg shadow mb-6 w-full max-w-3xl text-center">
            Q. {topic}
          </div>

          {/* 입장 및 카운트다운 안내 */}
          <div className="bg-gray-800 text-white text-2xl text-center px-8 py-12 rounded-lg shadow-lg w-full max-w-3xl">
            <p className="mb-4">
              귀하는 <span className="font-bold">“{position}”</span>의 입장입니다.
            </p>
            <p className="text-base">{countdown}초 후에 녹화가 시작됩니다.</p>
            <p className="text-base">입론을 준비하세요.</p>
          </div>
        </>
      )}
    </div>
  );
}

export default DebateStartPage;
