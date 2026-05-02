import React, { useState, useEffect, useMemo } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  LinearScale,
  type ChartOptions,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  RadialLinearScale,
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

// Helper function to convert azimuth to chart angle (0° = North at top)
const azimuthToChartAngle = (azimuth: number): number => {
  // Chart.js polar: 0° is right (East), 90° is top (North)
  // Azimuth: 0° is North, 90° is East, 180° is South, 270° is West
  // Convert: chartAngle = 90 - azimuth
  return (90 - azimuth + 360) % 360;
};

// Helper function to convert altitude to radius (0° = edge, 90° = center)
const altitudeToRadius = (altitude: number): number => {
  // Invert so 90° (zenith) is at center (0) and 0° (horizon) is at edge (90)
  return 90 - altitude;
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
  // Check if we have calculated data from window object
  const skymapData = typeof window !== 'undefined' && (window as any).__SKYMAP_DATA__;
  const targets = skymapData?.useCalculatedData ? skymapData.targets : propTargets;
  const moon = skymapData?.useCalculatedData ? skymapData.moon : propMoon;
  const observationTime = skymapData?.useCalculatedData ? skymapData.observationTime : propObservationTime;

  const [timeOffset, setTimeOffset] = useState(0); // Hours offset from observationTime
  const [currentTime, setCurrentTime] = useState(new Date(observationTime));

  // Update current time when timeOffset changes
  useEffect(() => {
    const baseTime = new Date(observationTime);
    const newTime = new Date(baseTime.getTime() + timeOffset * 60 * 60 * 1000);
    setCurrentTime(newTime);
  }, [timeOffset, observationTime]);

  // Calculate target positions based on current time
  const targetPositions = useMemo(() => {
    return targets.map(target => {
      // For simplicity, we'll use peak altitude and estimate azimuth
      // In a real implementation, you'd calculate actual alt/az for the current time
      const peakTime = new Date(target.visibility.peak_time);
      const baseTime = new Date(observationTime);
      
      // Calculate time difference in hours
      const hoursDiff = (currentTime.getTime() - peakTime.getTime()) / (1000 * 60 * 60);
      
      // Estimate altitude (peaks at peak_time, decreases as we move away)
      const altitude = Math.max(0, target.visibility.peak_altitude - Math.abs(hoursDiff) * 10);
      
      // Estimate azimuth based on time (simplified celestial motion)
      // Objects rise in the east (90°), transit south (180°), set in west (270°)
      const baseAzimuth = 180; // South at peak
      const azimuth = (baseAzimuth + hoursDiff * 15 + 360) % 360; // 15° per hour
      
      return {
        ...target,
        altitude,
        azimuth,
        chartAngle: azimuthToChartAngle(azimuth),
        radius: altitudeToRadius(altitude),
      };
    });
  }, [targets, currentTime, observationTime]);

  // Prepare chart data
  const chartData = {
    datasets: [
      // Horizon line (altitude = 0°)
      {
        label: 'Horizon',
        data: Array.from({ length: 360 }, (_, i) => ({
          x: i,
          y: 90, // radius for 0° altitude
        })),
        borderColor: 'rgba(156, 163, 175, 0.5)', // gray-400
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      // Altitude circles (30°, 60°)
      {
        label: '30° Altitude',
        data: Array.from({ length: 360 }, (_, i) => ({
          x: i,
          y: 60, // radius for 30° altitude
        })),
        borderColor: 'rgba(107, 114, 128, 0.3)', // gray-500
        borderWidth: 1,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      {
        label: '60° Altitude',
        data: Array.from({ length: 360 }, (_, i) => ({
          x: i,
          y: 30, // radius for 60° altitude
        })),
        borderColor: 'rgba(107, 114, 128, 0.3)', // gray-500
        borderWidth: 1,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        showLine: true,
      },
      // Moon position
      ...(moon && moon.altitude > 0
        ? [
            {
              label: `Moon (${moon.phase})`,
              data: [
                {
                  x: azimuthToChartAngle(moon.azimuth),
                  y: altitudeToRadius(moon.altitude),
                },
              ],
              backgroundColor: 'rgba(251, 191, 36, 0.8)', // amber-400
              borderColor: 'rgb(251, 191, 36)',
              borderWidth: 2,
              pointRadius: 8,
              pointStyle: 'circle',
            },
          ]
        : []),
      // Target positions
      ...targetPositions
        .filter(target => target.altitude > 0)
        .map(target => ({
          label: target.name,
          data: [
            {
              x: target.chartAngle,
              y: target.radius,
            },
          ],
          backgroundColor: getDifficultyColor(target.difficulty),
          borderColor: getDifficultyColor(target.difficulty),
          borderWidth: 2,
          pointRadius: 6,
          pointStyle: 'circle',
        })),
    ],
  };

  // Chart options
  const options: any = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1,
    scales: {
      r: {
        min: 0,
        max: 90,
        reverse: true, // So 0 (zenith) is at center
        ticks: {
          stepSize: 30,
          callback: (value: any) => {
            const altitude = 90 - Number(value);
            return altitude === 90 ? 'Zenith' : `${altitude}°`;
          },
          color: 'rgb(156, 163, 175)', // gray-400
          backdropColor: 'transparent',
        },
        grid: {
          color: 'rgba(75, 85, 99, 0.3)', // gray-600
          circular: true,
        },
        pointLabels: {
          color: 'rgb(229, 231, 235)', // gray-200
          font: {
            size: 14,
            weight: 'bold' as const,
          },
          callback: (_label: unknown, index: number) => {
            const directions = ['E', 'N', 'W', 'S'];
            return directions[Math.floor(index / 90)] || '';
          },
        },
        angleLines: {
          color: 'rgba(75, 85, 99, 0.3)', // gray-600
        },
      },
    },
    plugins: {
      legend: {
        display: false, // We'll create a custom legend
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)', // gray-900
        titleColor: 'rgb(229, 231, 235)', // gray-200
        bodyColor: 'rgb(229, 231, 235)',
        borderColor: 'rgb(75, 85, 99)', // gray-600
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          title: (context: any) => {
            const datasetLabel = context[0].dataset.label;
            return datasetLabel || '';
          },
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
          {currentTime.toLocaleString('en-US', {
            dateStyle: 'medium',
            timeStyle: 'short',
          })}
        </p>
      </div>

      {/* Chart Container */}
      <div className="relative w-full max-w-2xl mx-auto mb-6">
        <div className="aspect-square">
          <Chart type="scatter" data={chartData} options={options} />
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
          <p>• Center = Zenith (directly overhead)</p>
          <p>• Edge = Horizon (0° altitude)</p>
          <p>• N = North, E = East, S = South, W = West</p>
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
