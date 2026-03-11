/**
 * RefreshButton - Reusable refresh/reset button component
 * Resets filters and reloads data across all pages
 */

import React from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";

const RefreshButton = ({ 
  onRefresh, 
  loading = false, 
  size = "sm",
  variant = "outline",
  className = "",
  showText = true,
  tooltipText = null
}) => {
  const { t } = useLanguage();
  
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onRefresh}
      disabled={loading}
      className={`${className}`}
      title={tooltipText || t('common_refresh') || "Actualiser"}
      data-testid="refresh-button"
    >
      <RefreshCw className={`h-4 w-4 ${showText ? 'mr-2' : ''} ${loading ? 'animate-spin' : ''}`} />
      {showText && (t('common_refresh') || "Actualiser")}
    </Button>
  );
};

export default RefreshButton;
