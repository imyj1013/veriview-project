import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function PersonalInterviewForm() {
    const navigate = useNavigate();
  const [gender, setGender] = useState(null);
  const [job, setJob] = useState(null);
  const [career, setCareer] = useState(null);

  const jobOptions = [
    "경영/사무",
    "영업/판매",
    "공공/서비스",
    "ICT",
    "R&D",
    "생산/정비",
    "예술/디자인",
  ];

  return (
    <div className="min-h-screen bg-white py-12 px-4 flex flex-col items-center">
      {/* 로고 */}
      <img
        src="/images/Logo_image.png"
        alt="logo"
        className="w-[400px] mb-10 cursor-pointer"
        onClick={() => navigate("/")}
      />

      <form className="w-full max-w-2xl bg-white p-10 rounded-xl shadow space-y-8">
        {/* 이름 */}
        <div>
          <label className="block mb-2 font-semibold">이름</label>
          <input
            type="text"
            placeholder="이름을 입력하세요"
            className="w-full border border-gray-300 rounded px-4 py-2"
          />
        </div>

        {/* 생년월일 */}
        <div>
          <label className="block mb-2 font-semibold">생년월일</label>
          <input
            type="text"
            placeholder="ex) 20021030"
            className="w-full border border-gray-300 rounded px-4 py-2"
          />
        </div>

        {/* 성별 */}
        <div>
          <label className="block mb-2 font-semibold">성별</label>
          <div className="flex gap-4">
            {["남자", "여자"].map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setGender(g)}
                className={`border px-4 py-2 rounded ${
                  gender === g
                    ? "bg-blue-600 text-white"
                    : "bg-white text-gray-800"
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {/* 학력사항 */}
        <div>
          <label className="block mb-2 font-semibold">학력사항</label>
          <div className="grid grid-cols-2 gap-4">
            <select className="border border-gray-300 rounded px-4 py-2">
              <option>최종학력</option>
              <option>초등학교</option>
              <option>중학교</option>
              <option>고등학교</option>
              <option>대학교(2,3년제)</option>
              <option>대학교(4년제)</option>
              <option>대학원</option>
            </select>
            <select className="border border-gray-300 rounded px-4 py-2">
              <option>상태</option>
              <option>재학</option>
              <option>졸업</option>
              <option>중퇴</option>
            </select>
          </div>
        </div>

        {/* 희망직무 */}
        <div>
          <label className="block mb-2 font-semibold">희망직무</label>
          <div className="flex flex-wrap gap-2">
            {jobOptions.map((j) => (
              <button
                key={j}
                type="button"
                onClick={() => setJob(j)}
                className={`px-4 py-2 rounded border ${
                  job === j
                    ? "bg-blue-600 text-white"
                    : "bg-white text-gray-800"
                }`}
              >
                {j}
              </button>
            ))}
          </div>
        </div>

        {/* 경력사항 */}
        <div>
          <label className="block mb-2 font-semibold">경력사항</label>
          <div className="flex gap-4">
            {["신입", "경력"].map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCareer(c)}
                className={`border px-4 py-2 rounded ${
                  career === c
                    ? "bg-blue-600 text-white"
                    : "bg-white text-gray-800"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* 직무관련경험서술 */}
        <div>
          <label className="block mb-2 font-semibold">직무관련경험서술</label>
          <textarea
            placeholder="직무관련 경험을 서술하세요."
            className="w-full h-28 border border-gray-300 rounded px-4 py-2"
          />
        </div>

        {/* 보유기술 */}
        <div>
          <label className="block mb-2 font-semibold">보유기술</label>
          <textarea
            placeholder="보유하고 있는 기술을 서술하세요."
            className="w-full h-28 border border-gray-300 rounded px-4 py-2"
          />
        </div>

        {/* 강점/가치관 */}
        <div>
          <label className="block mb-2 font-semibold">강점/가치관</label>
          <textarea
            placeholder="자신의 강점과 가치관을 서술하세요."
            className="w-full h-28 border border-gray-300 rounded px-4 py-2"
          />
        </div>

        {/* 제출 버튼 */}
        <div className="text-center">
          <button
            type="submit"
            onClick={() => navigate("/interview/intro")}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            완료
          </button>
        </div>
      </form>
    </div>
  );
}

export default PersonalInterviewForm;
