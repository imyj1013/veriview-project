import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import axios from "axios";

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    user_id: "",
    password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(""); // 입력 변경 시 에러 초기화
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("/api/auth/login", {
        user_id: form.user_id,
        password: form.password,
      });

      login(res.data.access_token); // 토큰 저장
      navigate("/"); // 홈으로 이동
    } catch (err) {
      setError(
        err.response?.data?.error || "아이디 또는 비밀번호가 잘못되었습니다."
      );
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4 py-10">
      {/* 상단 로고 */}
      <img
        src="/images/Logo_image.png"
        alt="logo"
        className="w-72 mb-10 cursor-pointer"
        onClick={() => navigate("/")}
      />

      {/* 로그인 폼 */}
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <input
          type="text"
          name="user_id"
          placeholder="ID"
          value={form.user_id}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />
        <input
          type="password"
          name="password"
          placeholder="비밀번호"
          value={form.password}
          onChange={handleChange}
          className="w-full border px-4 py-2 rounded"
        />

        {error && <p className="text-sm text-red-500">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          로그인
        </button>

        <div className="text-center mt-4">
          <button
            type="button"
            className="text-sm text-gray-600 hover:underline"
            onClick={() => navigate("/signup")}
          >
            회원가입
          </button>
        </div>
      </form>
    </div>
  );
}

export default LoginPage;
