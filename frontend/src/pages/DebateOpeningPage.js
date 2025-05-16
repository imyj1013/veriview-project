

import React, { useRef, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function DebateOpeningPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [chunks, setChunks] = useState([]);
  const navigate = useNavigate();
  const { state } = useLocation(); // topic, position, debateId

  useEffect(() => {
    const startCamera = async () => {
      try {
        const userStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setStream(userStream);
        if (videoRef.current) {
          videoRef.current.srcObject = userStream;
        }

        const mediaRecorder = new MediaRecorder(userStream, {
          mimeType: "video/webm",
        });

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            setChunks((prev) => [...prev, e.data]);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
      } catch (err) {
        alert("웹캠 사용이 허용되지 않았습니다.");
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

  const handleStart = () => {
    mediaRecorderRef.current?.start();
  };

  const handleEnd = async () => {
    mediaRecorderRef.current?.stop();

    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      const formData = new FormData();
      formData.append("video", blob);

      try {
        await axios.post(`/api/debate/${state.debateId}/opening-video`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        navigate("/debate/ai-opening", { state });
      } catch (err) {
        console.error("영상 업로드 실패:", err);
        alert("영상 업로드에 실패했습니다.");
      }
    };
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
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

      <div className="bg-gray-100 px-6 py-4 rounded-lg shadow mb-6 text-center text-lg font-semibold w-full max-w-3xl">
        Q. {state?.topic || "질문이 없습니다."}
      </div>

      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full max-w-3xl h-[480px] bg-black rounded-lg mb-6"
      />

      <div className="flex gap-4">
        <button
          onClick={handleStart}
          className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
        >
          녹화 시작
        </button>
        <button
          onClick={handleEnd}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          발언 종료 (업로드)
        </button>
      </div>
    </div>
  );
}

export default DebateOpeningPage;
