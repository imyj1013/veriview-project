import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import fixWebmDuration from "webm-duration-fix";

function InterviewQ5() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const intervalRef = useRef(null);

  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [questionText, setQuestionText] = useState("");

  const stopCamera = () => {
    const stream = streamRef.current || videoRef.current?.srcObject;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    streamRef.current = null;
  };

  useEffect(() => {
    const interviewId = localStorage.getItem("interview_id");

    const fetchQuestion = async () => {
      try {
        const res = await axios.get(`/api/interview/${interviewId}/followup-question`);
        setQuestionText(res.data.question_text || "꼬리질문을 불러올 수 없습니다.");
      } catch (err) {
        console.error(err);
        setQuestionText("꼬리질문을 불러올 수 없습니다.");
      }
    };

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        alert("웹캠 접근 권한이 필요합니다.");
        console.error(err);
      }
    };

    fetchQuestion();
    startCamera();

    return () => {
      stopCamera();
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const formatTime = (seconds) => {
    const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");
    return `${mins}:${secs}`;
  };

  const startRecording = () => {
    const stream = videoRef.current?.srcObject;
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm" });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorderRef.current = mediaRecorder;
    recordedChunksRef.current = [];
    mediaRecorder.start();
    setIsRecording(true);

    intervalRef.current = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.onstop = async () => {
      stopCamera();

      const originalBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });
      try {
        const fixedBlob = await fixWebmDuration(originalBlob);
        const formData = new FormData();
        const interviewId = localStorage.getItem("interview_id");
        formData.append("file", fixedBlob, "followup.webm");

        await axios.post(
          `/api/interview/${interviewId}/FOLLOWUP/answer-video`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        await new Promise((r) => setTimeout(r, 100)); // 🔧 타이밍 안정화
        navigate("/interview/feedback");
      } catch (err) {
        alert("영상 업로드 실패");
        console.error(err);
      }
    };

    mediaRecorderRef.current.stop();
    setIsRecording(false);
    clearInterval(intervalRef.current);
  };

  const togglePause = () => {
    if (!mediaRecorderRef.current) return;
    if (isPaused) {
      mediaRecorderRef.current.resume();
      intervalRef.current = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
      setIsPaused(false);
    } else {
      mediaRecorderRef.current.pause();
      clearInterval(intervalRef.current);
      setIsPaused(true);
    }
  };

  const handleExit = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
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

      {/* 영상 및 질문 */}
      <div className="flex flex-col items-center border-4 px-6 py-8 rounded-xl">
        <div className="flex gap-6 mb-4">
          <div className="flex flex-col items-center">
            <div className="w-[400px] h-[300px] bg-gray-600 rounded-md"></div>
            <p className="mt-2 text-sm font-medium">AI 면접관</p>
          </div>
          <div className="flex flex-col items-center">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="w-[400px] h-[300px] bg-black rounded-md"
            />
            <p className="mt-2 text-sm">
              <i className="fas fa-microphone text-teal-500"></i> {isRecording ? formatTime(elapsedTime) : ""}
            </p>
          </div>
        </div>

        <div className="bg-gray-100 w-full text-center py-4 px-4 rounded text-lg font-medium mb-4">
          {questionText}
        </div>

        {/* 버튼 */}
        <div className="flex gap-4">
          {!isRecording ? (
            <button onClick={startRecording} className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300">
              발화버튼
            </button>
          ) : (
            <>
              <button onClick={togglePause} className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300">
                {isPaused ? "재개" : "일시정지"}
              </button>
              <button onClick={stopRecording} className="bg-gray-200 px-5 py-2 rounded hover:bg-gray-300">
                발화종료
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default InterviewQ5;
