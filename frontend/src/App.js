// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SignupPage from "./pages/SignupPage";
import LoginPage from "./pages/LoginPage";
import PersonalInterviewForm from "./pages/PersonalInterviewForm";
import DebateIntroPage from "./pages/DebateIntroPage";
import DebatePage from "./pages/DebatePage";
import DebateStartPage from "./pages/DebateStartPage";
import DebateOpeningPage from "./pages/DebateOpeningPage";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/personal" element={<PersonalInterviewForm />} />
        <Route path="/debate-intro" element={<DebateIntroPage />} />
       {/* <Route path="/debate" element={<DebatePage />} /> */}
        <Route path="/debate-start" element={<DebateStartPage />} />
        <Route path="/debate/opening" element={<DebateOpeningPage />} />
      </Routes>
    </Router>
  );
}

export default App;
