// src/pages/InterviewFeedbackPage.js

import React from "react";
import { useNavigate } from "react-router-dom";

function InterviewFeedbackPage() {
  const navigate = useNavigate();

  const feedbackData = [
    {
      type: "Q1.",
      question: "자기소개를 해주세요.",
      answer: "안녕하세요.",
      scores: {
        content: { stars: 4, value: 4.1 },
        voice: { stars: 4, value: 4.3 },
        behavior: { stars: 4, value: 3.7 },
      },
      feedback: "좋은 내용이었지만 시선이 조금 불안정하게 보입니다.",
    },
    {
      type: "Q2.",
      question: "당신이 이 직무에 적합한 이유는 무엇인가요?",
      answer: "장점: Zoom이나 Slack 같은 협업 도구가 발전했지만, 비정형적 대화나 우연한 아이디어 공유는 여전히 대면 환경에서 더 자주 일어납니다. 예를 들어 사무실 복도에서 마주친 짧은 대화가 혁신적인 아이디어로 이어지는 경우도 많습니다. 또한 재택 환경은 가족 간섭, 인터넷 불안정 등 다양한 변수에 노출되며, 이는 특히 신입 직원이나 자기 주도력이 약한 사람에게 치명적입니다.”",
      scores: {
        content: { stars: 3, value: 3.0 },
        voice: { stars: 4, value: 4.0 },
        behavior: { stars: 4, value: 4.0 },
      },
      feedback:
        "Zoom이나 Slack 같은 협업 도구가 발전했지만, 비정형적 대화나 우연한 아이디어 공유는 여전히 대면 환경에서 더 자주 일어납니다. 예를 들어 사무실 복도에서 마주친 짧은 대화가 혁신적인 아이디어로 이어지는 경우도 많습니다. 또한 재택 환경은 가족 간섭, 인터넷 불안정 등 다양한 변수에 노출되며, 이는 특히 신입 직원이나 자기 주도력이 약한 사람에게 치명적입니다.”",
    },
    {
        type: "Q3.",
        question: "당신이 이 직무에 적합한 이유는 무엇인가요?",
        answer: "장점: 협업 도구의 한계와 환경 요인을 잘 지적함...",
        scores: {
          content: { stars: 3, value: 3.0 },
          voice: { stars: 4, value: 4.0 },
          behavior: { stars: 4, value: 4.0 },
        },
        feedback:
          "Zoom이나 Slack 같은 협업 도구가 발전했지만, 비정형적 대화나 우연한 아이디어 공유는 아직 어렵습니다...",
      },
      {
        type: "Q4.",
        question: "당신이 이 직무에 적합한 이유는 무엇인가요?",
        answer: "장점: 협업 도구의 한계와 환경 요인을 잘 지적함...",
        scores: {
          content: { stars: 3, value: 3.0 },
          voice: { stars: 4, value: 4.0 },
          behavior: { stars: 4, value: 4.0 },
        },
        feedback:
          "Zoom이나 Slack 같은 협업 도구가 발전했지만, 비정형적 대화나 우연한 아이디어 공유는 아직 어렵습니다...",
      },
  ];

  const renderStars = (count) =>
    "★★★★★☆☆☆☆☆".slice(5 - count, 10 - count);

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
          <h2 className="text-xl font-semibold mb-6">
            {item.type}
          </h2>
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
            <span className="inline-block w-28 ">
              {renderStars(item.scores.content.stars)} ({item.scores.content.value}/5)
            </span>
          </div>
          <div className="mb-5">
            <span className="inline-block w-28 font-semibold align-top">목소리 점수</span>
            <span className="inline-block w-28">
              {renderStars(item.scores.voice.stars)} ({item.scores.voice.value}/5)
            </span>
          </div>
          <div className="mb-9">
            <span className="inline-block w-28 font-semibold align-top" >자세/행동 점수</span>
            <span className="inline-block w-28">
              {renderStars(item.scores.behavior.stars)} ({item.scores.behavior.value}/5)
            </span>
          </div>
          <div className="mt-4">
            <span className="inline-block w-28 font-semibold align-top">피드백</span>
            <span className="inline-block max-w-xl">{item.feedback}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default InterviewFeedbackPage;
