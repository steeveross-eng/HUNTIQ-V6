/**
 * CreateTripModal - Modal for creating a new hunting trip
 * BIONIC Design System compliant - No emojis
 */
import React, { useState } from 'react';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { CalendarIcon, Loader2, Target } from 'lucide-react';
import TripService from '@/services/TripService';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';
import { getSpeciesName } from '@/config/speciesImages';

const SPECIES_OPTIONS = [
  { value: 'deer', label: 'Chevreuil' },
  { value: 'moose', label: 'Orignal' },
  { value: 'bear', label: 'Ours noir' },
  { value: 'turkey', label: 'Dindon sauvage' },
  { value: 'duck', label: 'Canard' },
  { value: 'goose', label: 'Oie' },
  { value: 'hare', label: 'Lièvre' },
  { value: 'coyote', label: 'Coyote' },
  { value: 'other', label: 'Autre' }
];

const CreateTripModal = ({ open, onClose, onTripCreated }) => {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: '',
    target_species: 'deer',
    planned_date: new Date(),
    notes: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const tripData = {
        title: form.title || `Sortie ${SPECIES_OPTIONS.find(s => s.value === form.target_species)?.label || form.target_species}`,
        target_species: form.target_species,
        planned_date: form.planned_date.toISOString(),
        notes: form.notes || null
      };

      const result = await TripService.createTrip(tripData);

      if (result.success) {
        onTripCreated(result.trip);
        // Reset form
        setForm({
          title: '',
          target_species: 'deer',
          planned_date: new Date(),
          notes: ''
        });
      } else {
        toast.error(result.detail || 'Erreur lors de la création');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const selectedSpecies = SPECIES_OPTIONS.find(s => s.value === form.target_species);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-slate-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-2">
            <Target className="h-5 w-5 text-[#f5a623]" />
            Nouvelle Sortie de Chasse
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Planifiez votre prochaine sortie
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-gray-300">Titre (optionnel)</Label>
            <Input
              id="title"
              placeholder="Ex: Sortie matinale zone nord"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="bg-slate-800 border-slate-600 text-white"
            />
          </div>

          {/* Species */}
          <div className="space-y-2">
            <Label className="text-gray-300">Espèce ciblée</Label>
            <Select
              value={form.target_species}
              onValueChange={(value) => setForm({ ...form, target_species: value })}
            >
              <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                <SelectValue>
                  {selectedSpecies && (
                    <span className="flex items-center gap-2">
                      <SpeciesIcon species={selectedSpecies.value} size="xs" rounded />
                      <span>{selectedSpecies.label}</span>
                    </span>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {SPECIES_OPTIONS.map((species) => (
                  <SelectItem 
                    key={species.value} 
                    value={species.value}
                    className="text-white hover:bg-slate-700"
                  >
                    <span className="flex items-center gap-2">
                      <SpeciesIcon species={species.value} size="xs" rounded />
                      {species.label}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date */}
          <div className="space-y-2">
            <Label className="text-gray-300">Date prévue</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {form.planned_date ? (
                    format(form.planned_date, 'PPP', { locale: fr })
                  ) : (
                    <span>Choisir une date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 bg-slate-800 border-slate-600" align="start">
                <Calendar
                  mode="single"
                  selected={form.planned_date}
                  onSelect={(date) => date && setForm({ ...form, planned_date: date })}
                  initialFocus
                  locale={fr}
                  className="text-white"
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-gray-300">Notes (optionnel)</Label>
            <Textarea
              id="notes"
              placeholder="Objectifs, équipement prévu, etc."
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              className="bg-slate-800 border-slate-600 text-white resize-none"
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-slate-600 text-gray-300 hover:bg-slate-800"
              disabled={loading}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-[#f5a623] hover:bg-[#d4890e] text-black font-semibold"
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Créer la sortie
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateTripModal;
