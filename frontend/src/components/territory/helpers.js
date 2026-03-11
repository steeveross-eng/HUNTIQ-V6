/**
 * Territory Utility Helpers
 * Pure functions extracted from TerritoryMap.jsx (Phase 1)
 * 
 * @module territory/helpers
 */

/**
 * Calculate distance between two points using Haversine formula
 * @param {number} lat1 - Start latitude
 * @param {number} lon1 - Start longitude
 * @param {number} lat2 - End latitude
 * @param {number} lon2 - End longitude
 * @returns {number} Distance in km
 */
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

/**
 * Calculate total distance for a series of points
 * @param {Array<{lat: number, lng: number}>} points - Array of lat/lng points
 * @returns {number} Total distance in km
 */
export const calculateTotalDistance = (points) => {
  let total = 0;
  for (let i = 1; i < points.length; i++) {
    const p1 = points[i - 1];
    const p2 = points[i];
    total += calculateDistance(p1.lat, p1.lng, p2.lat, p2.lng);
  }
  return total;
};
