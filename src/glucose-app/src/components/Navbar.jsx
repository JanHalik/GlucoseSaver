import { useEffect, useState } from "react";
import { useDarkMode } from "../contexts/DarkModeContext";
export default function Navbar({onLogout}) {
  const { darkMode, toggleDarkMode } = useDarkMode();
  return (
    <header className="flex items-center justify-between px-6 h-14 border-b">
      <div className="font-semibold">
        Glocose meter
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={toggleDarkMode}
          className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700"
        >
          {darkMode ? "Light" : "Dark"}
        </button>

        <button
          onClick={onLogout}
          className="px-3 py-1 rounded bg-red-500 text-white"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
