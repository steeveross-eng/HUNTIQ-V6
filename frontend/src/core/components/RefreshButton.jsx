/**
 * RefreshButton - Core Component
 * ===============================
 * Reusable refresh/reset button with loading state.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

export const RefreshButton = ({ 
  onRefresh, 
  loading = false, 
  size = "sm",
  variant = "outline",
  className = "",
  showText = true,
  text = "Actualiser",
  tooltipText = null
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onRefresh}
      disabled={loading}
      className={className}
      title={tooltipText || text}
      data-testid="refresh-button"
    >
      <RefreshCw 
        className={`h-4 w-4 ${showText ? 'mr-2' : ''} ${loading ? 'animate-spin' : ''}`} 
      />
      {showText && text}
    </Button>
  );
};

export default RefreshButton;
