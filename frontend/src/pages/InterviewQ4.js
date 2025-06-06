import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function InterviewQ4() {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const aiVideoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const timerRef = useRef(null);

  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [question, setQuestion] = useState("");
  const [aiVideoUrl, setAiVideoUrl] = useState("");

  const [showAiImage, setShowAiImage] = useState(false);

  const formatTime = (sec) => {
    const m = String(Math.floor(sec / 60)).padStart(2, "0");
    const s = String(sec % 60).padStart(2, "0");
    return `00:${m}:${s}`;
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

    if (webcamRef.current) {
      webcamRef.current.srcObject = null;
    }

    mediaRecorderRef.current = null;
  };

  useEffect(() => {
    const interviewId = localStorage.getItem("interview_id");

    const fetchQuestionAndVideo = async () => {
      try {
        const res = await axios.get(`/api/interview/${interviewId}/question`);
        const q = res.data.questions.find((q) => q.question_type === "TECH");
        setQuestion(q?.question_text || "질문을 불러올 수 없습니다.");

        const aiVideoRes = await axios.get(
          `/api/interview/${interviewId}/TECH/ai-video`,
          { responseType: "blob" }
        );
        const videoBlob = new Blob([aiVideoRes.data], { type: "video/mp4" });
        const videoUrl = URL.createObjectURL(videoBlob);
        setAiVideoUrl(videoUrl);
        setTimeout(() => {
          if (aiVideoRef.current) {
            aiVideoRef.current.muted = false; // ✅ 음소거 해제
            aiVideoRef.current.volume = 1;
            aiVideoRef.current.play().catch(err => console.error("자동 재생 실패:", err));
          }
        }, 500);
      } catch (err) {
        console.error("질문 또는 면접관 영상 로딩 실패", err);
      }
    };

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (webcamRef.current) webcamRef.current.srcObject = stream;
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    fetchQuestionAndVideo();
    startCamera();

    return () => {
      stopCamera();
    };
  }, []);

  const startRecording = () => {
    const stream = webcamRef.current?.srcObject;
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    recordedChunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      stopCamera();

      const originalBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });

      try {
        const fixedBlob = await fixWebmDuration(originalBlob);
        const formData = new FormData();
        const interviewId = localStorage.getItem("interview_id");
        formData.append("file", fixedBlob, "tech.webm");

        await axios.post(`/api/interview/${interviewId}/TECH/answer-video`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        await new Promise((r) => setTimeout(r, 100));
        navigate("/interview/q5");
      } catch (err) {
        alert("영상 업로드 실패");
        console.error(err);
      }
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);

    timerRef.current = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    if (!mediaRecorderRef.current) return;
    mediaRecorderRef.current.stop();
    setIsRecording(false);
    clearInterval(timerRef.current);
  };

  const togglePause = () => {
    if (!mediaRecorderRef.current) return;

    if (isPaused) {
      mediaRecorderRef.current.resume();
      timerRef.current = setInterval(() => setElapsedTime((prev) => prev + 1), 1000);
      setIsPaused(false);
    } else {
      mediaRecorderRef.current.pause();
      clearInterval(timerRef.current);
      setIsPaused(true);
    }
  };

  const handleExit = () => {
    stopCamera();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      <div className="w-full max-w-6xl flex justify-between items-center mb-6">
        <img src="/images/Logo_image.png" alt="logo" className="w-[200px]" />
        <button onClick={handleExit} className="bg-gray-100 px-4 py-1 rounded hover:bg-gray-200">
          나가기
        </button>
      </div>

      <div className="w-full max-w-5xl bg-gray-100 py-4 px-6 text-center text-xl rounded mb-8 font-semibold">
        Q. {question}
      </div>

      <div className="flex gap-8 mb-6 w-full max-w-6xl justify-center">
        <div className="flex flex-col items-center">
          {showAiImage ? ( 
           <img
              src="/images/interviewer_static.png" 
              alt="AI 면접관"
              className="w-[500px] h-[400px] object-cover rounded-lg bg-black"
            />
          ) : (
          <video
            src={aiVideoUrl}
            ref={aiVideoRef}
            controls
            playsInline
            autoPlay
            onEnded={() => setShowAiImage(true)} 
            className="w-[500px] h-[400px] object-cover rounded-lg bg-black"
          />
          )}
          <p className="mt-2 text-base font-medium">AI 면접관</p>
        </div>

        <div className="flex flex-col items-center">
          <video
            ref={webcamRef}
            autoPlay
            muted
            playsInline
            className="w-[500px] h-[400px] bg-black object-cover rounded-lg"
          />
          <p className="mt-2 text-base font-medium">{isRecording ? formatTime(elapsedTime) : ""}</p>
        </div>
      </div>

      <div className="flex gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            녹화 시작
          </button>
        ) : (
          <>
            <button
              onClick={stopRecording}
              className="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600"
            >
              녹화 종료
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default InterviewQ4;
