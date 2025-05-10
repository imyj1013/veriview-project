import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';

const DebateRecorder = ({ debateId }) => {
  const webcamRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [videoBlob, setVideoBlob] = useState(null);
  const [uploading, setUploading] = useState(false);

  const startRecording = () => {
    const stream = webcamRef.current.video.srcObject;
    const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    const chunks = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setVideoBlob(blob);
    };

    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const uploadVideo = async () => {
    if (!videoBlob) return;
    setUploading(true);

    const formData = new FormData();
    formData.append('video', videoBlob, 'opening.webm');

    try {
      const response = await fetch(`/api/debate/${debateId}/opening-video`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      console.log('Upload success:', result);
      alert('업로드 완료!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('업로드 실패');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <Webcam ref={webcamRef} audio={true} />
      <div className="flex gap-4 mt-2">
        {!recording ? (
          <button onClick={startRecording} className="px-4 py-2 bg-green-600 text-white rounded">
            녹화 시작
          </button>
        ) : (
          <button onClick={stopRecording} className="px-4 py-2 bg-red-600 text-white rounded">
            녹화 중지
          </button>
        )}
        <button
          onClick={uploadVideo}
          disabled={!videoBlob || uploading}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          {uploading ? '업로드 중...' : '영상 업로드'}
        </button>
      </div>
      {videoBlob && (
        <video
          controls
          src={URL.createObjectURL(videoBlob)}
          className="mt-4 max-w-md rounded shadow"
        />
      )}
    </div>
  );
};

export default DebateRecorder;
