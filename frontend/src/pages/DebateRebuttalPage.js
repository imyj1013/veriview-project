// src/pages/DebateUserRebuttalPage.js

import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function DebateUserRebuttalPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const streamRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const navigate = useNavigate();
  const { state } = useLocation();

  // ✅ 자원 해제 함수
  const stopCamera = () => {
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
          stopCamera(); // ✅ navigate 전에 해제

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

            await new Promise((r) => setTimeout(r, 100)); // ⏱️ 안정적 전환
            navigate("/debate/ai-rebuttal", { state });
          } catch (err) {
            alert("반론 영상 업로드 실패");
            console.error(err);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
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

      {/* 캠 */}
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
          반론 종료
        </button>
      </div>
    </div>
  );
}

export default DebateUserRebuttalPage;
