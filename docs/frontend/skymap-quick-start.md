# SkyMap Component - Quick Start Guide

## 🚀 Quick Integration

### 1. Import the Component
```astro
---
import SkyMap from '../components/SkyMap';
---
```

### 2. Use in Your Page
```astro
<SkyMap 
  client:load
  targets={targets}
  moon={moon}
  observationTime={observationTime}
/>
```

### 3. Required Props Format
```typescript
const targets = [
  {
    id: "m31",
    name: "M31 (Andromeda Galaxy)",
    visibility: {
      peak_altitude: 75,        // degrees (0-90)
      peak_time: "2026-05-02T22:00:00Z"  // ISO 8601
    },
    difficulty: "Easy"          // "Easy", "Moderate", or "Challenging"
  }
];

const moon = {
  altitude: 30,                 // degrees (0-90)
  azimuth: 120,                 // degrees (0-360)
  phase: "Waxing Crescent"      // any string
};

const observationTime = "2026-05-02T21:00:00Z";  // ISO 8601
```

## 🎨 Demo Page

Visit the demo page to see the component in action:
```
http://localhost:4321/skymap-demo
```

## 📚 Full Documentation

For complete integration guide, see: `SKYMAP_INTEGRATION.md`

## ✅ Features

- ✨ Interactive polar chart
- 🎯 Target position markers
- 🌙 Moon position display
- ⏰ Time slider (-6h to +6h)
- 📱 Responsive design
- 🎨 Dark theme
- 🔍 Interactive tooltips
- 📊 Real-time altitude/azimuth

## 🎯 Color Coding

- 🟢 Green = Easy targets
- 🟡 Yellow = Moderate targets
- 🔴 Red = Challenging targets
- 🟠 Amber = Moon

## 📍 Coordinate System

- **Center** = Zenith (90° altitude, directly overhead)
- **Edge** = Horizon (0° altitude)
- **Top** = North (0° azimuth)
- **Right** = East (90° azimuth)
- **Bottom** = South (180° azimuth)
- **Left** = West (270° azimuth)

## 🔧 Troubleshooting

**Component not rendering?**
- Add `client:load` directive
- Check all required props are provided
- Ensure targets array is not empty

**No targets visible?**
- Targets with altitude ≤ 0 are filtered out
- Use time slider to find when targets are visible
- Check the "Visible Targets" list

## 📦 Dependencies

All dependencies are already installed:
- chart.js (^4.5.1)
- react-chartjs-2 (^5.3.1)
- react (^19.2.5)

No additional installation required! 🎉