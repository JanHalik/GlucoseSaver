// DarkModeContext.jsx
import { createContext, useContext, useState, useEffect } from "react";

const DarkModeContext = createContext();

export const DarkModeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);

  // Načtení z localStorage při mountu
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.setAttribute("data-ag-theme-mode", "dark");
      setDarkMode(true);
    }else{
      document.documentElement.setAttribute("data-ag-theme-mode", "light");
    }
  }, []);

  // Toggle funkce
  const toggleDarkMode = () => {
    document.documentElement.classList.toggle("dark");
    const isDark = document.documentElement.classList.contains("dark");
    setDarkMode(isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
  };

  return (
    <DarkModeContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </DarkModeContext.Provider>
  );
};

// Hook pro jednodušší použití
export const useDarkMode = () => useContext(DarkModeContext);
