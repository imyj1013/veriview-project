import React, { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function AIClosingPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId

  const videoRef = useRef(null);
  const userVideoRef = useRef(null);
  const [aiFinalText, setAiFinalText] = useState("");
  const [videoUrl, setVideoUrl] = useState("");

  useEffect(() => {
    const cleanupTracks = () => {
      const videos = document.querySelectorAll("video");
      videos.forEach(video => {
        const stream = video.srcObject;
        if (stream instanceof MediaStream) {
          stream.getTracks().forEach(track => track.stop());
          video.srcObject = null;
        }
      });
    };

    cleanupTracks();
    return cleanupTracks;
  }, []);

  useEffect(() => {
    if (!state?.debateId) return;

    const fetchFinalText = async () => {
      try {
        const res = await axios.get(`/api/debate/${state.debateId}/ai-closing`);
        setAiFinalText(res.data.ai_closing_text || "");
      } catch (err) {
        console.error("AI 최종변론 텍스트 로딩 실패:", err);
      }
    };

    const fetchFinalVideo = async () => {
      try {
        const res = await axios.get(
          `/api/debate/${state.debateId}/ai-closing-video`,
          { responseType: "blob" }
        );
        const videoBlob = new Blob([res.data], { type: "video/mp4" });
        setVideoUrl(URL.createObjectURL(videoBlob));

        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.play().catch(err => console.error("자동 재생 실패:", err));
          }
        }, 300);
      } catch (err) {
        console.error("AI 최종변론 영상 로딩 실패:", err);
      }
    };

    fetchFinalText();
    fetchFinalVideo();
  }, [state?.debateId]);

  const handleNext = () => {
    navigate("/debate/feedback", { state });
  };

  if (!state?.topic || !aiFinalText) return null;

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      {/* 상단 바 */}
      <div className="w-full max-w-6xl flex justify-between items-center mb-6">
        <img src="/images/Logo_image.png" alt="logo" className="w-[200px]" />
        <button className="text-lg" onClick={() => navigate("/")}>나가기</button>
      </div>

      {/* 주제 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 text-center text-xl rounded mb-8 font-semibold">
        Q. {state.topic}
      </div>

      {/* 영상 */}
      <div className="flex gap-8 mb-6 w-full max-w-6xl justify-center">
        {/* AI 토론자 */}
        <div className="flex flex-col items-center">
          {videoUrl ? (
            <video
              ref={videoRef}
              src={videoUrl}
              autoPlay
              controls
              playsInline
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

      {/* AI 최종변론 텍스트 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 rounded mb-8 text-base whitespace-pre-wrap break-words">
        <strong>AI 토론자의 최종변론:</strong> {aiFinalText}
      </div>

      {/* 버튼 */}
      <div className="flex gap-4">
        <button
          onClick={handleNext}
          className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition"
        >
          결과 피드백 보기
        </button>
      </div>
    </div>
  );
}

export default AIClosingPage;
