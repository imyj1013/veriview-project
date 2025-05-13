import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

function DebateFeedbackPage() {
  const navigate = useNavigate();
  const { state } = useLocation(); // state.debateId
  const [feedbackData, setFeedbackData] = useState([]);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await axios.get(`/api/debate/${state.debateId}/feedback`);
        const raw = res.data.debate_feedback;

        const titles = ["입론", "반론", "재반론", "최종변론"];
        const keys = [
          "user_opening_text",
          "user_rebuttal_text",
          "user_counter_rebuttal_text",
          "user_closing_text",
        ];

        const parsed = raw.map((item, i) => {
          return {
            title: titles[i],
            userAnswer: item[keys[i]],
            feedback: item.feedback,
            sampleAnswer: item.sample_answer,
            scores: [
              { title: "협력적 태도", score: item.collaborative_score, comment: item.collaborative_feedback },
              { title: "의사소통능력", score: item.communication_score, comment: item.communication_feedback },
              { title: "적극성", score: item.initiative_score, comment: item.initiative_feedback },
              { title: "논리력", score: item.logic_score, comment: item.logic_feedback },
              { title: "문제해결력", score: item.problem_solving_score, comment: item.problem_solving_feedback },
            ],
          };
        });

        setFeedbackData(parsed);
      } catch (err) {
        console.error("피드백 데이터 불러오기 실패:", err);
      }
    };

    fetchFeedback();
  }, [state]);

  const renderStars = (score) =>
    "★".repeat(Math.round(score)) + "☆".repeat(5 - Math.round(score));

  return (
    <div className="min-h-screen bg-white py-10 flex flex-col items-center">
      {/* 로고, 나가기 */}
      <div className="w-full max-w-6xl flex justify-start items-center mb-8">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[240px] cursor-pointer"
          onClick={() => navigate("/")}
        />
        <button
          onClick={() => navigate("/")}
          className="ml-auto bg-gray-100 px-4 py-1 rounded hover:bg-gray-200"
        >
          나가기
        </button>
      </div>

      {/* 전체 피드백 */}
      <div className="w-full max-w-4xl px-3">
        {feedbackData.map((section, idx) => (
          <div key={idx} className="mb-12">
            <h2 className="text-2xl font-semibold mb-1">[{section.title}] 피드백</h2>
            <hr className="border-gray-300 mb-6" />

            <div className="mb-4">
              <h3 className="text-lg font-semibold">사용자 답변</h3>
              <div className="border rounded p-4 text-sm bg-white">
                {section.userAnswer}
              </div>
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold">피드백</h3>
              <div className="border rounded p-4 text-sm bg-white">
                {section.feedback}
              </div>
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold">모범답안</h3>
              <div className="border rounded p-4 text-sm bg-white whitespace-pre-wrap">
                {section.sampleAnswer}
              </div>
            </div>

            {/* 점수 표 */}
            <div className="border rounded-lg overflow-hidden">
              <div className="grid grid-cols-12 bg-gray-100 px-4 py-2 text-sm font-semibold">
                <div className="col-span-2">점수</div>
                <div className="col-span-3">평가항목</div>
                <div className="col-span-7">피드백</div>
              </div>
              {section.scores.map((item, i) => (
                <div
                  key={i}
                  className={`grid grid-cols-12 px-4 py-2 text-sm ${
                    i % 2 === 0 ? "bg-white" : "bg-gray-50"
                  }`}
                >
                  <div className="col-span-2">
                    {renderStars(item.score)} ({item.score?.toFixed(1)})
                  </div>
                  <div className="col-span-3">{item.title}</div>
                  <div className="col-span-7">{item.comment}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DebateFeedbackPage;
