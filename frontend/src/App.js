// src/App.js

import { Routes, Route } from "react-router-dom";

// 기본 페이지
import HomePage from "./pages/HomePage";
import SignupPage from "./pages/SignupPage";
import LoginPage from "./pages/LoginPage";
import PersonalInterviewForm from "./pages/PersonalInterviewForm";

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

//공고추천

function App() {
  return (
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/personal" element={<PersonalInterviewForm />} />
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
      </Routes>
  );
}

export default App;
