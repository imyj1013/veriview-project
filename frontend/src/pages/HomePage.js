import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id"); 
    setIsLoggedIn(false);
    navigate("/login"); 
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center relative px-6">
      {/* 로그인 / 로그아웃 */}
      <div className="absolute top-10 right-10 space-x-6 text-sm font-medium text-gray-700">
        {isLoggedIn ? (
          <button onClick={handleLogout} className="hover:underline">
            로그아웃
          </button>
        ) : (
          <>
            <button onClick={() => navigate("/login")} className="hover:underline">
              로그인
            </button>
            <button onClick={() => navigate("/signup")} className="hover:underline">
              회원가입
            </button>
          </>
        )}
      </div>

      {/* 로고 */}
      <div
        className="text-center mb-12 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="mx-auto w-[500px] mb-2"
        />
      </div>

      {/* 홈 버튼들 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
        <HomeButton
          title="AI 토론면접"
          icon="/images/icon_debate.png"
          onClick={() => navigate("/debate-intro")}
        />
        <HomeButton
          title="AI 개인면접"
          icon="/images/icon_personal.png"
          onClick={() => navigate("interview/InterviewIntroPage")}
        />
        <HomeButton
          title="기업 추천"
          icon="/images/icon_company.png"
          onClick={() => navigate("recruitment/JobRecommendationForm")}
        />
      </div>
    </div>
  );
}

function HomeButton({ title, icon, onClick }) {
  return (
    <div
      onClick={onClick}
      className="w-[200px] h-[200px] cursor-pointer hover:scale-105 transition text-center"
    >
      <img src={icon} alt={title} className="w-[250px] h-[250px] mb-0" />
      <p className="mt-2 text-lg font-medium"></p>
    </div>
  );
}

export default HomePage;
