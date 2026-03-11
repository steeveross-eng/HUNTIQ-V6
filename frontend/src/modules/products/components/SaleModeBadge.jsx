/**
 * SaleModeBadge - Products Module Component
 * ==========================================
 * Badge for displaying product sale mode.
 * Architecture LEGO V5 - Business Module
 * 
 * @module modules/products/components
 */
import React from "react";
import { Badge } from "@/components/ui/badge";

/**
 * SaleModeBadge - Display product sale mode
 * @param {string} mode - "dropshipping", "affiliation", or "hybrid"
 */
export const SaleModeBadge = ({ mode }) => {
  const config = {
    dropshipping: { color: "bg-blue-600", label: "Dropshipping" },
    affiliation: { color: "bg-purple-600", label: "Affiliation" },
    hybrid: { color: "bg-gradient-to-r from-blue-600 to-purple-600", label: "Hybride" }
  };
  const { color, label } = config[mode] || config.dropshipping;
  return <Badge className={`${color} text-white text-xs`}>{label}</Badge>;
};

export default SaleModeBadge;
