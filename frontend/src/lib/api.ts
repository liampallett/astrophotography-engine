const API_BASE_URL = 'http://localhost:8000/api/v1';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

// Messier Catalogue Types
export interface MessierObject {
  id: string;
  messier_number: number;
  ngc_id: string | null;
  name: string;
  type: string;
  ra_hours: number;
  dec_degrees: number;
  magnitude: number;
  size_arcmin: number;
  constellation: string;
  best_months: string[];
  min_aperture_mm: number;
  difficulty: string;
  description: string;
  imaging_notes: string | null;
  distance_ly: number | null;
}

export interface MessierCatalogueResponse {
  objects: MessierObject[];
  count: number;
}

// Location Types
export interface Location {
  latitude: number;
  longitude: number;
  timezone: string;
  elevation?: number;
}

export interface GeocodeResponse {
  latitude: number;
  longitude: number;
  timezone: string;
  elevation: number;
  display_name: string;
  country: string;
}

// Equipment Types
export interface Equipment {
  aperture_mm: number;
  focal_length_mm: number;
  sensor_width_mm: number;
  sensor_height_mm: number;
}

// Observation Types
export interface Observation {
  date: string; // YYYY-MM-DD
  start_time: string; // HH:MM:SS
  duration_hours: number;
}

// Preferences Types
export interface Preferences {
  min_altitude: number;
  moon_avoidance_deg: number;
  include_planets: boolean;
}

// Target Calculation Request
export interface TargetCalculationRequest {
  location: Location;
  equipment: Equipment;
  observation: Observation;
  preferences: Preferences;
}

// Visibility Types
export interface Visibility {
  peak_time: string;
  peak_altitude: number;
  duration_hours: number;
}

// Moon Types
export interface MoonData {
  phase: string;
  illumination: number;
  rise_time?: string | null;
  set_time?: string | null;
}

export interface MoonInfo {
  altitude: number;
  azimuth: number;
  illumination: number;
  phase: string;
  phase_angle: number;
  observation_time?: string;
  location?: Location;
}

// Target Types
export interface Target {
  id: string;
  name: string;
  type: string;
  score: number;
  visibility: Visibility;
  moon_separation: number;
  weather_score: number | null;
  equipment_match: string;
  magnitude: number;
  size_arcmin: number;
  constellation: string;
  difficulty: string;
  description: string;
}

export interface TargetCalculationResponse {
  targets: Target[];
  moon: MoonData;
}

// ============================================================================
// CATALOGUE API
// ============================================================================

export async function getMessierCatalogue(): Promise<MessierObject[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/catalogue/messier`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data: MessierCatalogueResponse = await response.json();
    return data.objects;
  } catch (error) {
    console.error('Failed to fetch Messier catalogue:', error);
    throw error;
  }
}

export async function getMessierObject(id: string): Promise<MessierObject> {
  try {
    const response = await fetch(`${API_BASE_URL}/catalogue/messier/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch object ${id}:`, error);
    throw error;
  }
}

// ============================================================================
// LOCATION API
// ============================================================================

export async function geocodeAddress(address: string): Promise<GeocodeResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/location/geocode?address=${encodeURIComponent(address)}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to geocode address:', error);
    throw error;
  }
}

export async function reverseGeocode(
  latitude: number,
  longitude: number
): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/location/reverse?latitude=${latitude}&longitude=${longitude}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to reverse geocode:', error);
    throw error;
  }
}

export async function getTimezone(
  latitude: number,
  longitude: number
): Promise<{ timezone: string; utc_offset: number; dst_active: boolean }> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/location/timezone?latitude=${latitude}&longitude=${longitude}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to get timezone:', error);
    throw error;
  }
}

// ============================================================================
// MOON API
// ============================================================================

export async function getMoonInfo(
  latitude: number,
  longitude: number,
  date?: string,
  time?: string
): Promise<MoonInfo> {
  try {
    let url = `${API_BASE_URL}/moon?latitude=${latitude}&longitude=${longitude}`;
    if (date) url += `&date=${date}`;
    if (time) url += `&time=${time}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to get moon info:', error);
    throw error;
  }
}

export async function getMoonPhase(date?: string): Promise<{
  phase: string;
  illumination: number;
  phase_angle: number;
  date: string;
}> {
  try {
    let url = `${API_BASE_URL}/moon/phase`;
    if (date) url += `?date=${date}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to get moon phase:', error);
    throw error;
  }
}

// ============================================================================
// TARGETS API
// ============================================================================

export async function calculateTargets(
  request: TargetCalculationRequest
): Promise<TargetCalculationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/targets/calculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to calculate targets:', error);
    throw error;
  }
}

export async function getTonightTargets(
  latitude: number,
  longitude: number,
  equipment: Equipment
): Promise<TargetCalculationResponse> {
  try {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      aperture_mm: equipment.aperture_mm.toString(),
      focal_length_mm: equipment.focal_length_mm.toString(),
      sensor_width_mm: equipment.sensor_width_mm.toString(),
      sensor_height_mm: equipment.sensor_height_mm.toString(),
    });
    
    const response = await fetch(`${API_BASE_URL}/targets/tonight?${params}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to get tonight\'s targets:', error);
    throw error;
  }
}

export async function getTargetVisibility(
  objectId: string,
  latitude: number,
  longitude: number,
  date: string,
  time: string = '21:00:00',
  durationHours: number = 4
): Promise<any> {
  try {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      date: date,
      time: time,
      duration_hours: durationHours.toString(),
    });
    
    const response = await fetch(
      `${API_BASE_URL}/targets/visibility/${objectId}?${params}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to get target visibility:', error);
    throw error;
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:8000/health');
    return response.ok;
  } catch (error) {
    return false;
  }
}

export function formatMoonPhase(phase: string): string {
  const phaseNames: Record<string, string> = {
    'new': 'New Moon',
    'waxing_crescent': 'Waxing Crescent',
    'first_quarter': 'First Quarter',
    'waxing_gibbous': 'Waxing Gibbous',
    'full': 'Full Moon',
    'waning_gibbous': 'Waning Gibbous',
    'last_quarter': 'Last Quarter',
    'waning_crescent': 'Waning Crescent',
  };
  return phaseNames[phase] || phase;
}

export function formatDifficulty(difficulty: string): {
  label: string;
  color: string;
} {
  const difficultyMap: Record<string, { label: string; color: string }> = {
    'easy': { label: 'Easy', color: 'green' },
    'moderate': { label: 'Moderate', color: 'yellow' },
    'challenging': { label: 'Challenging', color: 'red' },
  };
  return difficultyMap[difficulty] || { label: difficulty, color: 'gray' };
}

export function formatEquipmentMatch(match: string): {
  label: string;
  color: string;
} {
  const matchMap: Record<string, { label: string; color: string }> = {
    'excellent': { label: 'Excellent', color: 'green' },
    'good': { label: 'Good', color: 'blue' },
    'fair': { label: 'Fair', color: 'yellow' },
    'poor': { label: 'Poor', color: 'red' },
  };
  return matchMap[match] || { label: match, color: 'gray' };
}

// Made with Bob - Phase 4
