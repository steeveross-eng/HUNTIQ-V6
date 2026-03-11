/**
 * BionicNavigation - BIONIC TACTICAL Design System
 * Unified navigation component with dropdown support
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { ChevronDown, Menu, X } from 'lucide-react';

// Navigation item with optional dropdown
export const BionicNavItem = ({
  label,
  to,
  icon: Icon,
  children,
  active,
  onClick,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasDropdown = React.Children.count(children) > 0;
  
  const baseClasses = cn(
    'flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider',
    'rounded-sm transition-all duration-200',
    'hover:bg-white/5 hover:text-white',
    active ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-400'
  );
  
  if (hasDropdown) {
    return (
      <div className="relative" onMouseLeave={() => setIsOpen(false)}>
        <button
          className={baseClasses}
          onMouseEnter={() => setIsOpen(true)}
          onClick={() => setIsOpen(!isOpen)}
        >
          {Icon && <Icon className="h-4 w-4" />}
          {label}
          <ChevronDown className={cn(
            'h-3 w-3 transition-transform',
            isOpen && 'rotate-180'
          )} />
        </button>
        
        {isOpen && (
          <div className={cn(
            'absolute top-full left-0 mt-1 min-w-[200px]',
            'bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl',
            'py-1 z-50'
          )}>
            {children}
          </div>
        )}
      </div>
    );
  }
  
  return (
    <Link to={to} className={baseClasses} onClick={onClick}>
      {Icon && <Icon className="h-4 w-4" />}
      {label}
    </Link>
  );
};

// Dropdown item
export const BionicNavDropdownItem = ({
  label,
  to,
  icon: Icon,
  description,
  onClick,
}) => {
  return (
    <Link
      to={to}
      className={cn(
        'flex items-start gap-3 px-4 py-2',
        'hover:bg-white/5 transition-colors',
        'group'
      )}
      onClick={onClick}
    >
      {Icon && (
        <Icon className="h-4 w-4 mt-0.5 text-gray-400 group-hover:text-[#F5A623]" />
      )}
      <div>
        <div className="text-sm font-medium text-white group-hover:text-[#F5A623]">
          {label}
        </div>
        {description && (
          <div className="text-xs text-gray-500 mt-0.5">
            {description}
          </div>
        )}
      </div>
    </Link>
  );
};

// Main navigation bar
export const BionicNavBar = ({
  logo,
  children,
  rightContent,
  className,
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  
  return (
    <nav className={cn(
      'bg-black/80 backdrop-blur-xl border-b border-white/10',
      'sticky top-0 z-50',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            {logo}
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {children}
          </div>
          
          {/* Right Content (language, user) */}
          <div className="hidden md:flex items-center gap-4">
            {rightContent}
          </div>
          
          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-400 hover:text-white"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {mobileOpen && (
        <div className="md:hidden border-t border-white/10 bg-black/95">
          <div className="px-4 py-4 space-y-2">
            {React.Children.map(children, (child) =>
              React.cloneElement(child, {
                onClick: () => setMobileOpen(false),
              })
            )}
          </div>
          <div className="px-4 py-4 border-t border-white/10">
            {rightContent}
          </div>
        </div>
      )}
    </nav>
  );
};

// Tab navigation for sections
export const BionicTabs = ({
  tabs,
  activeTab,
  onChange,
  className,
}) => {
  return (
    <div className={cn(
      'flex items-center gap-1 p-1',
      'bg-black/40 rounded-md border border-white/10',
      className
    )}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            'flex items-center gap-2 px-4 py-2 text-sm font-medium uppercase tracking-wider',
            'rounded-sm transition-all duration-200',
            activeTab === tab.id
              ? 'bg-[#F5A623] text-black'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          )}
        >
          {tab.icon && <tab.icon className="h-4 w-4" />}
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default {
  BionicNavBar,
  BionicNavItem,
  BionicNavDropdownItem,
  BionicTabs,
};
