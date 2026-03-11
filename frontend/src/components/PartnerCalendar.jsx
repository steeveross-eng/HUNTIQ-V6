/**
 * PartnerCalendar - Dynamic availability calendar for partners
 * Allows partners to manage their availability and view reservations
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  Clock,
  Lock,
  Unlock,
  Users,
  DollarSign,
  RefreshCw,
  Plus,
  AlertCircle
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Status colors
const STATUS_COLORS = {
  available: 'bg-green-500/20 text-green-500 border-green-500/30',
  reserved: 'bg-blue-500/20 text-blue-500 border-blue-500/30',
  blocked: 'bg-gray-500/20 text-gray-500 border-gray-500/30',
  pending: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30'
};

const STATUS_LABELS = {
  available: { fr: 'Disponible', en: 'Available' },
  reserved: { fr: 'Réservé', en: 'Reserved' },
  blocked: { fr: 'Bloqué', en: 'Blocked' },
  pending: { fr: 'En attente', en: 'Pending' }
};

const DAYS_FR = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const DAYS_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
const MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

const PartnerCalendar = ({ partnerId, offers = [] }) => {
  const { language } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarData, setCalendarData] = useState(null);
  const [selectedOffer, setSelectedOffer] = useState('all');
  const [selectedDate, setSelectedDate] = useState(null);
  const [showDayModal, setShowDayModal] = useState(false);
  const [selectedDayData, setSelectedDayData] = useState(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth() + 1;
  const DAYS = language === 'fr' ? DAYS_FR : DAYS_EN;
  const MONTHS = language === 'fr' ? MONTHS_FR : MONTHS_EN;

  useEffect(() => {
    if (partnerId) {
      loadCalendarData();
    }
  }, [partnerId, year, month]);

  const loadCalendarData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/api/partnership/calendar/${partnerId}`, {
        params: { year, month }
      });
      setCalendarData(response.data);
    } catch (error) {
      console.error('Error loading calendar:', error);
    }
    setLoading(false);
  };

  const previousMonth = () => {
    setCurrentDate(new Date(year, month - 2, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getDaysInMonth = () => {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = (firstDay.getDay() + 6) % 7; // Adjust for Monday start
    
    const days = [];
    
    // Previous month days
    for (let i = startingDay - 1; i >= 0; i--) {
      const prevDate = new Date(year, month - 1, -i);
      days.push({
        date: prevDate,
        day: prevDate.getDate(),
        isCurrentMonth: false,
        dateStr: formatDateStr(prevDate)
      });
    }
    
    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(year, month - 1, i);
      days.push({
        date,
        day: i,
        isCurrentMonth: true,
        dateStr: formatDateStr(date)
      });
    }
    
    // Next month days to complete the grid
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      const nextDate = new Date(year, month, i);
      days.push({
        date: nextDate,
        day: i,
        isCurrentMonth: false,
        dateStr: formatDateStr(nextDate)
      });
    }
    
    return days;
  };

  const formatDateStr = (date) => {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  };

  const getDayStatus = (dateStr) => {
    if (!calendarData) return null;
    
    const availability = calendarData.availability?.[dateStr] || [];
    const reservations = calendarData.reservations?.[dateStr] || [];
    
    // Filter by selected offer if not 'all'
    const filteredAvail = selectedOffer === 'all' 
      ? availability 
      : availability.filter(a => a.offer_id === selectedOffer);
    
    const filteredRes = selectedOffer === 'all'
      ? reservations
      : reservations.filter(r => r.offer_id === selectedOffer);
    
    if (filteredRes.length > 0) {
      const hasConfirmed = filteredRes.some(r => r.status === 'confirmed');
      const hasPending = filteredRes.some(r => r.status === 'pending');
      if (hasConfirmed) return 'reserved';
      if (hasPending) return 'pending';
    }
    
    if (filteredAvail.length > 0) {
      const hasBlocked = filteredAvail.some(a => a.status === 'blocked');
      const hasAvailable = filteredAvail.some(a => a.status === 'available');
      if (hasBlocked && !hasAvailable) return 'blocked';
      if (hasAvailable) return 'available';
    }
    
    return null;
  };

  const handleDayClick = (dayData) => {
    if (!dayData.isCurrentMonth) return;
    
    const dateStr = dayData.dateStr;
    const availability = calendarData?.availability?.[dateStr] || [];
    const reservations = calendarData?.reservations?.[dateStr] || [];
    
    setSelectedDate(dateStr);
    setSelectedDayData({
      date: dateStr,
      availability: selectedOffer === 'all' ? availability : availability.filter(a => a.offer_id === selectedOffer),
      reservations: selectedOffer === 'all' ? reservations : reservations.filter(r => r.offer_id === selectedOffer)
    });
    setShowDayModal(true);
  };

  const setAvailabilityStatus = async (offerId, date, status) => {
    try {
      await axios.post(`${API}/api/partnership/availability`, {
        offer_id: offerId,
        date: date,
        status: status
      });
      toast.success(language === 'fr' ? 'Disponibilité mise à jour' : 'Availability updated');
      loadCalendarData();
      setShowDayModal(false);
    } catch (error) {
      toast.error(language === 'fr' ? 'Erreur lors de la mise à jour' : 'Update error');
    }
  };

  const handleReservationAction = async (reservationId, action) => {
    try {
      await axios.post(`${API}/api/partnership/reservations/${reservationId}/respond`, {
        action: action
      });
      toast.success(action === 'confirm' 
        ? (language === 'fr' ? 'Réservation confirmée!' : 'Reservation confirmed!')
        : (language === 'fr' ? 'Réservation annulée' : 'Reservation cancelled'));
      loadCalendarData();
      setShowDayModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error');
    }
  };

  const isToday = (dateStr) => {
    return dateStr === formatDateStr(new Date());
  };

  const days = getDaysInMonth();

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <Calendar className="h-5 w-5 text-[#f5a623]" />
              {language === 'fr' ? 'Calendrier des disponibilités' : 'Availability Calendar'}
            </CardTitle>
            <CardDescription>
              {language === 'fr' 
                ? 'Gérez vos disponibilités et consultez les réservations'
                : 'Manage your availability and view reservations'}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedOffer} onValueChange={setSelectedOffer}>
              <SelectTrigger className="w-[200px] bg-background">
                <SelectValue placeholder={language === 'fr' ? 'Toutes les offres' : 'All offers'} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{language === 'fr' ? 'Toutes les offres' : 'All offers'}</SelectItem>
                {(calendarData?.offers || offers).map((offer) => (
                  <SelectItem key={offer.id} value={offer.id}>{offer.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={loadCalendarData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Calendar Navigation */}
        <div className="flex items-center justify-between mb-4">
          <Button variant="ghost" onClick={previousMonth}>
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-white">
              {MONTHS[month - 1]} {year}
            </h3>
            <Button variant="outline" size="sm" onClick={goToToday}>
              {language === 'fr' ? "Aujourd'hui" : 'Today'}
            </Button>
          </div>
          <Button variant="ghost" onClick={nextMonth}>
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mb-4 text-xs">
          {Object.entries(STATUS_LABELS).map(([status, labels]) => (
            <div key={status} className="flex items-center gap-1">
              <div className={`w-3 h-3 rounded ${STATUS_COLORS[status].split(' ')[0]}`}></div>
              <span className="text-gray-400">{labels[language]}</span>
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {/* Day headers */}
          {DAYS.map((day) => (
            <div key={day} className="text-center text-xs text-gray-500 py-2 font-medium">
              {day}
            </div>
          ))}
          
          {/* Day cells */}
          {days.map((dayData, index) => {
            const status = dayData.isCurrentMonth ? getDayStatus(dayData.dateStr) : null;
            const reservations = calendarData?.reservations?.[dayData.dateStr] || [];
            const hasReservation = reservations.length > 0;
            
            return (
              <button
                key={index}
                onClick={() => handleDayClick(dayData)}
                disabled={!dayData.isCurrentMonth}
                className={`
                  relative p-2 min-h-[60px] rounded-lg border transition-all text-left
                  ${!dayData.isCurrentMonth 
                    ? 'bg-background/30 text-gray-600 cursor-not-allowed border-transparent' 
                    : `hover:bg-white/5 cursor-pointer ${status ? STATUS_COLORS[status] : 'bg-background/50 border-border'}`
                  }
                  ${isToday(dayData.dateStr) ? 'ring-2 ring-[#f5a623]' : ''}
                `}
              >
                <span className={`text-sm font-medium ${dayData.isCurrentMonth ? '' : 'opacity-50'}`}>
                  {dayData.day}
                </span>
                
                {/* Reservation indicator */}
                {hasReservation && dayData.isCurrentMonth && (
                  <div className="absolute bottom-1 right-1">
                    <div className="flex items-center gap-0.5">
                      <Users className="h-3 w-3" />
                      <span className="text-[10px]">{reservations.length}</span>
                    </div>
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* No data message */}
        {!calendarData && !loading && (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>{language === 'fr' ? 'Créez une offre pour commencer' : 'Create an offer to get started'}</p>
          </div>
        )}
      </CardContent>

      {/* Day Detail Modal */}
      <Dialog open={showDayModal} onOpenChange={setShowDayModal}>
        <DialogContent className="bg-card border-border text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-[#f5a623]" />
              {selectedDate}
            </DialogTitle>
            <DialogDescription>
              {language === 'fr' ? 'Gérer cette date' : 'Manage this date'}
            </DialogDescription>
          </DialogHeader>

          {selectedDayData && (
            <div className="space-y-4">
              {/* Reservations */}
              {selectedDayData.reservations.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">
                    {language === 'fr' ? 'Réservations' : 'Reservations'}
                  </h4>
                  <div className="space-y-2">
                    {selectedDayData.reservations.map((res, idx) => (
                      <Card key={idx} className="bg-background/50 border-border">
                        <CardContent className="p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-white">{res.client_name}</p>
                              <p className="text-xs text-gray-400">{res.offer_title}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge className={STATUS_COLORS[res.status]}>
                                  {STATUS_LABELS[res.status]?.[language] || res.status}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  <Users className="h-3 w-3 inline mr-1" />
                                  {res.guests}
                                </span>
                              </div>
                            </div>
                            {res.status === 'pending' && (
                              <div className="flex gap-1">
                                <Button 
                                  size="sm" 
                                  className="bg-green-600 hover:bg-green-700"
                                  onClick={() => handleReservationAction(res.id, 'confirm')}
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  className="border-red-500 text-red-500"
                                  onClick={() => handleReservationAction(res.id, 'cancel')}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Availability Actions */}
              {selectedDayData.reservations.filter(r => r.status === 'confirmed').length === 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">
                    {language === 'fr' ? 'Disponibilité' : 'Availability'}
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {(calendarData?.offers || []).map((offer) => (
                      <div key={offer.id} className="space-y-2">
                        <p className="text-xs text-gray-400 truncate">{offer.title}</p>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 border-green-500 text-green-500 hover:bg-green-500/10"
                            onClick={() => setAvailabilityStatus(offer.id, selectedDate, 'available')}
                          >
                            <Unlock className="h-3 w-3 mr-1" />
                            {language === 'fr' ? 'Ouvrir' : 'Open'}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 border-gray-500 text-gray-500 hover:bg-gray-500/10"
                            onClick={() => setAvailabilityStatus(offer.id, selectedDate, 'blocked')}
                          >
                            <Lock className="h-3 w-3 mr-1" />
                            {language === 'fr' ? 'Bloquer' : 'Block'}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDayModal(false)}>
              {language === 'fr' ? 'Fermer' : 'Close'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default PartnerCalendar;
