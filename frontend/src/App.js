// src/App.js

import { Routes, Route } from "react-router-dom";

// 기본 페이지
import HomePage from "./pages/HomePage";
import SignupPage from "./pages/SignupPage";
import LoginPage from "./pages/LoginPage";
import InterviewPortfolioPage from "./pages/InterviewPortfolioPage";

// 토론면접 페이지
import DebateIntroPage from "./pages/DebateIntroPage"; //설명페이지
import DebateStartPage from "./pages/DebateStartPage"; //주제, 입장 페이지
import DebateOpeningPage from "./pages/DebateOpeningPage"; //사용자의 입론페이지
import AIOpeningPage from "./pages/AIOpeningPage"; //AI토론자의 입론페이지
import DebateRebuttalPage from "./pages/DebateRebuttalPage"; //사용자의 반론페이지
import AIRebuttalPage from "./pages/AIRebuttalPage"; //AI토론자의 반론페이지
import DebateCounterPage from "./pages/DebateCounterPage"; //사용자의 재반론 페이지
import AICounterPage from "./pages/AICounterPage"; //AI토론자의 재반론 페이지
import DebateClosingPage from "./pages/DebateClosingPage"; //사용자의 최종변론 페이지
import AIClosingPage from "./pages/AIClosingPage"; //AI 토론자의 최종변론 페이지
import DebateFeedbackPage from "./pages/DebateFeedbackPage"; //피드백 페이지
//개인면접 페이지

import InterviewIntroPage from "./pages/InterviewIntroPage"; //설명페이지
import InterviewQuestionPage from "./pages/InterviewQuestionPage"; //시작페이지
import InterviewEndPage from "./pages/InterviewEndPage"; //시작페이지
import InterviewFeedbackPage from "./pages/InterviewFeedbackPage"; //시작페이지

// 개인면접 질문별 페이지
import InterviewQ1 from "./pages/InterviewQ1";
import InterviewQ2 from "./pages/InterviewQ2";
import InterviewQ3 from "./pages/InterviewQ3";
import InterviewQ4 from "./pages/InterviewQ4";
import InterviewQ5 from "./pages/InterviewQ5";

//공고추천

function App() {
  return (
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        {/* 토론면접 */}
        <Route path="/debate-intro" element={<DebateIntroPage />} />
        <Route path="/debate-start" element={<DebateStartPage />} />
        <Route path="/debate/opening" element={<DebateOpeningPage />} />
        <Route path="/debate/ai-opening" element={<AIOpeningPage />} />
        <Route path="/debate/user-rebuttal" element={<DebateRebuttalPage />} />
        <Route path="/debate/ai-rebuttal" element={<AIRebuttalPage />} />
        <Route path="/debate/user-counter" element={<DebateCounterPage />} />
        <Route path="/debate/ai-counter" element={<AICounterPage />} />
        <Route path="/debate/user-closing" element={<DebateClosingPage />} />
        <Route path="/debate/ai-closing" element={<AIClosingPage />} />
        <Route path="/debate/feedback" element={<DebateFeedbackPage />} />
        {/* 개인면접 */}
        <Route path="/interview/portfolio" element={<InterviewPortfolioPage />} />
        <Route path="/interview/intro" element={<InterviewIntroPage />} />
        <Route path="/interview/question/:step" element={<InterviewQuestionPage />} />
        <Route path="/interview/end" element={<InterviewEndPage />} />
        <Route path="/interview/feedback" element={<InterviewFeedbackPage />} />
        <Route path="/interview/q1" element={<InterviewQ1 />} />
        <Route path="/interview/q2" element={<InterviewQ2 />} />
        <Route path="/interview/q3" element={<InterviewQ3 />} />
        <Route path="/interview/q4" element={<InterviewQ4 />} />
        <Route path="/interview/q5" element={<InterviewQ5 />} />
      </Routes>
  );
}

export default App;
