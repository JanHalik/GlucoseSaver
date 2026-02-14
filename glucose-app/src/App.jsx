import React, { useState, useEffect } from "react";
import GlucoseChart from "./components/GlucoseGraphDaD";
import LoginForm from "./components/LoginForm";
import AppThemeProvider from "./components/AppThemeProvider";
import AppLayout from "./layouts/AppLayout";
import { DarkModeProvider } from "./contexts/DarkModeContext";

function App() {
  const GLUCOSE_API_HOST = import.meta.env.VITE_GLUCOSE_API_HOST;
  const GLUCOSE_API_PORT = import.meta.env.VITE_GLUCOSE_API_PORT;
  const [token, setToken] = useState(localStorage.getItem("GlucoseToken"));
  const [expired, setExpired] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("GlucoseToken");
    setToken(null);
  };
  useEffect(() => {
    const handleExpired = () => {
      setToken(null);
      setExpired(true);
    };

    window.addEventListener("tokenExpired", handleExpired);
    return () => window.removeEventListener("tokenExpired", handleExpired);
  }, []);

  const [data, setData] = useState(null);
  useEffect(() => {
   fetch(`http://${GLUCOSE_API_HOST}:${GLUCOSE_API_PORT}/all_data?name=glucose`,{
    method: "GET",
    headers: {
      "x-api-password": `${token}`,
    }
  },)
      .then((res) => {
        if (res.status === 401) {
            // Token expiroval → odhlásit
            localStorage.removeItem("GlucoseToken");
            window.dispatchEvent(new Event("tokenExpired"));
            return null;
        }
        return res.json()})
      .then((data) => {
        console.log(data);
        setData(data.map(({ timestamp, glucose }) => ({
          timestamp: timestamp.replace(" ", "T"),
          value: glucose
        })));
      });
  }, []);
  return token ? (
    <DarkModeProvider>
    <AppThemeProvider>
    <AppLayout onLogout={handleLogout} >
      <div style={{ width: "100%", height: "300px" }}>
      <GlucoseChart data={data}/>
      </div>
    </AppLayout>
    </AppThemeProvider>
    </DarkModeProvider>
/*       <div className="App min-h-screen bg-gray-50 p-4">
        <DeviceService onLogout={handleLogout} />
      </div> */
  ):(
    <div className= "login-form">
      {expired && <p className="text-red-500 text-center">Session expired. Please login again.</p>}
      <LoginForm onLogin={(t) => {setToken(t); setExpired(false);}} />
    </div>
  );
}

export default App;
// cd glucose-app
//npm install react-chartjs-2 chart.js chartjs-plugin-annotation
// npm install react-vertical-timeline-component
//npm install react-icons
// npm install ag-grid-community ag-grid-react
// npm install @mui/material @mui/icons-material @emotion/react @emotion/styled

// npm install chart.js react-chartjs-2
// npm run dev