// src/pages/InterviewFeedbackPage.js

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function InterviewFeedbackPage() {
  const navigate = useNavigate();
  const [feedbackData, setFeedbackData] = useState([]);

  useEffect(() => {
    const fetchFeedback = async () => {
      const interviewId = localStorage.getItem("interview_id");
      try {
        const res = await axios.get(`/api/interview/${interviewId}/feedback`);
        const formatted = res.data.interview_feedback.map((item, idx) => ({
          type: `Q${idx + 1}.`,
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
    const stars = Math.round(score);
    return "★★★★★☆☆☆☆☆".slice(5 - stars, 10 - stars);
  };

  return (
    <div className="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
      {/* 로고 + 나가기 */}
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
        <div
          key={index}
          className="w-full max-w-4xl border-t border-gray-300 pt-6 mb-16"
        >
          <h2 className="text-xl font-semibold mb-6">{item.type}</h2>

          <div className="mb-5">
            <span className="inline-block w-28 font-semibold">질문</span>
            <span>“{item.question}”</span>
          </div>

          <div className="mb-5">
            <span className="inline-block w-28 font-semibold align-top">사용자 답변</span>
            <span className="inline-block max-w-xl">“{item.answer}”</span>
          </div>

          <div className="mb-5">
            <span className="inline-block w-28 font-semibold align-top">내용 점수</span>
            <div>
              <span className="inline-block w-28">
                {renderStars(item.scores.content.value)} ({item.scores.content.value}/5)
              </span>
              <p className="text-sm text-gray-600 mt-1 ml-28">{item.scores.content.feedback}</p>
            </div>
          </div>

          <div className="mb-5">
            <span className="inline-block w-28 font-semibold align-top">목소리 점수</span>
            <div>
              <span className="inline-block w-28">
                {renderStars(item.scores.voice.value)} ({item.scores.voice.value}/5)
              </span>
              <p className="text-sm text-gray-600 mt-1 ml-28">{item.scores.voice.feedback}</p>
            </div>
          </div>

          <div className="mb-9">
            <span className="inline-block w-28 font-semibold align-top">자세/행동 점수</span>
            <div>
              <span className="inline-block w-28">
                {renderStars(item.scores.behavior.value)} ({item.scores.behavior.value}/5)
              </span>
              <p className="text-sm text-gray-600 mt-1 ml-28">{item.scores.behavior.feedback}</p>
            </div>
          </div>

          <div className="mt-6">
            <span className="inline-block w-28 font-semibold align-top">종합 피드백</span>
            <span className="inline-block max-w-xl text-gray-800 text-base">{item.feedback}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default InterviewFeedbackPage;
