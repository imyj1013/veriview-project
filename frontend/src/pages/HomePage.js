import React from "react";

function HomePage() {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4 pt-10">
      {/* 로그인 / 회원가입 */}
      <div className="absolute top-16 right-16 space-x-6 text-sm font-medium">
        <button className="text-gray-700 hover:underline">로그인</button>
        <button className="text-gray-700 hover:underline">회원가입</button>
      </div>

      {/* 로고 */}
      <div className="text-center mb-12">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="mx-auto w-828 H-164 mb-2"
        />
        <p className="text-gray-500 tracking-widest text-sm leading-snug">
         
        </p>
      </div>

      {/* 버튼들 */}
      {/* 예시 */}

      <div className="w-full max-w-5xl px-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 justify-items-center">
        <HomeButton  icon="/images/icon_debate.png" />
        <HomeButton  icon="/images/icon_personal.png" />
        <HomeButton  icon="/images/icon_company.png" />
      </div>
    </div>
  );
}

function HomeButton({ title, icon }) {
  return (
    <div className="w-280 h-280 flex flex-col items-center justify-center border border-gray-300 rounded-3xl shadow-md hover:shadow-xl transition cursor-pointer bg-white">
      <img src={icon} alt={title} className="w-280 h-280 object-contain mb-0" />
      <p className="text-gray-800 font-semibold text-sm">{title}</p>
    </div>
  );
}

export default HomePage;
