// src/pages/DebateStartPage.js
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function DebateStartPage() {
  const navigate = useNavigate();
  const [topic, setTopic] = useState("");
  const [position, setPosition] = useState("");
  const [debateId, setDebateId] = useState(null);
  const [countdown, setCountdown] = useState(10);

  // TODO: 실제 로그인한 사용자 ID 가져오기
  const userId = localStorage.getItem("user_id"); // 백엔드 연결 시 자동화 가능

  useEffect(() => {
    const fetchDebate = async () => {
      try {
        const res = await axios.post("/api/debate/start", {
          user_id: userId || "kimoo", // 임시 fallback
        });

        setTopic(res.data.topic);
        setPosition(res.data.position === "PRO" ? "찬성" : "반대");
        setDebateId(res.data.debate_id);
      } catch (err) {
        console.error("토론 시작 실패:", err);
        // 예외 처리 필요 시 여기에 UI 표시 추가 가능
      }
    };

    fetchDebate();
  }, [userId]);

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
        },
      });
    }
  }, [countdown, debateId, navigate, topic, position]);

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6 py-12">
      <img src="/images/Logo_image.png" alt="logo" className="w-[250px] mb-8" />

      {topic && (
        <>
          <div className="bg-gray-100 text-lg px-6 py-3 rounded-lg shadow mb-6 text-center w-full max-w-2xl">
            <span className="font-semibold">Q. {topic}</span>
          </div>

          <div className="bg-gray-800 text-white text-2xl text-center px-8 py-12 rounded-lg shadow-lg w-full max-w-xl">
            <p className="mb-2">귀하는 “<span className="font-bold">{position}</span>”의 입장입니다.</p>
            <p className="text-base mt-4">{countdown}초 후에 녹화가 시작됩니다.</p>
            <p className="text-base">입론을 준비하세요.</p>
          </div>
        </>
      )}
    </div>
  );
}

export default DebateStartPage;
