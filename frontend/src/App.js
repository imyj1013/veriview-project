// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import PersonalInterviewForm from "./pages/PersonalInterviewForm";
import DebateIntroPage from "./pages/DebateIntroPage";
import DebatePage from "./pages/DebatePage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/personal" element={<PersonalInterviewForm />} />
        <Route path="/debate-intro" element={<DebateIntroPage />} />
        <Route path="/debate" element={<DebatePage />} />
      </Routes>
    </Router>
  );
}

export default App;
