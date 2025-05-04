import React from "react";

function LoginPage() {
  return (
    <div className="min-h-screen bg-[#F5F5F5] flex flex-col items-center justify-center relative px-6">
      {/* 상단 로그인 / 회원가입 */}
      <div className="absolute top-10 right-10 space-x-6 text-sm font-medium text-gray-700">
        <button className="hover:underline">로그인</button>
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

      {/* 로그인 폼 */}
      <form className="flex flex-col items-center space-y-4">
        <input
          type="text"
          placeholder="ID"
          className="border px-4 py-2 rounded-lg w-80 shadow-sm"
        />
        <input
          type="password"
          placeholder="비밀번호"
          className="border px-4 py-2 rounded-lg w-80 shadow-sm"
        />
        <button
          type="submit"
          className="bg-white border px-6 py-2 rounded-lg shadow hover:shadow-md"
        >
          로그인
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
