import { useState, useEffect } from "react";
import axios from "axios";

export default function useAuth() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setIsLoggedIn(true);
    }
  }, []);

  const login = (token, user_id) => {
    localStorage.setItem("access_token", token);
    localStorage.setItem("user_id", user_id);
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    delete axios.defaults.headers.common["Authorization"];
    setIsLoggedIn(false);
  };

  return { isLoggedIn, login, logout };
}
