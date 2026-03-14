import { useEffect, useMemo, useRef, useState } from "react";
import { Line } from "react-chartjs-2";
import { cs } from "date-fns/locale";
import ws from "../ws/websocketService";
function addDays(dateStr, diff) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d)) return "";
  d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

export default function GlucoseChart({ patient_id}) {
  const GLUCOSE_API_HOST = window.__ENV__?.VITE_GLUCOSE_API_HOST ??   import.meta.env.VITE_GLUCOSE_API_HOST;
  const GLUCOSE_API_PORT = window.__ENV__?.VITE_GLUCOSE_API_PORT ??   import.meta.env.VITE_GLUCOSE_API_PORT;
  const GLUCOSE_ROOT_PATH = window.__ENV__?.VITE_GLUCOSE_ROOT_PATH || '';
  const GLUCOSE_API_PROTOCOL = window.__ENV__?.VITE_GLUCOSE_API_PROTOCOL || 'http';
  const GLUCOSE_WS_PROTOCOL = GLUCOSE_API_PROTOCOL === 'https' ? 'wss' : 'ws';
  const containerRef = useRef(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [filteredData, setFilteredData] = useState([]);


   const [loading, setLoading] = useState(false);
  // Funkce pro načtení dat
  const fetchData = () => {
    console.info("Loading...")
    setLoading(true);
    let url=`${GLUCOSE_API_PROTOCOL}://${GLUCOSE_API_HOST}:${GLUCOSE_API_PORT}/${GLUCOSE_ROOT_PATH}measurements/${patient_id}/day/${selectedDate}`;
    const response = fetch(url,{
    headers: {
      Authorization: `IncognitoUms auth=${localStorage.getItem("GlucoseToken")}`,
    },})
      .then((res) => {
        return res.json()})
      .then((data) => {
        console.info("Loaded")
        setLoading(false);
        console.log(data)
        setFilteredData(data || []);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
      });
  };
  useEffect(() => {
    fetchData();
    ws.connect(`${GLUCOSE_WS_PROTOCOL}://${GLUCOSE_API_HOST}:${GLUCOSE_API_PORT}/${GLUCOSE_ROOT_PATH}view/ws?patient_id=${patient_id}`);

    const handler = (payload) => {
      console.log(payload)
      if (payload.entity!="service") return;
      if (!gridRef.current) return;
      if (payload.operation=="delete"){
          gridRef.current.api.applyTransaction({
            remove: [payload.data],
          });
          console.info("Service row deleted",payload.data.ID)
          return;
      }
      if (serviceType!=payload.data.ServiceType && serviceType!="All") return;
      switch (payload.operation) {
        case "change":
          gridRef.current.api.applyTransaction({
            update: [payload.data],
          });
          console.info("Service row updated",payload.data.ID)
          break;
        case "add":
          gridRef.current.api.applyTransaction({
            add: [payload.data],
          });
          console.info("Service row added",payload.data.ID)
          break;
        default:
          console.warn("Unknown WS action", msg);
      }
    };

    ws.on("entity", handler);

    return () => ws.off("entity", handler);
  }, [selectedDate, patient_id]);
  // kolečko + shift
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !selectedDate) return;

    const onWheel = e => {
      if (!e.shiftKey) return;

      e.preventDefault();
      setSelectedDate(prev =>
        addDays(prev, e.deltaY > 0 ? 1 : -1)
      );
    };

    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [selectedDate]);


  const chartData = {
    datasets: [
      {
        label: "Glykémie (mmol/l)",
        data: filteredData.map(d => ({
          x: d.Time.replace(" ", "T"), // ISO
          y: d.Value
        })),
        borderColor: "#2563eb",
        tension: 0.3,
        pointRadius: 4,
        spanGaps: 20 * 60 * 1000
      }
    ]
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: "time",
        min: `${selectedDate}T00:00:00`,
        max: `${selectedDate}T23:59:59`,
        time: {
          unit: "minute",
          tooltipFormat: "HH:mm:ss",
          displayFormats: {
            minute: "HH:mm"
          }
        },
        adapters: {
          date: {
            locale: cs
          }
        }
      },
      y: {
        min: 1,
        max: 15
      }
    },
    plugins: {
      annotation: {
        //DM2: 4-7.5 mmol/l (6-7.5 ráno a večer),
        //DM1: 4-6.5 mmol/l (ráno a večer), po jídle do 10 mmol/l, Time in Range (3,9–10 mmol/l): >70 %, ideálně >80 %
        annotations: {
          optimalRangeMorning: {
            type: "box",
            xMin: `${selectedDate}T00:00:00`,
            xMax: `${selectedDate}T06:59:59`,
            yMin: 4,
            yMax: 6.5,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          optimalRangeBeforeSleep: {
            type: "box",
            xMin: `${selectedDate}T20:00:00`,
            xMax: `${selectedDate}T21:59:59`,
            yMin: 5,
            yMax: 7.5,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          optimalRangeNight: {
            type: "box",
            xMin: `${selectedDate}T22:00:00`,
            xMax: `${selectedDate}T23:59:59`,
            yMin: 4,
            yMax: 7,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          afterBrekfastRange: {
            type: "box",
            xMin: `${selectedDate}T07:00:00`,
            xMax: `${selectedDate}T10:59:59`,
            yMin: 4.5,
            yMax: 8,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          optimalRange: {
            type: "box",
            xMin: `${selectedDate}T11:00:00`,
            xMax: `${selectedDate}T11:59:59`,
            yMin: 4,
            yMax: 7,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          afterLunchRange: {
            type: "box",
            xMin: `${selectedDate}T12:00:00`,
            xMax: `${selectedDate}T14:59:59`,
            yMin: 4.5,
            yMax: 8,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          optimalRange2: {
            type: "box",
            xMin: `${selectedDate}T15:00:00`,
            xMax: `${selectedDate}T17:59:59`,
            yMin: 4,
            yMax: 7,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          afterDinnerRange: {
            type: "box",
            xMin: `${selectedDate}T18:00:00`,
            xMax: `${selectedDate}T19:59:59`,
            yMin: 4.5,
            yMax: 8,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          },
          subOptimalRange: {
            type: "box",
            xMin: `${selectedDate}T06:00:00`,
            xMax: `${selectedDate}T20:59:59`,
            yMin: 3.5,
            yMax: 10,
            backgroundColor: "rgba(197, 200, 0, 0.15)",
            borderWidth: 0
          },
          subOptimalRangeNight: {
            type: "box",
            xMin: `${selectedDate}T21:00:00`,
            xMax: `${selectedDate}T23:59:59`,
            yMin: 3.5,
            yMax: 8.5,
            backgroundColor: "rgba(197, 200, 0, 0.15)",
            borderWidth: 0
          },
          subOptimalRangeNight2: {
            type: "box",
            xMin: `${selectedDate}T00:00:00`,
            xMax: `${selectedDate}T05:59:59`,
            yMin: 3.5,
            yMax: 8,
            backgroundColor: "rgba(197, 200, 0, 0.15)",
            borderWidth: 0
          },
        }
      }
    }
  };

  return (
    <div ref={containerRef}>
      <label>
        Den:
        <input
          type="date"
          value={selectedDate}
          onChange={e => setSelectedDate(e.target.value)}
          style={{ marginLeft: "0.5rem" }}
        />
      </label>

      <div style={{ height: "320px", marginTop: "1rem" }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}