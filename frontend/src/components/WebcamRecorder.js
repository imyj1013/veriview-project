// src/components/WebcamRecorder.js
import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

function WebcamRecorder({ onSave }) {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);

  const startRecording = () => {
    setRecordedChunks([]);
    const stream = webcamRef.current.stream;
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: "video/webm",
    });

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setRecordedChunks((prev) => [...prev, event.data]);
      }
    };

    mediaRecorderRef.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const saveVideo = () => {
    const blob = new Blob(recordedChunks, { type: "video/webm" });
    onSave(blob);
  };

  return (
    <div className="space-y-4">
      <Webcam
        audio={true}
        ref={webcamRef}
        mirrored
        className="rounded-lg shadow w-full max-w-md"
      />
      <div className="flex gap-4 justify-center">
        {!recording ? (
          <button onClick={startRecording} className="bg-blue-600 text-white px-4 py-2 rounded">
            녹화 시작
          </button>
        ) : (
          <button onClick={stopRecording} className="bg-red-500 text-white px-4 py-2 rounded">
            녹화 중지
          </button>
        )}
        {recordedChunks.length > 0 && (
          <button onClick={saveVideo} className="bg-green-600 text-white px-4 py-2 rounded">
            영상 저장 및 업로드
          </button>
        )}
      </div>
    </div>
  );
}

export default WebcamRecorder;
