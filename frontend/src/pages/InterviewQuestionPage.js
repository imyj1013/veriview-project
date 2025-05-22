import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function InterviewQuestionPage() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const userStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        if (videoRef.current) {
          videoRef.current.srcObject = userStream;
        }

        setRecording(true);
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    startCamera();

    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const handleStartInterview = () => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("로그인이 필요합니다.");
      navigate("/login");
      return;
    }
    navigate("/interview/q1"); // 질문 1 페이지로 이동
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

      {/* 면접관과 사용자 화면 */}
      <div className="flex flex-col items-center border-4 px-6 py-8 rounded-xl">
        <div className="flex gap-6 mb-4">
          {/* AI 면접관 화면 */}
          <div className="flex flex-col items-center">
            <div className="w-[400px] h-[300px] bg-gray-600 rounded-md"></div>
            <p className="mt-2 text-center text-sm font-medium">AI 면접관</p>
          </div>
          {/* 사용자 화면 (웹캠) */}
          <div className="flex flex-col items-center">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="w-[400px] h-[300px] bg-black rounded-md"
            />
            <p className="mt-2 text-center text-sm">
              <i className="fas fa-microphone text-teal-500"></i>
            </p>
          </div>
        </div>

        {/* 안내 메시지 */}
        <div className="bg-gray-100 w-full text-center py-4 px-4 rounded">
          <p className="text-lg font-semibold text-gray-800">
            발화버튼을 누른 후 답변해주세요.
          </p>
          <p className="text-sm text-gray-600 mt-1">
            *질문 넘기기를 누를 시 이전 페이지로 돌아갈 수 없습니다.
          </p>
        </div>

        {/* 시작 버튼 */}
        <button
          onClick={handleStartInterview}
          className="mt-6 bg-gray-200 text-black px-6 py-2 rounded hover:bg-gray-300"
        >
          시작하기
        </button>
      </div>
    </div>
  );
}

export default InterviewQuestionPage;
