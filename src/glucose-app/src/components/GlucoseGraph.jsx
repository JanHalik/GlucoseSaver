import { useMemo, useState } from "react";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  annotationPlugin
);

export default function GlucoseChart({ data }) {
  const [selectedDate, setSelectedDate] = useState(() =>
    new Date(data[0].timestamp).toISOString().slice(0, 10)
  );

  const filteredData = useMemo(() => {
    return data.filter(d =>
      d.timestamp.startsWith(selectedDate)
    );
  }, [data, selectedDate]);

  const chartData = {
    labels: filteredData.map(d =>
      new Date(d.timestamp).toLocaleTimeString("cs-CZ", {
        hour: "2-digit",
        minute: "2-digit"
      })
    ),
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
    <div>
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
