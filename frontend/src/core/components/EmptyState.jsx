/**
 * EmptyState - Core Component
 * ============================
 * Reusable empty state placeholder with customizable icon and text.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React from 'react';
import { Button } from '@/components/ui/button';
import { 
  FileQuestion, 
  Search, 
  Inbox, 
  FolderOpen, 
  AlertCircle,
  Plus 
} from 'lucide-react';

const presetIcons = {
  empty: Inbox,
  search: Search,
  folder: FolderOpen,
  file: FileQuestion,
  error: AlertCircle
};

export const EmptyState = ({
  icon: CustomIcon = null,
  preset = 'empty',
  title = 'Aucun élément',
  description = null,
  actionLabel = null,
  onAction = null,
  actionIcon: ActionIcon = Plus,
  className = '',
  size = 'md'
}) => {
  const Icon = CustomIcon || presetIcons[preset] || Inbox;
  
  const sizeConfig = {
    sm: {
      container: 'py-6',
      icon: 'h-10 w-10',
      iconContainer: 'w-16 h-16',
      title: 'text-base',
      description: 'text-xs'
    },
    md: {
      container: 'py-12',
      icon: 'h-12 w-12',
      iconContainer: 'w-20 h-20',
      title: 'text-lg',
      description: 'text-sm'
    },
    lg: {
      container: 'py-16',
      icon: 'h-16 w-16',
      iconContainer: 'w-24 h-24',
      title: 'text-xl',
      description: 'text-base'
    }
  };

  const config = sizeConfig[size];

  return (
    <div 
      className={`flex flex-col items-center justify-center text-center ${config.container} ${className}`}
      data-testid="empty-state"
    >
      <div className={`${config.iconContainer} rounded-full bg-gray-800/50 flex items-center justify-center mb-4`}>
        <Icon className={`${config.icon} text-gray-500`} />
      </div>
      
      <h3 className={`text-white font-semibold mb-2 ${config.title}`}>
        {title}
      </h3>
      
      {description && (
        <p className={`text-gray-400 ${config.description} max-w-sm`}>
          {description}
        </p>
      )}
      
      {actionLabel && onAction && (
        <Button
          onClick={onAction}
          className="mt-6 bg-[#f5a623] hover:bg-[#d4891c] text-black"
          data-testid="empty-state-action"
        >
          <ActionIcon className="h-4 w-4 mr-2" />
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

/**
 * NoResults - Search-specific empty state
 */
export const NoResults = ({
  searchTerm = '',
  onClear = null,
  className = ''
}) => (
  <EmptyState
    preset="search"
    title="Aucun résultat"
    description={
      searchTerm 
        ? `Aucun résultat pour "${searchTerm}". Essayez avec d'autres termes.`
        : "Modifiez vos filtres pour trouver ce que vous cherchez."
    }
    actionLabel={onClear ? "Effacer les filtres" : null}
    onAction={onClear}
    className={className}
  />
);

/**
 * ErrorState - Error-specific empty state
 */
export const ErrorState = ({
  title = 'Une erreur est survenue',
  description = "Veuillez réessayer plus tard.",
  onRetry = null,
  className = ''
}) => (
  <EmptyState
    preset="error"
    title={title}
    description={description}
    actionLabel={onRetry ? "Réessayer" : null}
    onAction={onRetry}
    className={className}
  />
);

export default EmptyState;
