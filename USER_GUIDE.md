# 📖 Astrophotography Target Finder - User Guide

Welcome to the Astrophotography Target Finder! This guide will help you get the most out of the application.

## 🎯 What Does This App Do?

The Astrophotography Target Finder helps you discover the best celestial objects to photograph based on:
- **Your Location** - What's visible from where you are
- **Your Equipment** - What fits in your telescope's field of view
- **Current Conditions** - Moon phase, altitude, and timing
- **Professional Calculations** - Powered by Astropy astronomy library

## 🚀 Quick Start

### 1. Enter Your Location

**Option A: Search by Address**
1. Type your city or address (e.g., "London, UK" or "New York City")
2. Click "Search"
3. The app will automatically fill in coordinates and timezone

**Option B: Manual Coordinates**
1. Enter latitude (-90 to 90)
2. Enter longitude (-180 to 180)
3. Timezone will be detected automatically
4. Optionally enter elevation in meters

**Tips:**
- Use your exact observing location for best results
- Elevation affects atmospheric calculations slightly
- Timezone is important for accurate twilight calculations

### 2. Configure Your Equipment

**Telescope Settings:**
- **Aperture (mm)**: Diameter of your main lens or mirror
  - Example: 200mm for an 8-inch telescope
- **Focal Length (mm)**: Distance from lens to focal point
  - Example: 1000mm for an f/5 telescope

**Camera Settings:**
- **Sensor Width (mm)**: Horizontal dimension of your camera sensor
  - Full frame: ~36mm
  - APS-C: ~23.5mm
  - Micro 4/3: ~17.3mm
- **Sensor Height (mm)**: Vertical dimension
  - Full frame: ~24mm
  - APS-C: ~15.6mm
  - Micro 4/3: ~13mm

**Quick Presets:**
- Click preset buttons for common setups
- Field of View is calculated automatically
- Helps match targets to your equipment

### 3. Set Observation Time

**Date & Time:**
- Select the date you plan to observe
- Choose start time (default: 9 PM)
- Set duration (1-12 hours)

**Preferences:**
- **Minimum Altitude**: Objects below this won't be shown (default: 30°)
  - Higher altitude = better seeing conditions
  - Lower altitude = more objects available
- **Moon Avoidance**: Minimum distance from moon (default: 30°)
  - Larger value = darker skies
  - Smaller value = more objects available

**Quick Presets:**
- Evening (9 PM, 4 hours)
- Night (10 PM, 6 hours)
- Midnight (12 AM, 5 hours)

### 4. Calculate Targets

Click the **"Calculate Best Targets"** button to get your personalized recommendations!

## 📊 Understanding the Results

### Target Cards

Each recommended target shows:

**Header:**
- **Rank**: Position in recommendations (#1 is best)
- **ID & Name**: Messier number and common name
- **Constellation**: Where to find it in the sky
- **Score**: Overall rating (0-100)
  - 80-100: Excellent (green)
  - 60-79: Good (blue)
  - 40-59: Fair (yellow)
  - 0-39: Poor (red)

**Badges:**
- **Difficulty**: Easy, Moderate, or Challenging
- **Equipment Match**: How well it fits your setup
- **Magnitude**: Brightness (lower = brighter)
- **Size**: Angular size in arcminutes

**Visibility Info:**
- **Peak Time**: When object is highest in sky
- **Peak Altitude**: Maximum height above horizon
- **Duration**: Hours above minimum altitude
- **Moon Separation**: Angular distance from moon

### Moon Information

Displayed at top of results:
- **Phase**: New, Waxing Crescent, First Quarter, etc.
- **Illumination**: Percentage of moon lit (0-100%)

## 🎓 Understanding the Scoring

Targets are scored based on multiple factors:

### Visibility (40%)
- Higher altitude = better score
- Objects near zenith (90°) score highest
- Low altitude objects affected by atmosphere

### Brightness (25%)
- Brighter objects (lower magnitude) score higher
- Magnitude < 5: Excellent
- Magnitude 5-8: Good
- Magnitude 8-10: Moderate
- Magnitude > 10: Challenging

### Equipment Match (15%)
- How well object fits your field of view
- Ideal: Object takes 30-70% of frame
- Too small: Hard to see details
- Too large: Won't fit in frame

### Moon Impact (10%)
- Greater separation = higher score
- < 30°: Significant interference
- 30-60°: Moderate interference
- > 60°: Minimal interference

### Weather (10%)
- Currently not implemented
- Will include cloud cover when available

## 💡 Tips for Best Results

### Location
- Use your exact observing site
- Dark sky sites will have more options
- Consider light pollution in your area

### Equipment
- Accurate specs give better matches
- Try different equipment presets
- Wider field = more large objects
- Longer focal length = smaller objects

### Timing
- Plan around moon phase
- New moon = darkest skies
- Full moon = brightest objects only
- Check weather forecast separately

### Observation
- Start with "Easy" difficulty targets
- Higher altitude = better seeing
- Allow time for setup and focusing
- Consider multiple targets per session

## 🌟 Object Types Explained

### Galaxies
- Distant collections of stars
- Require dark skies
- Long exposures reveal structure
- Examples: M31 (Andromeda), M51 (Whirlpool)

### Nebulae
- Clouds of gas and dust
- Often colorful in images
- Good for narrowband filters
- Examples: M42 (Orion), M8 (Lagoon)

### Open Clusters
- Groups of young stars
- Wide field targets
- Beautiful star colors
- Examples: M45 (Pleiades), M44 (Beehive)

### Globular Clusters
- Dense spherical star clusters
- Require higher magnification
- Thousands of stars
- Examples: M13 (Hercules), M3

### Planetary Nebulae
- Shells of gas from dying stars
- Small but bright
- OIII filter recommended
- Examples: M27 (Dumbbell), M57 (Ring)

## 🔧 Troubleshooting

### "Backend API Not Running"
**Solution:**
```bash
cd astrophotography-engine/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### "No suitable targets found"
**Possible causes:**
- Observation time during daylight
- Moon avoidance too strict
- Minimum altitude too high
- Wrong hemisphere for selected objects

**Solutions:**
- Choose nighttime hours
- Reduce moon avoidance to 20°
- Lower minimum altitude to 20°
- Check your latitude is correct

### "Failed to find location"
**Solutions:**
- Try different address format
- Use city name only
- Enter coordinates manually
- Check internet connection

### Targets seem wrong
**Check:**
- Correct hemisphere (N/S)
- Correct timezone
- Date is correct
- Time is in 24-hour format

## 📱 Keyboard Shortcuts

- **Enter** in address field: Search location
- **Tab**: Navigate between fields
- **Escape**: Close error messages

## 🎯 Example Workflows

### Beginner Setup
1. Location: Your city
2. Equipment: 80mm refractor preset
3. Time: Evening preset (9 PM, 4 hours)
4. Preferences: Default (30° min altitude, 30° moon avoidance)
5. Look for "Easy" difficulty targets

### Intermediate Setup
1. Location: Dark sky site coordinates
2. Equipment: 8" SCT preset
3. Time: Custom (10 PM, 6 hours)
4. Preferences: 40° min altitude, 45° moon avoidance
5. Mix of "Easy" and "Moderate" targets

### Advanced Setup
1. Location: Precise coordinates with elevation
2. Equipment: Custom long focal length setup
3. Time: Midnight start, 8 hours
4. Preferences: 50° min altitude, 60° moon avoidance
5. Focus on "Challenging" targets

## 📚 Additional Resources

### Learning More
- [Messier Catalogue](https://en.wikipedia.org/wiki/Messier_object)
- [Astropy Documentation](https://docs.astropy.org)
- [Astrophotography Basics](https://www.cloudynights.com)

### Equipment Help
- Telescope specifications usually on tube or mount
- Camera sensor size in manual or manufacturer website
- Online calculators for field of view verification

### Planning Tools
- Clear Sky Chart for weather
- Stellarium for sky simulation
- PhotoPills for planning

## 🆘 Getting Help

If you encounter issues:
1. Check this guide first
2. Verify backend is running
3. Check browser console for errors
4. Review API documentation
5. Check GitHub issues

## 🎉 Happy Imaging!

Remember:
- Start with bright, easy targets
- Practice makes perfect
- Dark skies make a huge difference
- Have fun exploring the universe!

---

**Made with ❤️ for astrophotographers**