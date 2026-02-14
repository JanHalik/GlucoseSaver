import { useEffect, useMemo, useRef, useState } from "react";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  annotationPlugin
);

function addDays(dateStr, diff) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d)) return "";
  d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

export default function GlucoseChart({ data }) {
  const containerRef = useRef(null);
  const safeData = Array.isArray(data) ? data : [];
  const [selectedDate, setSelectedDate] = useState("");

  // inicializace dne z dat
  useEffect(() => {
    if (safeData.length === 0) return;

    const firstValid = safeData.find(
      d => d?.timestamp && !isNaN(new Date(d.timestamp))
    );
    if (!firstValid) return;

    setSelectedDate(firstValid.timestamp.slice(0, 10));
  }, [safeData]);

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

  const filteredData = useMemo(() => {
    if (!selectedDate) return [];
    return safeData.filter(
      d => d?.timestamp?.slice(0, 10) === selectedDate
    );
  }, [safeData, selectedDate]);

  // prázdný stav
  if (safeData.length === 0) {
    return <div>Žádná data k dispozici</div>;
  }

  const chartData = {
    labels: filteredData.map(d => {
      const dt = new Date(d.timestamp);
      return isNaN(dt)
        ? ""
        : dt.toLocaleTimeString("cs-CZ", {
            hour: "2-digit",
            minute: "2-digit"
          });
    }),
    datasets: [
      {
        label: "Glykémie (mmol/l)",
        data: filteredData.map(d => d.value),
        borderColor: "#2563eb",
        tension: 0.3,
        pointRadius: 4
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 0,
        max: 15
      }
    },
    plugins: {
      annotation: {
        annotations: {
          optimalRange: {
            type: "box",
            yMin: 3,
            yMax: 9,
            backgroundColor: "rgba(0,200,0,0.15)",
            borderWidth: 0
          }
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