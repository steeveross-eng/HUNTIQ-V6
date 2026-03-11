/**
 * GPX Export Utilities
 * Functions to export waypoints and tracks to GPX format
 */

/**
 * Generate GPX XML from waypoints
 * @param {Array} waypoints - Array of waypoint objects {name, lat, lng, type, notes}
 * @param {string} trackName - Optional track name
 * @returns {string} GPX XML string
 */
export const generateGPX = (waypoints, trackName = 'Bionic Hunt Export') => {
  const now = new Date().toISOString();
  
  let gpxContent = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Chasse Bionic™ / Bionic Hunt™"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>${escapeXml(trackName)}</name>
    <desc>Waypoints exported from Chasse Bionic™ Territory Map</desc>
    <author>
      <name>Chasse Bionic™</name>
      <link href="https://chassebionic.ca">
        <text>chassebionic.ca</text>
      </link>
    </author>
    <time>${now}</time>
  </metadata>
`;

  // Add waypoints
  waypoints.forEach((wp, index) => {
    const typeSymbol = getGPXSymbol(wp.type);
    gpxContent += `  <wpt lat="${wp.lat}" lon="${wp.lng}">
    <name>${escapeXml(wp.name || `Waypoint ${index + 1}`)}</name>
    <desc>${escapeXml(wp.notes || wp.type || 'Custom waypoint')}</desc>
    <sym>${typeSymbol}</sym>
    <type>${escapeXml(wp.type || 'custom')}</type>
    <time>${now}</time>
  </wpt>
`;
  });

  // If we have multiple waypoints, create a route
  if (waypoints.length > 1) {
    gpxContent += `  <rte>
    <name>${escapeXml(trackName)} Route</name>
`;
    waypoints.forEach((wp, index) => {
      gpxContent += `    <rtept lat="${wp.lat}" lon="${wp.lng}">
      <name>${escapeXml(wp.name || `Point ${index + 1}`)}</name>
    </rtept>
`;
    });
    gpxContent += `  </rte>
`;
  }

  gpxContent += `</gpx>`;
  
  return gpxContent;
};

/**
 * Convert waypoint type to GPX symbol
 */
const getGPXSymbol = (type) => {
  const symbols = {
    custom: 'Flag, Blue',
    cache: 'Geocache',
    feeding: 'Forest',
    water: 'Drinking Water',
    crossing: 'Trail Head',
    camera: 'Photo',
    parking: 'Parking Area',
    danger: 'Skull and Crossbones'
  };
  return symbols[type] || 'Flag, Blue';
};

/**
 * Escape XML special characters
 */
const escapeXml = (str) => {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
};

/**
 * Download GPX file
 * @param {Array} waypoints - Array of waypoint objects
 * @param {string} filename - Filename without extension
 */
export const downloadGPX = (waypoints, filename = 'bionic-waypoints') => {
  if (!waypoints || waypoints.length === 0) {
    throw new Error('No waypoints to export');
  }

  const gpxContent = generateGPX(waypoints, filename);
  const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}_${new Date().toISOString().split('T')[0]}.gpx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  return true;
};

/**
 * Parse GPX file and extract waypoints
 * @param {string} gpxContent - GPX XML content
 * @returns {Array} Array of waypoint objects
 */
export const parseGPX = (gpxContent) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(gpxContent, 'application/xml');
  const waypoints = [];

  // Parse waypoints
  const wptElements = doc.querySelectorAll('wpt');
  wptElements.forEach((wpt, index) => {
    const lat = parseFloat(wpt.getAttribute('lat'));
    const lon = parseFloat(wpt.getAttribute('lon'));
    const name = wpt.querySelector('name')?.textContent || `Waypoint ${index + 1}`;
    const desc = wpt.querySelector('desc')?.textContent || '';
    const type = wpt.querySelector('type')?.textContent || 'custom';

    if (!isNaN(lat) && !isNaN(lon)) {
      waypoints.push({
        id: `imported_${Date.now()}_${index}`,
        lat,
        lng: lon,
        name,
        notes: desc,
        type: mapGPXTypeToLocal(type),
        imported: true
      });
    }
  });

  // Also parse route points if no waypoints found
  if (waypoints.length === 0) {
    const rteptElements = doc.querySelectorAll('rtept');
    rteptElements.forEach((rtept, index) => {
      const lat = parseFloat(rtept.getAttribute('lat'));
      const lon = parseFloat(rtept.getAttribute('lon'));
      const name = rtept.querySelector('name')?.textContent || `Point ${index + 1}`;

      if (!isNaN(lat) && !isNaN(lon)) {
        waypoints.push({
          id: `route_${Date.now()}_${index}`,
          lat,
          lng: lon,
          name,
          type: 'custom',
          imported: true
        });
      }
    });
  }

  return waypoints;
};

/**
 * Map GPX type string to local type
 */
const mapGPXTypeToLocal = (gpxType) => {
  const typeMap = {
    'custom': 'custom',
    'geocache': 'cache',
    'forest': 'feeding',
    'water': 'water',
    'drinking water': 'water',
    'trail': 'crossing',
    'photo': 'camera',
    'parking': 'parking',
    'danger': 'danger'
  };
  
  const normalized = (gpxType || '').toLowerCase();
  for (const [key, value] of Object.entries(typeMap)) {
    if (normalized.includes(key)) {
      return value;
    }
  }
  return 'custom';
};

export default {
  generateGPX,
  downloadGPX,
  parseGPX
};
