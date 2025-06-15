// src/pages/InterviewFeedbackPage.js

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function InterviewFeedbackPage() {
  const navigate = useNavigate();
  const [feedbackData, setFeedbackData] = useState([]);

  useEffect(() => {
    // ✅ 모든 비디오 스트림 정리 함수
    const cleanupTracks = () => {
      try {
        const videos = document.querySelectorAll("video");
        videos.forEach((video) => {
          const stream = video.srcObject;
          if (stream instanceof MediaStream) {
            stream.getTracks().forEach((track) => {
              try {
                track.stop();
              } catch (err) {
                console.warn("트랙 중지 실패", err);
              }
            });
            video.srcObject = null;
          }
        });
      } catch (err) {
        console.warn("스트림 정리 중 에러 발생", err);
      }
    };

    cleanupTracks();       // ✅ 진입 시 웹캠 정리
    return cleanupTracks;  // ✅ 이탈 시도 정리 보장
  }, []);

  useEffect(() => {
    const fetchFeedback = async () => {
      const interviewId = localStorage.getItem("interview_id");
      try {
        const res = await axios.get(`/api/interview/${interviewId}/feedback`);
        const formatted = res.data.interview_feedback.map((item, idx) => ({
          type: `Q${idx + 1}.`,
          question_type: item.question_type,
          question: item.question_text,
          answer: item.answer_text,
          scores: {
            content: { value: item.content_score, feedback: item.content_feedback },
            voice: { value: item.voice_score, feedback: item.voice_feedback },
            behavior: { value: item.action_score, feedback: item.action_feedback },
          },
          feedback: item.feedback,
        }));
        setFeedbackData(formatted);
      } catch (err) {
        console.error("피드백 불러오기 실패", err);
      }
    };
    fetchFeedback();
  }, []);

  const renderStars = (score) => {
    const fullStars = Math.round(score);
    return (
      <span className="text-yellow-400">
        {"★".repeat(fullStars)}
        <span className="text-gray-300">{"★".repeat(5 - fullStars)}</span>
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      {/* 상단 바 */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-8">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[240px] cursor-pointer"
          onClick={() => navigate("/")}
        />
        <button
          onClick={() => navigate("/")}
          className="bg-gray-100 px-6 py-2 rounded hover:bg-gray-200"
        >
          나가기
        </button>
      </div>

      {/* 피드백 섹션 */}
      {feedbackData.map((item, index) => (
        <div key={index} className="w-full max-w-4xl border-t border-gray-300 pt-6 mb-16">
          <h2 className="text-lg font-bold mb-2">질문유형 : {item.question_type}</h2>

          <table className="table-fixed w-full border border-gray-300 text-sm mb-6">
            <tbody>
              <tr className="border-b">
                <td className="w-28 font-semibold bg-gray-50 p-2">질문</td>
                <td className="p-2">{item.question}</td>
              </tr>
              <tr className="border-b">
                <td className="font-semibold bg-gray-50 p-2 align-top">사용자 답변</td>
                <td className="p-2 whitespace-pre-line">{item.answer}</td>
              </tr>
              <tr className="border-b">
                <td className="font-semibold bg-gray-50 p-2 align-top">피드백</td>
                <td className="p-2 whitespace-pre-line">{item.feedback}</td>
              </tr>
            </tbody>
          </table>

          <table className="table-fixed w-full border border-gray-300 text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="w-24 py-2">점수</th>
                <th className="w-48 py-2">평가항목</th>
                <th className="py-2">피드백</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t">
                <td className="text-center py-2">
                  {renderStars(item.scores.content.value)} ({item.scores.content.value})
                </td>
                <td className="text-center">내용 점수</td>
                <td className="px-3 py-2">{item.scores.content.feedback}</td>
              </tr>
              <tr className="border-t">
                <td className="text-center py-2">
                  {renderStars(item.scores.voice.value)} ({item.scores.voice.value})
                </td>
                <td className="text-center">목소리 점수</td>
                <td className="px-3 py-2">{item.scores.voice.feedback}</td>
              </tr>
              <tr className="border-t">
                <td className="text-center py-2">
                  {renderStars(item.scores.behavior.value)} ({item.scores.behavior.value})
                </td>
                <td className="text-center">자세/행동 점수</td>
                <td className="px-3 py-2">{item.scores.behavior.feedback}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

export default InterviewFeedbackPage;
