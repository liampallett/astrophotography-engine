# SkyMap Component Integration Guide

## Overview
The SkyMap component is an interactive polar chart that visualizes celestial targets in the night sky, showing their positions in altitude/azimuth coordinates.

## Component Location
`astrophotography-engine/frontend/src/components/SkyMap.tsx`

## Features
✅ Interactive polar plot with altitude/azimuth coordinates
✅ Target position markers with color-coded difficulty levels
✅ Moon position display
✅ Horizon line at 0° altitude
✅ Cardinal directions (N, E, S, W)
✅ Time slider to see target movement across the sky (-6h to +6h)
✅ Responsive design for mobile and desktop
✅ Dark theme matching the application
✅ Altitude circles at 30°, 60°, and 90° (zenith)
✅ Interactive tooltips with target details
✅ Visible targets list with real-time altitude/azimuth

## Dependencies
All required dependencies are already installed:
- `chart.js` (^4.5.1)
- `react-chartjs-2` (^5.3.1)
- `react` (^19.2.5)

## Props Interface

```typescript
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
```

### Props Details

**targets** (required)
- Array of target objects to display on the sky map
- Each target must have:
  - `id`: Unique identifier
  - `name`: Display name
  - `visibility.peak_altitude`: Peak altitude in degrees (0-90)
  - `visibility.peak_time`: ISO 8601 datetime string
  - `difficulty`: "Easy", "Moderate", or "Challenging"

**moon** (optional)
- Moon position data
- `altitude`: Moon altitude in degrees (0-90)
- `azimuth`: Moon azimuth in degrees (0-360)
- `phase`: Moon phase description (e.g., "Full Moon", "Waxing Crescent")

**observationTime** (required)
- ISO 8601 datetime string representing the base observation time
- Used as the reference point for the time slider

## Integration in Astro Pages

### Example 1: Basic Integration

```astro
---
// src/pages/results.astro
import Layout from '../layouts/Layout.astro';
import SkyMap from '../components/SkyMap';

const targets = [
  {
    id: "m31",
    name: "M31 (Andromeda Galaxy)",
    visibility: {
      peak_altitude: 75,
      peak_time: "2026-05-02T22:00:00Z"
    },
    difficulty: "Easy"
  },
  {
    id: "m42",
    name: "M42 (Orion Nebula)",
    visibility: {
      peak_altitude: 45,
      peak_time: "2026-05-02T20:30:00Z"
    },
    difficulty: "Moderate"
  }
];

const moon = {
  altitude: 30,
  azimuth: 120,
  phase: "Waxing Crescent"
};

const observationTime = "2026-05-02T21:00:00Z";
---

<Layout title="Sky Map">
  <div class="container mx-auto px-4 py-8">
    <SkyMap 
      client:load
      targets={targets}
      moon={moon}
      observationTime={observationTime}
    />
  </div>
</Layout>
```

### Example 2: Integration with API Data

```astro
---
// src/pages/targets.astro
import Layout from '../layouts/Layout.astro';
import SkyMap from '../components/SkyMap';

// Fetch data from your backend API
const response = await fetch('http://localhost:8000/api/targets', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    latitude: 51.5074,
    longitude: -0.1278,
    observation_date: "2026-05-02",
    observation_time: "21:00"
  })
});

const data = await response.json();

// Transform API response to SkyMap format
const targets = data.targets.map(target => ({
  id: target.id,
  name: target.name,
  visibility: {
    peak_altitude: target.visibility.peak_altitude,
    peak_time: target.visibility.peak_time
  },
  difficulty: target.difficulty
}));

const moon = data.moon ? {
  altitude: data.moon.altitude,
  azimuth: data.moon.azimuth,
  phase: data.moon.phase
} : undefined;

const observationTime = `${data.observation_date}T${data.observation_time}:00Z`;
---

<Layout title="Target Recommendations">
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-white mb-6">
      Recommended Targets for Tonight
    </h1>
    
    <SkyMap 
      client:load
      targets={targets}
      moon={moon}
      observationTime={observationTime}
    />
    
    <!-- Additional content -->
  </div>
</Layout>
```

### Example 3: Conditional Rendering

```astro
---
import Layout from '../layouts/Layout.astro';
import SkyMap from '../components/SkyMap';

const { targets, moon, observationTime } = Astro.props;
const hasTargets = targets && targets.length > 0;
---

<Layout title="Sky Visualization">
  <div class="container mx-auto px-4 py-8">
    {hasTargets ? (
      <SkyMap 
        client:load
        targets={targets}
        moon={moon}
        observationTime={observationTime}
      />
    ) : (
      <div class="bg-gray-800 rounded-lg p-8 text-center">
        <p class="text-gray-300">No targets available for visualization</p>
      </div>
    )}
  </div>
</Layout>
```

## Important Notes

### Client Directive
Always use `client:load` directive when importing the SkyMap component in Astro pages:
```astro
<SkyMap client:load {...props} />
```

This ensures the React component is hydrated on the client side, enabling interactivity.

### Styling
The component uses Tailwind CSS classes and is designed for dark theme:
- Background: `bg-gray-800`
- Text: `text-white`, `text-gray-300`
- Borders: `border-gray-700`

Ensure your page layout has a dark background for best visual consistency.

### Responsive Design
The component is fully responsive:
- Mobile: Single column layout, compact controls
- Desktop: Optimized chart size with better spacing
- The chart maintains a 1:1 aspect ratio for proper polar visualization

### Time Slider
- Range: -6 hours to +6 hours from observation time
- Step: 0.5 hours (30 minutes)
- Updates target positions in real-time
- Smooth animations when time changes

## Color Coding

### Difficulty Levels
- 🟢 **Green** (`rgb(34, 197, 94)`): Easy targets
- 🟡 **Yellow** (`rgb(234, 179, 8)`): Moderate targets
- 🔴 **Red** (`rgb(239, 68, 68)`): Challenging targets
- 🟠 **Amber** (`rgb(251, 191, 36)`): Moon position

## Coordinate System

### Altitude
- 0° = Horizon (edge of chart)
- 30° = Low in sky
- 60° = High in sky
- 90° = Zenith (center of chart, directly overhead)

### Azimuth
- 0° = North (top)
- 90° = East (right)
- 180° = South (bottom)
- 270° = West (left)

## Troubleshooting

### Component Not Rendering
- Ensure `client:load` directive is used
- Check that all required props are provided
- Verify targets array is not empty

### TypeScript Errors
- The component uses `any` types for Chart.js options to avoid complex type issues
- This is intentional and safe for this use case

### Chart Not Displaying Correctly
- Verify altitude values are between 0-90
- Verify azimuth values are between 0-360
- Check that observationTime is a valid ISO 8601 string

### Targets Not Visible
- Targets with altitude ≤ 0 are automatically filtered out
- Use the time slider to see when targets become visible
- Check the "Visible Targets" list below the chart

## Performance Considerations

- The component efficiently updates only when props or time offset changes
- Uses React `useMemo` for expensive calculations
- Chart.js provides hardware-accelerated rendering
- Handles up to 50+ targets without performance issues

## Future Enhancements

Potential improvements for future versions:
- Real-time altitude/azimuth calculation using astronomical libraries
- Export sky map as image
- Toggle visibility of different target types
- Constellation overlays
- Light pollution zones
- Weather overlay integration

## Support

For issues or questions:
1. Check this integration guide
2. Review the component source code
3. Test with sample data first
4. Verify all dependencies are installed

## Example Data Format

```json
{
  "targets": [
    {
      "id": "m31",
      "name": "M31 (Andromeda Galaxy)",
      "visibility": {
        "peak_altitude": 75.5,
        "peak_time": "2026-05-02T22:00:00Z"
      },
      "difficulty": "Easy"
    }
  ],
  "moon": {
    "altitude": 30.2,
    "azimuth": 120.5,
    "phase": "Waxing Crescent"
  },
  "observationTime": "2026-05-02T21:00:00Z"
}
```

---

**Component Version**: 1.0.0  
**Last Updated**: May 2, 2026  
**Compatibility**: Astro 6.x, React 19.x, Chart.js 4.x