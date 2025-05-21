

import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix"; 

function DebateClosingPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [recording, setRecording] = useState(false);
  const navigate = useNavigate();
  const { state } = useLocation(); 

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

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
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const handleEnd = async () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);

      mediaRecorderRef.current.onstop = async () => {
        const originalBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });

        if (videoRef.current?.srcObject) {
          videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
          videoRef.current.srcObject = null; 
        }

        try {
          const fixedBlob = await fixWebmDuration(originalBlob); 
          const formData = new FormData();
          formData.append("file", fixedBlob, "closing-video.webm");

          await axios.post(
            `/api/debate/${state.debateId}/closing-video`,
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );

          navigate("/debate/ai-closing", { state });
        } catch (err) {
          alert("최종변론 영상 업로드 실패");
          console.error(err);
        }
      };
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

      {/* 녹화 상태 표시, 종료 */}
      <div className="flex gap-4">
        <span className="text-green-700 font-semibold">녹화 중...</span>
        <button
          onClick={handleEnd}
          disabled={!recording}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          최종변론 종료
        </button>
      </div>
    </div>
  );
}

export default DebateClosingPage;
