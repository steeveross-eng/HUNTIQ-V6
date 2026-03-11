/**
 * ConfirmDialog - Core Component
 * ===============================
 * Reusable confirmation dialog for destructive actions.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { AlertTriangle, Trash2, LogOut, XCircle } from 'lucide-react';

const presetIcons = {
  delete: Trash2,
  warning: AlertTriangle,
  logout: LogOut,
  cancel: XCircle
};

const presetColors = {
  delete: 'text-red-500',
  warning: 'text-amber-500',
  logout: 'text-orange-500',
  cancel: 'text-gray-500'
};

export const ConfirmDialog = ({
  open,
  onOpenChange,
  title = 'Confirmer l\'action',
  description = 'Êtes-vous sûr de vouloir continuer ?',
  confirmLabel = 'Confirmer',
  cancelLabel = 'Annuler',
  onConfirm,
  onCancel,
  preset = 'warning',
  icon: CustomIcon = null,
  destructive = false,
  loading = false
}) => {
  const Icon = CustomIcon || presetIcons[preset] || AlertTriangle;
  const iconColor = presetColors[preset] || presetColors.warning;

  const handleConfirm = () => {
    onConfirm?.();
    onOpenChange?.(false);
  };

  const handleCancel = () => {
    onCancel?.();
    onOpenChange?.(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="bg-card border-border">
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full bg-gray-800 ${iconColor}`}>
              <Icon className="h-5 w-5" />
            </div>
            <AlertDialogTitle className="text-white">
              {title}
            </AlertDialogTitle>
          </div>
          <AlertDialogDescription className="text-gray-400 mt-2">
            {description}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel 
            onClick={handleCancel}
            className="bg-transparent border-gray-700 text-gray-300 hover:bg-gray-800"
          >
            {cancelLabel}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={loading}
            className={
              destructive || preset === 'delete'
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-[#f5a623] hover:bg-[#d4891c] text-black'
            }
          >
            {loading ? 'Chargement...' : confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

/**
 * useConfirmDialog - Hook for managing confirm dialog state
 */
export const useConfirmDialog = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [config, setConfig] = React.useState({});
  const resolveRef = React.useRef(null);

  const confirm = (options = {}) => {
    return new Promise((resolve) => {
      resolveRef.current = resolve;
      setConfig(options);
      setIsOpen(true);
    });
  };

  const handleConfirm = () => {
    resolveRef.current?.(true);
    setIsOpen(false);
  };

  const handleCancel = () => {
    resolveRef.current?.(false);
    setIsOpen(false);
  };

  const DialogComponent = () => (
    <ConfirmDialog
      open={isOpen}
      onOpenChange={setIsOpen}
      onConfirm={handleConfirm}
      onCancel={handleCancel}
      {...config}
    />
  );

  return { confirm, ConfirmDialog: DialogComponent };
};

export default ConfirmDialog;
