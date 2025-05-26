import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const educationOptions = ["초등학교", "중학교", "고등학교", "대학교(2,3년제)", "대학교(4년제)", "대학원"];
  const statusOptions = ["재학", "졸업", "중퇴"];
  const experienceOptions = ["신입", "경력"];
  const employmentTypes = ["인턴", "정규직", "계약직"];
  const jobOptions = ["경영/사무", "영업/판매", "공공/서비스", "ICT", "R&D", "생산/정비", "예술/디자인"];
  const regionOptions = ["전국", "서울", "경기", "인천" , " 대전" , "세종", "충남", "충북", "광주", 
    , "전남" , "전북" , "대구" , " 경북" , "부산" , "울산" , "경남" , "강원", "제주"];

const regionSubRegions = {
  서울: [
    "전체", "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
    "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
    "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구",
    "중구", "중랑구"
  ],
  경기: [
    "전체", "가평군", "고양특례시", "과천시", "광명시", "광주시", "구리시", "군포시",
    "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시",
    "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인특례시",
    "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"
  ],
  인천: [
  "전체", "중구", "동구", "미추홀구", "연수구", "남동구", 
  "부평구", "계양구", "서구", "강화군", "옹진군"
],
대전: [
  "전체",  "동구", "중구", "서구", "유성구", "대덕구"
 ],
  강원: [
  "전체", "강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군",
  "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"
  ],
   세종: ["조치원읍", "연기면", "연동면", "부강면", "금남면", "장군면", "연서면", "전의면", 
    "전동면", "소정면", "한솔동", "새롬동", "도담동", "아름동", "종촌동", "고운동", "보람동", 
    "대평동", "소담동", "반곡동", "집현동", "합강동"
], 
충남: [
      "전체", "천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시",
      "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"
    ],
    충북: [
      "전체", "청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "증평군",
      "진천군", "괴산군", "음성군", "단양군"
    ],
    광주: ["전체", "동구", "서구", "남구", "북구", "광산구"],
    전남: [
      "전체", "목포시", "여수시", "순천시", "나주시", "광양시", "담양군", "곡성군", "구례군",
      "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", "영암군", "무안군",
      "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"
    ],
    전북: [
      "전체", "전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", "완주군",
      "진안군", "무주군", "장수군", "임실군", "순창군", "고창군", "부안군"
    ],
    대구: ["전체", "중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"],
    경북: [
      "전체", "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시",
      "상주시", "문경시", "경산시", "군위군", "의성군", "청송군", "영양군", "영덕군",
      "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군", "울진군", "울릉군"
    ],
    부산: ["전체", "중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구",
      "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"
    ],
    울산: ["전체", "중구", "남구", "동구", "북구", "울주군"],
    경남: [
      "전체", "창원시", "진주시", "통영시", "사천시", "김해시", "밀양시", "거제시", "양산시",
      "의령군", "함안군", "창녕군", "고성군", "남해군", "하동군", "산청군", "함양군",
      "거창군", "합천군"
    ],
    강원: [
      "전체", "강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군",
      "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"
    ],
    제주: ["전체", "제주시", "서귀포시"],

  전국: ["전국"]
};

const JobRecommendationForm = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    education: "",
    status: "",
    major: "",
    doubleMajor: "",
    experience: "",
    employment: "",
    job: "",
    region: "",
    subregion: "",
    certificate: "",
    skills: "",
  });
  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("로그인이 필요합니다.");
      navigate("/login");
    }
  }, []);

  
  const handleSubmit = async (e) => {
    e.preventDefault();

    const userId = localStorage.getItem("user_id");
    if (!userId) {
      alert("로그인이 필요합니다.");
      navigate("/login");
      return;
    }
    const fullEducation = `${form.education} ${form.status}`.trim();
    const location = form.region === "전국" ? "전국" : `${form.region} ${form.subregion}`.trim();
    localStorage.setItem("user_location", location); //location 저장
    
    const payload = {
      user_id: userId,
      education: fullEducation,
      major: form.major,
      double_major: form.doubleMajor,
      workexperience: form.experience,
      qualification: form.certificate,
      tech_stack: form.skills,
      location: location,
      category: form.job,
      employmenttype: form.type,
    };

    try {
      const response = await axios.post("/api/recruitment/start", payload);
      localStorage.setItem("job_postings", JSON.stringify(response.data.posting));
      navigate("/recruitment/JobRecommendationPage");
    } catch (error) {
      console.error("채용공고 추천 실패:", error);
      alert("요청에 실패했습니다.");
    }
  };


  const handleRegionChange = (e) => {
    const selected = e.target.value;
    setForm({ ...form, region: selected, subregion: "" });
  };

  return (
    <div className="min-h-screen bg-white py-10 px-4">
      <div className="max-w-3xl mx-auto bg-white p-8 shadow rounded">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[400px] mx-auto mb-16 cursor-pointer"
          onClick={() => navigate("/")}
        />

        {/* 학력사항 */}
        <div className="mb-12">
          <p className="font-bold mb-6">학력사항*</p>
          <div className="flex items-center mb-2">
            <label className="w-24 font-medium text-right pr-4 ">최종학력*</label>
            <div className="flex gap-4 w-full">
              <select
                value={form.education}
                onChange={(e) => setForm({ ...form, education: e.target.value })}
                className="border px-3 py-2 rounded w-1/2"
              >
                <option value="">학교</option>
                {educationOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                className="border px-3 py-2 rounded w-1/2"
              >
                <option value="">상태</option>
                {statusOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center mb-2">
            <label className="w-24 font-medium text-right pr-4">전공*</label>
            <input
              type="text"
              className="border w-full px-3 py-2 rounded"
              value={form.major}
              onChange={(e) => setForm({ ...form, major: e.target.value })}
              placeholder="전공"
            />
          </div>
          <div className="flex items-center">
            <label className="w-24 font-medium text-right pr-4">복수전공</label>
            <input
              type="text"
              className="border w-full px-3 py-2 rounded"
              value={form.doubleMajor}
              onChange={(e) => setForm({ ...form, doubleMajor: e.target.value })}
              placeholder="복수전공"
            />
          </div>
        </div>

        {/* 경력사항 */}
        <div className="mb-12 flex items-center gap-4">
            <p className="font-bold mb-">경력사항*</p>
          <div className="flex gap-2">
            {experienceOptions.map((exp) => (
              <button
                key={exp}
                type="button"
                className={`px-4 py-2 border rounded ${form.experience === exp ? "bg-blue-600 text-white" : ""}`}
                onClick={() => setForm({ ...form, experience: exp })}
              >
                {exp}
              </button>
            ))}
          </div>
        </div>

        {/* 고용형태 */}
        <div className="mb-12 flex items-center gap-4">
            <p className="font-bold mb-">고용형태*</p>
         
          <div className="flex gap-2">
            {employmentTypes.map((type) => (
              <button
                key={type}
                type="button"
                className={`px-4 py-2 border rounded ${form.type === type ? "bg-blue-600 text-white" : ""}`}
                onClick={() => setForm({ ...form, type: type })}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* 선호직무 */}
        <div className="mb-12">
          <label className="block font-bold mb-2">선호직무*</label>
          <div className="grid grid-cols-4 gap-2">
            {jobOptions.map((job) => (
              <button
                key={job}
                type="button"
                className={`px-3 py-2 border rounded text-sm ${form.job === job ? "bg-blue-600 text-white" : ""}`}
                onClick={() => setForm({ ...form, job })}
              >
                {job}
              </button>
            ))}
          </div>
        </div>

        {/* 근무지역 */}
        <div className="mb-12">
         <p className="font-bold mb-4">근무지역*</p>
          <select
            className="border px-3 py-2 rounded w-1/2"
            value={form.region}
            onChange={handleRegionChange}
          >
            <option value="">시/도 선택</option>
            {regionOptions.map((region) => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>

          <select
            className="border px-3 py-2 rounded w-1/2"
            value={form.subregion}
            onChange={(e) => setForm({ ...form, subregion: e.target.value })}
            disabled={!form.region || regionSubRegions[form.region] === undefined}
          >
            <option value="">하위지역 선택</option>
            {regionSubRegions[form.region]?.map((sub) => (
              <option key={sub} value={sub}>{sub}</option>
            ))}
          </select>
        </div>

        {/* 자격증 */}
        <div className="mb-12  items-start gap-4">
            
          <label className="block w-24 font-bold  mb-3 ">자격증</label>
          <textarea
            placeholder="ex) 정보처리기사"
            className="border w-full px-3 py-2 rounded h-20"
            value={form.certificate}
            onChange={(e) => setForm({ ...form, certificate: e.target.value })}
          />
        </div>

        {/* 보유기술 */}
        <div className="mb-12  items-start gap-4">
          <label className="block w-24 font-bold mb-3">보유기술</label>
          <textarea
            placeholder="보유하고 있는 기술을 서술하세요."
            className="border w-full px-3 py-2 rounded h-28"
            value={form.skills}
            onChange={(e) => setForm({ ...form, skills: e.target.value })}
          />
        </div>

        {/* 제출 버튼 */}
        <div className="text-center">
          <button
            onClick={handleSubmit}
            className="bg-blue-600 text-white px-6 py-2 border rounded hover:bg-blue-700"
          >
            완료
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobRecommendationForm;
