/**
 * placeTypes.js — Types de lieux BIONIC Design System
 * Extrait de MonTerritoireBionicPage.jsx (IM1 Refactorisation)
 */
import { Tent, Building, Lock, CircleDot, Target, Droplet, Eye, ParkingCircle, Pin } from 'lucide-react';
import { BIONIC_COLORS } from '@/config/bionic-colors';

export const PLACE_TYPES = [
  { id: 'zec', nameKey: 'place_zec', name: 'ZEC', Icon: Tent, color: BIONIC_COLORS?.green?.primary || '#22c55e' },
  { id: 'pourvoirie', nameKey: 'place_pourvoirie', name: 'Pourvoirie', Icon: Building, color: BIONIC_COLORS?.blue?.light || '#3b82f6' },
  { id: 'prive', nameKey: 'place_private', name: 'Territoire privé', Icon: Lock, color: BIONIC_COLORS?.gold?.primary || '#f5a623' },
  { id: 'sepaq', nameKey: 'place_sepaq', name: 'Réserve faunique (Sépaq)', Icon: CircleDot, color: BIONIC_COLORS?.purple?.primary || '#8b5cf6' },
  { id: 'affut', nameKey: 'place_affut', name: 'Affût / Cache', Icon: Target, color: BIONIC_COLORS?.red?.primary || '#ef4444' },
  { id: 'saline', nameKey: 'place_saline', name: 'Saline', Icon: Droplet, color: BIONIC_COLORS?.cyan?.primary || '#06b6d4' },
  { id: 'observation', nameKey: 'place_observation', name: 'Point d\'observation', Icon: Eye, color: '#ec4899' },
  { id: 'stationnement', nameKey: 'place_parking', name: 'Stationnement', Icon: ParkingCircle, color: BIONIC_COLORS?.gray?.[500] || '#6b7280' },
  { id: 'camp', nameKey: 'place_camp', name: 'Camp de chasse', Icon: Tent, color: '#84cc16' },
  { id: 'autre', nameKey: 'place_other', name: 'Autre lieu', Icon: Pin, color: BIONIC_COLORS?.purple?.light || '#a855f7' },
];
