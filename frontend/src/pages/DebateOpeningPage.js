import React, { useRef, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

function DebateOpeningPage() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [stream, setStream] = useState(null);
  const [recording, setRecording] = useState(false);
  const navigate = useNavigate();
  const { state } = useLocation(); // { topic, position, debateId, aiOpeningText }

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
        setStream(userStream);

        const mediaRecorder = new MediaRecorder(userStream, {
          mimeType: "video/webm",
        });

        recordedChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder;
        setRecording(true);
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

  const handleEnd = async () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        const formData = new FormData();
        formData.append("file", blob, "opening-video.webm");

        try {
          await axios.post(`/api/debate/${state.debateId}/opening-video`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          // 성공 시 다음 페이지로 이동
          navigate("/debate/ai-opening", { state });
        } catch (err) {
          alert("영상 전송에 실패했습니다.");
          console.error(err);
        }
      };
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-4 py-10">
      {/* 상단 로고 + 나가기 */}
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
      <div className="bg-gray-100 px-6 py-4 rounded-lg shadow mb-6 text-center text-lg font-semibold w-full max-w-3xl">
        Q. {state?.topic || "질문이 없습니다."}
      </div>

      {/* 웹캠 영상 */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full max-w-3xl h-[480px] bg-black rounded-lg mb-6"
      />

      {/* 발언 종료 */}
      <button
        onClick={handleEnd}
        disabled={!recording}
        className="bg-blue-600 text-white px-8 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50"
      >
        발언 종료
      </button>
    </div>
  );
}

export default DebateOpeningPage;
