// src/pages/DebateOpeningPage.js

import React, { useRef, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function DebateOpeningPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const streamRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const hasStartedRef = useRef(false);

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
  };

  useEffect(() => {
    const init = async () => {
      if (hasStartedRef.current) return;
      hasStartedRef.current = true;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: "video/webm",
        });

        recordedChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const originalBlob = new Blob(recordedChunksRef.current, {
            type: "video/webm",
          });

          try {
            const fixedBlob = await fixWebmDuration(originalBlob);
            const formData = new FormData();
            formData.append("file", fixedBlob, "opening-video.webm");

            await axios.post(
              `/api/debate/${state.debateId}/opening-video`,
              formData,
              {
                headers: { "Content-Type": "multipart/form-data" },
              }
            );
          } catch (err) {
            alert("입론 영상 업로드 실패");
            console.error(err);
          }

          stopCamera(); // ✅ 업로드 후 정리
          navigate("/debate/ai-opening", { state });
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setRecording(true);
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    init();

    return () => {
      stopCamera(); // ✅ 언마운트 시 정리
    };
  }, [navigate, state]);

  const handleExit = () => {
    stopCamera();
    navigate("/");
  };

  const handleEnd = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
      {/* 상단바 */}
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
          입론 종료
        </button>
      </div>
    </div>
  );
}

export default DebateOpeningPage;
