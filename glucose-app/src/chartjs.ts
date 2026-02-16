import { Chart as ChartJS } from "chart.js";
import {
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
  TimeScale
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";

// ⬇️ KRITICKÉ – MUSÍ BÝT PŘED POUŽITÍM
import "chartjs-adapter-date-fns";

ChartJS.register(
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
  TimeScale,
  annotationPlugin
);
