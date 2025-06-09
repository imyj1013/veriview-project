import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

function AICounterPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId

  const userVideoRef = useRef(null);
  const [aiCounterText, setAiCounterText] = useState("");
  const [aiVideoUrl, setAiVideoUrl] = useState(null);

  // 사용자 웹캠 연결
  useEffect(() => {
    const startUserCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        if (userVideoRef.current) {
          userVideoRef.current.srcObject = stream;
        }
      } catch (err) {
        alert("웹캠 접근이 필요합니다.");
        console.error(err);
      }
    };

    startUserCamera();

    return () => {
      if (userVideoRef.current?.srcObject) {
        userVideoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // AI 텍스트 + 영상 로딩
  useEffect(() => {
    const fetchData = async () => {
      try {
        const textRes = await axios.get(`/api/debate/${state.debateId}/ai-counter-rebuttal`);
        setAiCounterText(textRes.data.ai_counter_rebuttal_text || "");
      } catch (err) {
        console.error("AI 재반론 텍스트 로딩 실패:", err);
      }

      try {
        // 캐시 방지를 위한 타임스탬프 추가
        const timestamp = new Date().getTime();
        const videoRes = await axios.get(
          `/api/debate/${state.debateId}/ai-counter-rebuttal-video?t=${timestamp}`,
          { 
            responseType: "blob",
            headers: {
              'Cache-Control': 'no-cache, no-store, must-revalidate',
              'Pragma': 'no-cache',
              'Expires': '0'
            }
          }
        );
        
        // 이전 비디오 URL 정리
        if (aiVideoUrl) {
          URL.revokeObjectURL(aiVideoUrl);
        }
        
        const videoBlobUrl = URL.createObjectURL(videoRes.data);
        setAiVideoUrl(videoBlobUrl);
      } catch (err) {
        console.error("AI 재반론 영상 로딩 실패:", err);
      }
    };

    if (state?.debateId) fetchData();

    return () => {
      if (aiVideoUrl) {
        URL.revokeObjectURL(aiVideoUrl);
      }
    };
  }, [state?.debateId]);

  const handleNext = () => {
    navigate("/debate/user-closing", { state });
  };

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      {/* 상단 로고 & 나가기 */}
      <div className="w-full max-w-6xl flex justify-between items-center mb-6">
        <img src="/images/Logo_image.png" alt="logo" className="w-[200px]" />
        <button onClick={() => navigate("/")} className="text-lg">
          나가기
        </button>
      </div>

      {/* 질문 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 text-center text-xl rounded mb-8 font-semibold">
        Q. {state?.topic || "질문을 불러올 수 없습니다."}
      </div>

      {/* 영상 */}
      <div className="flex gap-8 mb-6 w-full max-w-6xl justify-center">
        {/* AI 토론자 */}
        <div className="flex flex-col items-center">
          {aiVideoUrl ? (
            <video
              src={aiVideoUrl}
              autoPlay
              controls
              className="w-[480px] h-[360px] bg-black object-cover rounded-lg"
            />
          ) : (
            <div className="w-[480px] h-[360px] bg-gray-600 rounded-lg flex items-center justify-center text-white">
              로딩 중...
            </div>
          )}
          <p className="mt-2 text-base font-medium">AI 토론자</p>
        </div>

        {/* 사용자 */}
        <div className="flex flex-col items-center">
          <video
            ref={userVideoRef}
            autoPlay
            muted
            playsInline
            className="w-[480px] h-[360px] bg-black object-cover rounded-lg"
          />
          <p className="mt-2 text-base font-medium">00:00</p>
        </div>
      </div>

      {/* AI 재반론 텍스트 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 rounded mb-8 text-base whitespace-pre-wrap break-words leading-relaxed">
        <strong>AI 토론자의 재반론:</strong> {aiCounterText || "불러오는 중..."}
      </div>

      {/* 버튼 */}
      <div className="flex gap-4">
        <button
          onClick={handleNext}
          className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition"
        >
          최종변론 시작
        </button>
      </div>
    </div>
  );
}

export default AICounterPage;
