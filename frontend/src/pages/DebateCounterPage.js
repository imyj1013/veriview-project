// src/pages/DebateCounterPage.js

import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function DebateCounterPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const streamRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const navigate = useNavigate();
  const { state } = useLocation();

  const stopCamera = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
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
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        const recorder = new MediaRecorder(stream, {
          mimeType: "video/webm",
        });

        recordedChunksRef.current = [];

        recorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunksRef.current.push(event.data);
          }
        };

        recorder.onstop = async () => {
          stopCamera(); // ✅ 확실하게 정리

          const originalBlob = new Blob(recordedChunksRef.current, {
            type: "video/webm",
          });

          try {
            const fixedBlob = await fixWebmDuration(originalBlob);

            const formData = new FormData();
            formData.append("file", fixedBlob, "counter-rebuttal-video.webm");

            await axios.post(
              `/api/debate/${state.debateId}/counter-rebuttal-video`,
              formData,
              {
                headers: { "Content-Type": "multipart/form-data" },
              }
            );

            // ✅ navigate 전에 짧은 지연 (onstop 처리 타이밍 안정화)
            await new Promise((r) => setTimeout(r, 100));

            navigate("/debate/ai-counter", { state });
          } catch (err) {
            alert("재반론 영상 업로드 실패");
            console.error(err);
          }
        };

        mediaRecorderRef.current = recorder;
        recorder.start();
        setRecording(true);
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    startCamera();

    return () => {
      stopCamera(); // ✅ 언마운트 시 정리
    };
  }, [state, navigate]);

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
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
      {/* 상단 바 */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-6">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[240px] cursor-pointer"
          onClick={handleExit}
        />
        <button
          onClick={handleExit}
          className="bg-gray-100 px-4 py-1 rounded hover:bg-gray-200"
        >
          나가기
        </button>
      </div>

      {/* 질문 */}
      <div className="bg-gray-100 text-lg font-semibold px-6 py-4 rounded-lg shadow mb-6 w-full max-w-3xl text-center">
        Q. {state?.topic || "질문을 불러올 수 없습니다."}
      </div>

      {/* 비디오 */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full max-w-3xl h-[480px] bg-black rounded-lg mb-6"
      />

      {/* 버튼 */}
      <div className="flex gap-4">
        {recording && <span className="text-green-700 font-semibold">녹화 중...</span>}
        <button
          onClick={handleEnd}
          disabled={!recording}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          재반론 종료
        </button>
      </div>
    </div>
  );
}

export default DebateCounterPage;
