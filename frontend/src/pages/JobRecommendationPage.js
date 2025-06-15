import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MapPin, Search, User } from "lucide-react";

const JOBS_PER_PAGE = 9;
const PAGES_PER_GROUP = 5;

function JobRecommendationPage() {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [jobData, setJobData] = useState([]);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedJobs = localStorage.getItem("job_postings");
    const storedUser = localStorage.getItem("user_id");

    if (storedJobs) {
      try {
        setJobData(JSON.parse(storedJobs));
      } catch (err) {
        console.error("채용공고 JSON 파싱 오류:", err);
      }
    }

    if (storedUser) {
      setUserName(storedUser);
    }
  }, []);

  const totalPages = Math.ceil(jobData.length / JOBS_PER_PAGE);

  const getCurrentPageJobs = () => {
    const start = (currentPage - 1) * JOBS_PER_PAGE;
    return jobData.slice(start, start + JOBS_PER_PAGE);
  };

  const getPageGroup = () => {
    const start = Math.floor((currentPage - 1) / PAGES_PER_GROUP) * PAGES_PER_GROUP + 1;
    return Array.from({ length: Math.min(PAGES_PER_GROUP, totalPages - start + 1) }, (_, i) => start + i);
  };

  const handlePageClick = (page) => setCurrentPage(page);
  const handlePrevGroup = () => {
    const prevStart = Math.max(1, Math.floor((currentPage - 1) / PAGES_PER_GROUP) * PAGES_PER_GROUP - PAGES_PER_GROUP + 1);
    setCurrentPage(prevStart);
  };
  const handleNextGroup = () => {
    const nextStart = Math.min(totalPages, Math.floor((currentPage - 1) / PAGES_PER_GROUP) * PAGES_PER_GROUP + PAGES_PER_GROUP + 1);
    setCurrentPage(nextStart);
  };

  return (
    <div className="min-h-screen bg-white-50 px-4 py-10">
      <div className="max-w-6xl mx-auto text-center mt-5 mb-5">
        <img
          src="/images/Logo_image.png"
          alt="logo"
          className="w-[400px] mx-auto mb-7 cursor-pointer"
          onClick={() => navigate("/")}
        />
        <h2 className="text-2xl font-semibold">
          {userName}님을 위한 추천공고, 놓치지 마세요!
        </h2>
      </div>

      <div className="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {getCurrentPageJobs().map((job, index) => (
          <div
            key={index}
            className="bg-gray-100 rounded-xl shadow border p-5 text-left hover:shadow-md transition"
          >
            <h3 className="text-lg font-semibold mb-2">{job.title}</h3>
            <p className="text-sm mb-1">{job.corporation}</p>
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <MapPin className="w-4 h-4 mr-1" />
              {job.location || "지역 정보 없음"}
            </div>
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <Search className="w-4 h-4 mr-1" />
              {job.keyword || "키워드 없음"}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <User className="w-4 h-4 mr-1" />
              신입/경력
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-2 mt-10">
        {currentPage > PAGES_PER_GROUP && (
          <button onClick={handlePrevGroup} className="px-3 py-1 border rounded">
            이전
          </button>
        )}
        {getPageGroup().map((page) => (
          <button
            key={page}
            onClick={() => handlePageClick(page)}
            className={`px-3 py-1 border rounded ${page === currentPage ? "bg-blue-500 text-white" : ""}`}
          >
            {page}
          </button>
        ))}
        {Math.floor((currentPage - 1) / PAGES_PER_GROUP) < Math.floor((totalPages - 1) / PAGES_PER_GROUP) && (
          <button onClick={handleNextGroup} className="px-3 py-1 border rounded">
            다음
          </button>
        )}
      </div>
    </div>
  );
}

export default JobRecommendationPage;
