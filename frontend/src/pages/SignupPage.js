import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    user_id: "",
    password: "",
    name: "",
    email: "",
  });
  const [errors, setErrors] = useState({});
  const [idAvailable, setIdAvailable] = useState(null);
  const [idMessage, setIdMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: "" });

    if (e.target.name === "user_id") {
      setIdAvailable(null);
      setIdMessage("");
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!form.user_id.trim()) newErrors.user_id = "ID를 입력하세요.";
    if (!form.password || form.password.length < 4)
      newErrors.password = "비밀번호는 4자 이상 입력하세요.";
    if (!form.name) newErrors.name = "이름을 입력하세요.";
    if (!form.email || !form.email.includes("@"))
      newErrors.email = "이메일 형식이 올바르지 않습니다.";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleIdCheck = async () => {
    if (!form.user_id.trim()) {
      setIdAvailable(false);
      setIdMessage("ID를 입력해주세요.");
      return;
    }
    try {
      const res = await axios.get(`/api/auth/check-username/${form.user_id}`);
      if (res.data.available) {
        setIdAvailable(true);
        setIdMessage("사용 가능한 ID입니다.");
      } else {
        setIdAvailable(false);
        setIdMessage("이미 존재하는 ID입니다.");
      }
    } catch {
      setIdAvailable(false);
      setIdMessage("중복 확인 실패");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    if (idAvailable === false) {
      setErrors((prev) => ({ ...prev, user_id: "이미 존재하는 ID입니다." }));
      return;
    }

    try {
      const res = await axios.post("/api/auth/signup", form);
      alert(res.data.message || "회원가입 성공!");
      navigate("/login");
    } catch (err) {
      alert(err.response?.data?.error || "회원가입 실패");
    }
  };

  return (
    /* 로고 */
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4">
      <img
        src="/images/Logo_image.png"
        alt="logo"
       className="mx-auto w-[500px] mb-2 cursor-pointer"
        onClick={() => navigate("/")}
      />

      <form onSubmit={handleSubmit} className="w-full max-w-xs space-y-4 text-sm">
        {/* ID 입력 + 중복확인 */}
        <div className="flex gap-2">
          <input
            type="text"
            name="user_id"
            placeholder="ID"
            value={form.user_id}
            onChange={handleChange}
            className="w-2/3 border border-gray-300 px-4 py-2 rounded"
          />
          <button
            type="button"
            onClick={handleIdCheck}
            className="w-1/3 bg-gray-100 border border-gray-300 rounded"
          >
            중복확인
          </button>
        </div>
        {idMessage && (
          <p className={`text-sm ${idAvailable ? "text-green-600" : "text-red-500"}`}>
            {idMessage}
          </p>
        )}
        {errors.user_id && (
          <p className="text-sm text-red-500">{errors.user_id}</p>
        )}

        {/* 비밀번호, 이름, 이메일 */}
        <input
          type="password"
          name="password"
          placeholder="비밀번호"
          value={form.password}
          onChange={handleChange}
          className="w-full border border-gray-300 px-4 py-2 rounded"
        />
        {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}

        <input
          type="text"
          name="name"
          placeholder="이름"
          value={form.name}
          onChange={handleChange}
          className="w-full border border-gray-300 px-4 py-2 rounded"
        />
        {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}

        <input
          type="email"
          name="email"
          placeholder="이메일"
          value={form.email}
          onChange={handleChange}
          className="w-full border border-gray-300 px-4 py-2 rounded"
        />
        {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}

        <button
          type="submit"
          className="w-full bg-gray-100 border border-gray-300 py-2 rounded hover:shadow"
        >
          가입하기
        </button>
      </form>
    </div>
  );
}

export default SignupPage;
