import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function InterviewQ3() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [intervalId, setIntervalId] = useState(null);

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
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, []);

  const formatTime = (seconds) => {
    const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  };

  const startRecording = () => {
    const stream = videoRef.current?.srcObject;
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: "video/webm",
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
      const url = URL.createObjectURL(blob);
      console.log("녹화 완료, 미리보기 URL:", url);
    };

    recordedChunksRef.current = [];
    mediaRecorder.start();
    mediaRecorderRef.current = mediaRecorder;
    setIsRecording(true);

    const id = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
    setIntervalId(id);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    clearInterval(intervalId);
    navigate("/interview/q4");
  };

  const togglePause = () => {
    if (!mediaRecorderRef.current) return;

    if (isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    } else {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
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
            <p className="mt-2 text-center text-sm font-medium">
            <i className="fas fa-microphone text-teal-500"></i>
              {isRecording ? formatTime(elapsedTime) : ""}
            </p>
          </div>
        </div>

        {/* 질문 */}
        <div className="bg-gray-100 w-full text-center py-4 px-4 rounded text-lg font-medium mb-4">
          자기소개를 해주세요.
        </div>

        {/* 버튼 */}
        <div className="flex gap-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300"
            >
              발화버튼
            </button>
          ) : (
            <>
              <button
                onClick={togglePause}
                className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300"
              >
                {isPaused ? "재개" : "일시정지"}
              </button>
              <button
                onClick={stopRecording}
                className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300"
              >
                발화종료
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default InterviewQ3;
