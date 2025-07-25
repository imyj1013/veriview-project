import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function DebateUserRebuttalPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId

  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const streamRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const timerRef = useRef(null);

  const formatTime = (sec) => {
    const h = String(Math.floor(sec / 3600)).padStart(2, "0");
    const m = String(Math.floor((sec % 3600) / 60)).padStart(2, "0");
    const s = String(sec % 60).padStart(2, "0");
    return `${h}:${m}:${s}`;
  };

  const stopCamera = () => {
    clearInterval(timerRef.current);
    setElapsedTime(0);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    mediaRecorderRef.current = null;
  };

  useEffect(() => {
    const startCamera = async () => {
      try {
        const userStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        streamRef.current = userStream;
        if (videoRef.current) {
          videoRef.current.srcObject = userStream;
        }

        const mediaRecorder = new MediaRecorder(userStream, {
          mimeType: "video/webm",
        });

        recordedChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            recordedChunksRef.current.push(e.data);
          }
        };

        mediaRecorder.onstop = async () => {
          stopCamera();

          const originalBlob = new Blob(recordedChunksRef.current, {
            type: "video/webm",
          });

          try {
            const fixedBlob = await fixWebmDuration(originalBlob);
            const formData = new FormData();
            formData.append("file", fixedBlob, "rebuttal-video.webm");

            await axios.post(
              `/api/debate/${state.debateId}/rebuttal-video`,
              formData,
              {
                headers: { "Content-Type": "multipart/form-data" },
              }
            );

            await new Promise((r) => setTimeout(r, 100));
            navigate("/debate/ai-rebuttal", { state });
          } catch (err) {
            alert("반론 영상 업로드 실패");
            console.error(err);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setRecording(true);

        timerRef.current = setInterval(() => {
          setElapsedTime((prev) => prev + 1);
        }, 1000);
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    startCamera();

    return () => {
      stopCamera();
    };
  }, [navigate, state]);

  const handleEnd = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleExit = () => {
    stopCamera();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      {/* 상단 로고 & 나가기 */}
      <div className="w-full max-w-6xl flex justify-between items-center mb-6">
        <img src="/images/Logo_image.png" alt="logo" className="w-[200px]" />
        <button
          onClick={handleExit}
          className="bg-gray-100 px-4 py-1 rounded hover:bg-gray-200"
        >
          나가기
        </button>
      </div>

      {/* 질문 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 text-center text-xl rounded mb-8 font-semibold">
        Q. {state?.topic || "질문을 불러올 수 없습니다."}
      </div>

      {/* 영상 레이아웃 */}
      <div className="flex gap-8 mb-6 w-full max-w-6xl justify-center">
        {/* AI 토론자 이미지 */}
        <div className="flex flex-col items-center">
          <img
            src="/images/ai_avatar.png"
            alt="AI Avatar"
            className="w-[480px] h-[360px] object-contain rounded-lg bg-gray-200"
          />
          <p className="mt-2 text-base font-medium">AI 토론자</p>
        </div>

        {/* 사용자 */}
        <div className="flex flex-col items-center">
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-[480px] h-[360px] bg-black object-cover rounded-lg"
          />
          <p className="mt-2 text-base font-medium">{formatTime(elapsedTime)}</p>
        </div>
      </div>

      {/* 안내 텍스트 */}
      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 rounded mb-8 text-base text-center whitespace-pre-wrap break-words leading-relaxed">
        반론을 녹화 중입니다.
      </div>

      {/* 버튼 */}
      <div className="flex gap-4">
        <button
          onClick={handleEnd}
          disabled={!recording}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          반론 종료
        </button>
      </div>
    </div>
  );
}

export default DebateUserRebuttalPage;
