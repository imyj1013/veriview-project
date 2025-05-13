import { useState, useEffect } from "react";
import axios from "axios";

export default function useAuth() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = getToken();
    setIsLoggedIn(!!token);
  }, []);

  const login = (token) => {
    localStorage.setItem("access_token", token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`; 
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    delete axios.defaults.headers.common["Authorization"];
    setIsLoggedIn(false);
  };

  const getToken = () => localStorage.getItem("access_token");

  return { isLoggedIn, login, logout, getToken };
}
