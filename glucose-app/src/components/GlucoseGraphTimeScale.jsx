import { useEffect, useMemo, useRef, useState } from "react";
import { Line } from "react-chartjs-2";
import { cs } from "date-fns/locale";

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
    datasets: [
      {
        label: "Glykémie (mmol/l)",
        data: filteredData.map(d => ({
          x: d.timestamp.replace(" ", "T"), // ISO
          y: d.value
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