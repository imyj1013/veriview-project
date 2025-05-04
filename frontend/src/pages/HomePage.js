// src/pages/HomePage.js
import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center relative px-6">
      {/* 상단 로그인 / 회원가입 */}
      <div className="absolute top-10 right-10 space-x-6 text-sm font-medium text-gray-700">
        <button onClick={() => navigate("/login")} className="hover:underline">
          로그인
        </button>
        <button className="hover:underline">회원가입</button>
      </div>

      {/* 로고 */}
      <div className="text-center mb-12">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="mx-auto w-[500px] mb-2"
        />
      </div>

      {/* 버튼 3개 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
        <HomeButton
          title="AI 토론면접"
          icon="/images/icon_debate.png"
          onClick={() => navigate("/debate-description")}
        />
        <HomeButton
          title="AI 개인면접"
          icon="/images/icon_personal.png"
          onClick={() => navigate("/personal")}
        />
        <HomeButton
          title="기업 추천"
          icon="/images/icon_company.png"
            onClick={() => alert("아직 준비중입니다")} 
        />
      </div>
    </div>
  );
}

function HomeButton({ title, icon, onClick }) {
  return (
    <div
      onClick={onClick}
      className="w-[200px] h-[200px] cursor-pointer hover:scale-105 transition"
    >
      <img src={icon} alt={title} className="w-[210px] h-[210px] mb-0" />
    </div>
  );
}

export default HomePage;
