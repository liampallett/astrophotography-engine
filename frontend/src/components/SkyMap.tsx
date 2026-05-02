import React, { useState, useEffect, useMemo } from 'react';
import {
  Chart as ChartJS,
  ScatterController,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  LinearScale,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  ScatterController,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  LinearScale
);

// Props interface
interface SkyMapProps {
  targets: Array<{
    id: string;
    name: string;
    visibility: {
      peak_altitude: number;
      peak_time: string;
    };
    difficulty: string;
  }>;
  moon?: {
    altitude: number;
    azimuth: number;
    phase: string;
  };
  observationTime: string;
}

// Convert altitude+azimuth to Cartesian x/y sky map coordinates.
// North=up (+y), East=right (+x), zenith=origin, horizon=radius 90.
const altAzToXY = (altitude: number, azimuth: number): { x: number; y: number } => {
  const radius = 90 - altitude;
  const rad = (azimuth * Math.PI) / 180;
  return { x: Math.sin(rad) * radius, y: Math.cos(rad) * radius };
};

// Generate a full circle of points at a given altitude for reference rings.
const circleAt = (altitude: number): Array<{ x: number; y: number }> => {
  const r = 90 - altitude;
  return Array.from({ length: 361 }, (_, i) => {
    const rad = (i * Math.PI) / 180;
    return { x: Math.sin(rad) * r, y: Math.cos(rad) * r };
  });
};

// Difficulty color mapping
const getDifficultyColor = (difficulty: string): string => {
  const difficultyLower = difficulty.toLowerCase();
  if (difficultyLower.includes('easy') || difficultyLower.includes('beginner')) {
    return 'rgb(34, 197, 94)'; // green-500
  } else if (difficultyLower.includes('moderate') || difficultyLower.includes('intermediate')) {
    return 'rgb(234, 179, 8)'; // yellow-500
  } else {
    return 'rgb(239, 68, 68)'; // red-500
  }
};

const SkyMap: React.FC<SkyMapProps> = ({ targets: propTargets, moon: propMoon, observationTime: propObservationTime }) => {
  // Reactively receive calculated data via window.__SKYMAP_DATA__ + 'skymap-data-ready' event.
  const readWindowData = () =>
    typeof window !== 'undefined' ? (window as any).__SKYMAP_DATA__ ?? null : null;

  const [liveData, setLiveData] = useState<any>(readWindowData);

  useEffect(() => {
    const handler = () => setLiveData(readWindowData());
    window.addEventListener('skymap-data-ready', handler);
    return () => window.removeEventListener('skymap-data-ready', handler);
  }, []);

  const active = liveData?.useCalculatedData ? liveData : null;
  const targets: SkyMapProps['targets'] = active?.targets ?? propTargets;
  const moon: SkyMapProps['moon'] = active?.moon ?? propMoon;
  const observationTime: string = active?.observationTime ?? propObservationTime;

  const [timeOffset, setTimeOffset] = useState(0);
  const [currentTime, setCurrentTime] = useState(() => new Date(observationTime));

  // Keep currentTime in sync with slider and reset when new data arrives
  useEffect(() => {
    const base = new Date(observationTime);
    setCurrentTime(new Date(base.getTime() + timeOffset * 3600000));
  }, [timeOffset, observationTime]);

  // Reset slider when new observation data arrives
  useEffect(() => {
    setTimeOffset(0);
  }, [observationTime]);

  // Calculate target positions based on current time
  const targetPositions = useMemo(() => {
    return targets.map(target => {
      const peakTime = new Date(target.visibility.peak_time);
      const hoursDiff = (currentTime.getTime() - peakTime.getTime()) / 3600000;

      // Altitude falls off ~10°/hr from peak; clamp to horizon
      const altitude = Math.max(0, target.visibility.peak_altitude - Math.abs(hoursDiff) * 10);
      // Objects transit south (180°) at peak, drift 15°/hr due to Earth's rotation
      const azimuth = (180 + hoursDiff * 15 + 360) % 360;
      const { x, y } = altAzToXY(altitude, azimuth);

      return { ...target, altitude, azimuth, x, y };
    });
  }, [targets, currentTime, observationTime]);

  // Prepare chart data
  const chartData = {
    datasets: [
      // Horizon circle (altitude = 0°)
      {
        label: 'Horizon',
        data: circleAt(0),
        borderColor: 'rgba(156, 163, 175, 0.6)',
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      // 30° altitude reference circle
      {
        label: '30° Altitude',
        data: circleAt(30),
        borderColor: 'rgba(107, 114, 128, 0.35)',
        borderWidth: 1,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      // 60° altitude reference circle
      {
        label: '60° Altitude',
        data: circleAt(60),
        borderColor: 'rgba(107, 114, 128, 0.35)',
        borderWidth: 1,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      // Moon position (only when altitude and azimuth are known)
      ...(moon && moon.altitude > 0 && moon.azimuth != null
        ? [
            {
              label: `Moon (${moon.phase})`,
              data: [altAzToXY(moon.altitude, moon.azimuth)],
              backgroundColor: 'rgba(251, 191, 36, 0.8)',
              borderColor: 'rgb(251, 191, 36)',
              borderWidth: 2,
              pointRadius: 8,
              pointStyle: 'circle' as const,
              showLine: false,
            },
          ]
        : []),
      // Target positions
      ...targetPositions
        .filter(target => target.altitude > 0)
        .map(target => ({
          label: target.name,
          data: [{ x: target.x, y: target.y }],
          backgroundColor: getDifficultyColor(target.difficulty),
          borderColor: getDifficultyColor(target.difficulty),
          borderWidth: 2,
          pointRadius: 6,
          pointStyle: 'circle' as const,
          showLine: false,
        })),
    ],
  };

  // Don't render the chart until we have real data from the API
  if (!active) {
    return null;
  }

  const REFERENCE_LABELS = new Set(['Horizon', '30° Altitude', '60° Altitude']);

  // Chart options
  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        min: -100,
        max: 100,
        grid: { color: 'rgba(75, 85, 99, 0.2)', drawTicks: false },
        ticks: { display: false },
        border: { display: false },
      },
      y: {
        min: -100,
        max: 100,
        grid: { color: 'rgba(75, 85, 99, 0.2)', drawTicks: false },
        ticks: { display: false },
        border: { display: false },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: 'rgb(229, 231, 235)',
        bodyColor: 'rgb(229, 231, 235)',
        borderColor: 'rgb(75, 85, 99)',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        filter: (item: any) => !REFERENCE_LABELS.has(item.dataset.label),
        callbacks: {
          title: (context: any) => context[0].dataset.label || '',
          label: (context: any) => {
            const target = targetPositions.find(t => t.name === context.dataset.label);
            if (target) {
              return [
                `Altitude: ${target.altitude.toFixed(1)}°`,
                `Azimuth: ${target.azimuth.toFixed(1)}°`,
                `Difficulty: ${target.difficulty}`,
              ];
            }
            return '';
          },
        },
      },
    },
  };

  return (
    <div className="w-full bg-gray-800 rounded-lg p-6 shadow-xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Sky Map</h2>
        <p className="text-gray-300 text-sm">
          {isNaN(currentTime.getTime())
            ? observationTime
            : currentTime.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })}
        </p>
      </div>

      {/* Chart Container with compass labels */}
      {/* Use padding-bottom trick instead of aspect-square: Chart.js reads clientHeight */}
      {/* at init time before CSS aspect-ratio is resolved, giving height=0 canvas. */}
      <div className="w-full max-w-2xl mx-auto mb-6">
        <div style={{ position: 'relative', paddingBottom: '100%' }}>
          <div style={{ position: 'absolute', inset: 0 }}>
            <Chart type="scatter" data={chartData} options={options} />
          </div>
          {/* Compass direction labels */}
          <div style={{ position: 'absolute', top: '4px', left: '50%', transform: 'translateX(-50%)' }} className="text-gray-200 font-bold text-sm pointer-events-none">N</div>
          <div style={{ position: 'absolute', bottom: '4px', left: '50%', transform: 'translateX(-50%)' }} className="text-gray-200 font-bold text-sm pointer-events-none">S</div>
          <div style={{ position: 'absolute', left: '4px', top: '50%', transform: 'translateY(-50%)' }} className="text-gray-200 font-bold text-sm pointer-events-none">W</div>
          <div style={{ position: 'absolute', right: '4px', top: '50%', transform: 'translateY(-50%)' }} className="text-gray-200 font-bold text-sm pointer-events-none">E</div>
        </div>
      </div>

      {/* Time Slider */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Time Offset: {timeOffset > 0 ? '+' : ''}{timeOffset} hours
        </label>
        <input
          type="range"
          min="-6"
          max="6"
          step="0.5"
          value={timeOffset}
          onChange={(e) => setTimeOffset(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>-6h</span>
          <span>Now</span>
          <span>+6h</span>
        </div>
      </div>

      {/* Legend */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Legend</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-sm text-gray-300">Easy Target</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span className="text-sm text-gray-300">Moderate Target</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span className="text-sm text-gray-300">Challenging Target</span>
          </div>
          {moon && moon.altitude > 0 && (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-amber-400"></div>
              <span className="text-sm text-gray-300">Moon</span>
            </div>
          )}
        </div>
        <div className="mt-3 text-xs text-gray-400">
          <p>• Center = Zenith (directly overhead) &nbsp;|&nbsp; Edge = Horizon (0°)</p>
          <p>• Dashed rings = 30° and 60° altitude</p>
        </div>
      </div>

      {/* Target List */}
      <div className="border-t border-gray-700 pt-4 mt-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">
          Visible Targets ({targetPositions.filter(t => t.altitude > 0).length})
        </h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {targetPositions
            .filter(t => t.altitude > 0)
            .sort((a, b) => b.altitude - a.altitude)
            .map(target => (
              <div
                key={target.id}
                className="flex items-center justify-between p-2 bg-gray-700 rounded text-sm"
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getDifficultyColor(target.difficulty) }}
                  ></div>
                  <span className="text-white font-medium">{target.name}</span>
                </div>
                <div className="text-gray-300 text-xs">
                  Alt: {target.altitude.toFixed(1)}° | Az: {target.azimuth.toFixed(1)}°
                </div>
              </div>
            ))}
          {targetPositions.filter(t => t.altitude > 0).length === 0 && (
            <p className="text-gray-400 text-sm italic">No targets visible at this time</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkyMap;

// Made with Bob
