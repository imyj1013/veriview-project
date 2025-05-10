// src/pages/DebateOpeningPage.js
import React, { useRef, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function DebateOpeningPage() {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId 받음

  useEffect(() => {
    const startCamera = async () => {
      try {
        const userStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        videoRef.current.srcObject = userStream;
        setStream(userStream);
      } catch (err) {
        alert("웹캠 사용이 허용되지 않았습니다.");
        console.error(err);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [stream]);

  const handleEnd = () => {
    // 추후에 영상 저장 API 연동 예정
    navigate("/debate/ai-opening", { state });
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
      {/* 로고 */}
      <img
        src="/images/Logo_image.png"
        alt="logo"
        className="w-[250px] mb-8 cursor-pointer"
        onClick={() => navigate("/")}
      />

      {/* 질문 */}
      <div className="bg-gray-100 px-6 py-4 rounded-lg shadow mb-4 text-center text-lg font-medium w-full max-w-2xl">
        Q. {state?.topic || "질문이 없습니다."}
      </div>

      {/* 웹캠 영상 */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full max-w-xl h-[360px] bg-black rounded-lg mb-6"
      />

      {/* 발언 종료 */}
      <button
        onClick={handleEnd}
        className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition"
      >
        발언 종료
      </button>
    </div>
  );
}

export default DebateOpeningPage;
