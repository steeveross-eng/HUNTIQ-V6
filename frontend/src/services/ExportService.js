/**
 * ExportService - Export data to PDF and CSV
 * Phase P3.3 - Export functionality
 */
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const SPECIES_LABELS = {
  deer: 'Cerf',
  moose: 'Orignal',
  bear: 'Ours',
  wild_turkey: 'Dindon sauvage',
  duck: 'Canard',
  wild_boar: 'Sanglier',
  goose: 'Oie'
};

const WAYPOINT_TYPES = {
  hunting: 'Spot de chasse',
  stand: 'Mirador/Affût',
  camera: 'Caméra trail',
  feeder: 'Nourrisseur',
  sighting: 'Observation',
  parking: 'Stationnement',
  custom: 'Autre'
};

export const ExportService = {
  /**
   * Export data to CSV
   */
  exportToCSV(data, filename, headers) {
    const csvRows = [];
    
    // Add headers
    csvRows.push(headers.join(','));
    
    // Add data rows
    for (const row of data) {
      const values = headers.map(header => {
        const value = row[header] ?? '';
        // Escape quotes and wrap in quotes if contains comma
        const escaped = String(value).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }
    
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    
    this.downloadBlob(blob, `${filename}.csv`);
  },

  /**
   * Export waypoints to CSV
   */
  exportWaypointsCSV(waypoints) {
    const headers = ['name', 'type', 'lat', 'lng', 'notes', 'created_at'];
    const data = waypoints.map(wp => ({
      name: wp.name,
      type: WAYPOINT_TYPES[wp.type] || wp.type,
      lat: wp.lat,
      lng: wp.lng,
      notes: wp.notes || '',
      created_at: wp.created_at ? new Date(wp.created_at).toLocaleDateString('fr-CA') : ''
    }));
    
    this.exportToCSV(data, 'waypoints_bionic_hunt', headers);
  },

  /**
   * Export hunting trips to CSV
   */
  exportTripsCSV(trips) {
    const headers = ['date', 'species', 'duration_hours', 'success', 'observations', 'weather_conditions', 'temperature', 'lat', 'lng', 'notes'];
    const data = trips.map(trip => ({
      date: trip.date ? new Date(trip.date).toLocaleDateString('fr-CA') : '',
      species: SPECIES_LABELS[trip.species] || trip.species,
      duration_hours: trip.duration_hours,
      success: trip.success ? 'Oui' : 'Non',
      observations: trip.observations,
      weather_conditions: trip.weather_conditions || '',
      temperature: trip.temperature || '',
      lat: trip.location_lat,
      lng: trip.location_lng,
      notes: trip.notes || ''
    }));
    
    this.exportToCSV(data, 'sorties_chasse_bionic_hunt', headers);
  },

  /**
   * Export waypoints to PDF
   */
  exportWaypointsPDF(waypoints) {
    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(245, 166, 35); // BIONIC HUNT orange
    doc.text('BIONIC HUNT/Chasse - Mes Waypoints', 14, 20);
    
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Exporté le ${new Date().toLocaleDateString('fr-CA')}`, 14, 28);
    doc.text(`Total: ${waypoints.length} waypoints`, 14, 34);
    
    // Table
    const tableData = waypoints.map(wp => [
      wp.name,
      WAYPOINT_TYPES[wp.type] || wp.type,
      `${wp.lat.toFixed(4)}, ${wp.lng.toFixed(4)}`,
      wp.notes || '-'
    ]);
    
    doc.autoTable({
      startY: 42,
      head: [['Nom', 'Type', 'Coordonnées', 'Notes']],
      body: tableData,
      theme: 'striped',
      headStyles: {
        fillColor: [245, 166, 35],
        textColor: [0, 0, 0],
        fontStyle: 'bold'
      },
      styles: {
        fontSize: 9,
        cellPadding: 3
      },
      columnStyles: {
        0: { cellWidth: 50 },
        1: { cellWidth: 35 },
        2: { cellWidth: 45 },
        3: { cellWidth: 50 }
      }
    });
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(`BIONIC HUNT/Chasse - Page ${i}/${pageCount}`, doc.internal.pageSize.width / 2, doc.internal.pageSize.height - 10, { align: 'center' });
    }
    
    doc.save('waypoints_bionic_hunt.pdf');
  },

  /**
   * Export analytics report to PDF
   */
  exportAnalyticsPDF(analytics) {
    const doc = new jsPDF();
    const { overview, species_breakdown, weather_analysis, monthly_trends } = analytics;
    
    // Header
    doc.setFontSize(22);
    doc.setTextColor(245, 166, 35);
    doc.text('BIONIC HUNT/Chasse - Rapport Analytique', 14, 20);
    
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Généré le ${new Date().toLocaleDateString('fr-CA')} à ${new Date().toLocaleTimeString('fr-CA')}`, 14, 28);
    
    // Overview Section
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text('Vue d\'ensemble', 14, 42);
    
    doc.setFontSize(10);
    doc.setTextColor(60);
    let y = 50;
    doc.text(`• Sorties totales: ${overview.total_trips}`, 20, y);
    doc.text(`• Sorties réussies: ${overview.successful_trips}`, 20, y + 6);
    doc.text(`• Taux de succès: ${overview.success_rate}%`, 20, y + 12);
    doc.text(`• Heures de chasse: ${overview.total_hours}h`, 20, y + 18);
    doc.text(`• Observations: ${overview.total_observations}`, 20, y + 24);
    doc.text(`• Durée moyenne: ${overview.avg_trip_duration}h`, 20, y + 30);
    
    // Species Breakdown
    if (species_breakdown && species_breakdown.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text('Répartition par espèce', 14, y + 46);
      
      const speciesData = species_breakdown.map(s => [
        SPECIES_LABELS[s.species] || s.species,
        s.trips.toString(),
        s.successes.toString(),
        `${s.success_rate}%`,
        s.total_observations.toString()
      ]);
      
      doc.autoTable({
        startY: y + 52,
        head: [['Espèce', 'Sorties', 'Succès', 'Taux', 'Observations']],
        body: speciesData,
        theme: 'striped',
        headStyles: {
          fillColor: [34, 197, 94],
          textColor: [255, 255, 255]
        },
        styles: { fontSize: 9 }
      });
    }
    
    // Weather Analysis
    if (weather_analysis && weather_analysis.length > 0) {
      const currentY = doc.lastAutoTable ? doc.lastAutoTable.finalY + 15 : y + 90;
      
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text('Analyse météo', 14, currentY);
      
      const weatherData = weather_analysis.map(w => [
        w.condition,
        w.trips.toString(),
        `${w.success_rate}%`,
        w.avg_observations.toFixed(1)
      ]);
      
      doc.autoTable({
        startY: currentY + 6,
        head: [['Condition', 'Sorties', 'Taux succès', 'Obs. moy.']],
        body: weatherData,
        theme: 'striped',
        headStyles: {
          fillColor: [59, 130, 246],
          textColor: [255, 255, 255]
        },
        styles: { fontSize: 9 }
      });
    }
    
    // Monthly Trends
    if (monthly_trends && monthly_trends.length > 0) {
      doc.addPage();
      
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text('Tendances mensuelles', 14, 20);
      
      const trendsData = monthly_trends.map(t => [
        `${t.month} ${t.year}`,
        t.trips.toString(),
        t.successes.toString(),
        `${t.success_rate}%`,
        t.observations.toString()
      ]);
      
      doc.autoTable({
        startY: 26,
        head: [['Mois', 'Sorties', 'Succès', 'Taux', 'Observations']],
        body: trendsData,
        theme: 'striped',
        headStyles: {
          fillColor: [139, 92, 246],
          textColor: [255, 255, 255]
        },
        styles: { fontSize: 9 }
      });
    }
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(`BIONIC HUNT/Chasse - Rapport Analytique - Page ${i}/${pageCount}`, doc.internal.pageSize.width / 2, doc.internal.pageSize.height - 10, { align: 'center' });
    }
    
    doc.save('rapport_analytique_bionic_hunt.pdf');
  },

  /**
   * Export hunting trips to PDF
   */
  exportTripsPDF(trips) {
    const doc = new jsPDF('l'); // Landscape for more columns
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(245, 166, 35);
    doc.text('BIONIC HUNT/Chasse - Journal de Chasse', 14, 20);
    
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Exporté le ${new Date().toLocaleDateString('fr-CA')}`, 14, 28);
    doc.text(`Total: ${trips.length} sorties`, 14, 34);
    
    // Table
    const tableData = trips.map(trip => [
      trip.date ? new Date(trip.date).toLocaleDateString('fr-CA') : '-',
      SPECIES_LABELS[trip.species] || trip.species,
      `${trip.duration_hours}h`,
      trip.success ? 'Oui' : 'Non',
      trip.observations.toString(),
      trip.weather_conditions || '-',
      trip.temperature ? `${trip.temperature}°C` : '-'
    ]);
    
    doc.autoTable({
      startY: 42,
      head: [['Date', 'Espèce', 'Durée', 'Succès', 'Obs.', 'Météo', 'Temp.']],
      body: tableData,
      theme: 'striped',
      headStyles: {
        fillColor: [245, 166, 35],
        textColor: [0, 0, 0],
        fontStyle: 'bold'
      },
      styles: {
        fontSize: 9,
        cellPadding: 3
      }
    });
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(`BIONIC HUNT/Chasse - Journal de Chasse - Page ${i}/${pageCount}`, doc.internal.pageSize.width / 2, doc.internal.pageSize.height - 10, { align: 'center' });
    }
    
    doc.save('journal_chasse_bionic_hunt.pdf');
  },

  /**
   * Download blob as file
   */
  downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};

export default ExportService;
