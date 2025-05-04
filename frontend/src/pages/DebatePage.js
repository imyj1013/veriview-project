import React from "react";
import { useNavigate } from "react-router-dom";

function DebatePage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-white flex flex-col items-center py-10 px-6">
      {/* 로고 */}
      <img src="/images/Logo_image.png" 
      alt="logo"
      className="w-[400px] mb-8 cursor-pointer"
      onClick={() => navigate("/")}
      />
      

      {/* 예시 질문/응답 박스 */}
      <div className="w-full max-w-3xl bg-gray-100 p-4 rounded-lg mb-4 text-center">
        <p className="text-gray-700 text-base font-medium">
          Q. 재택근무가 대면근무보다 효율적인가? (예시질문)
        </p>
      </div>

      <div className="w-full max-w-3xl bg-gray-100 p-6 rounded-lg mb-6 relative flex items-start gap-4">
        <img
          src="/images/Debate_image3.png"
          alt="왼쪽 사람"
          className="w-24 h-24 absolute left-[-150px] top-6"
        />
        <p className="text-gray-800 px-6 py-6 text-sm text-left leading-relaxed">
          A: “재택근무는 직원들의 업무 자율성을 높이고, 출퇴근 시간이 절약되어 업무 생산성이 향상됩니다.
          특히, IT 업계는 창의적인 직군에서는 조용한 환경에서 집중할 수 있어 더 좋은 결과를 만들 수 있습니다.
          또한, 원격 협업 도구가 발달하면서 소통의 문제도 최소화되었습니다.”
        </p>
        <img
          src="/images/Debate_image4.png"
          alt="오른쪽 사람"
          className="w-24 h-24 absolute right-[-150px] top-6"
        />
      </div>

      {/* 발화 버튼 */}
      <button className="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded-lg text-sm text-gray-800 transition">
        발화 버튼
      </button>
    </div>
  );
}

export default DebatePage;
