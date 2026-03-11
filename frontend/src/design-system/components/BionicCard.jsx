/**
 * BionicCard - BIONIC TACTICAL Design System
 * HUD-style glassmorphism card component
 */

const cardVariants = {
  default: 'bg-black/60 backdrop-blur-xl border border-white/10 shadow-2xl',
  solid: 'bg-[#121212] border border-[#262626] shadow-lg',
  outlined: 'bg-black/40 backdrop-blur-md border-2 border-white/20',
  highlighted: 'bg-black/60 backdrop-blur-xl border border-[#F5A623]/30 shadow-[0_0_20px_rgba(245,166,35,0.1)]',
  interactive: 'bg-black/60 backdrop-blur-xl border border-white/10 shadow-2xl hover:border-[#F5A623]/30 hover:shadow-[0_0_20px_rgba(245,166,35,0.1)] transition-all duration-300 cursor-pointer',
};

export function BionicCard({ children, variant = 'default', className = '', noPadding = false, ...props }) {
  const classes = ['rounded-md', cardVariants[variant] || cardVariants.default];
  if (!noPadding) classes.push('p-4');
  if (className) classes.push(className);
  return (
    <div className={classes.join(' ')} {...props}>
      {children}
    </div>
  );
}

BionicCard.displayName = 'BionicCard';

export function BionicCardHeader({ children, className = '', ...props }) {
  return (
    <div className={`border-b border-white/10 pb-3 mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

BionicCardHeader.displayName = 'BionicCardHeader';

export function BionicCardTitle({ children, className = '', as: Tag = 'h3', ...props }) {
  return (
    <Tag className={`text-white font-semibold uppercase tracking-wide text-sm ${className}`} {...props}>
      {children}
    </Tag>
  );
}

BionicCardTitle.displayName = 'BionicCardTitle';

export function BionicCardContent({ children, className = '', ...props }) {
  return (
    <div className={`text-gray-300 ${className}`} {...props}>
      {children}
    </div>
  );
}

BionicCardContent.displayName = 'BionicCardContent';

export function BionicCardFooter({ children, className = '', ...props }) {
  return (
    <div className={`border-t border-white/10 pt-3 mt-4 flex items-center justify-end gap-2 ${className}`} {...props}>
      {children}
    </div>
  );
}

BionicCardFooter.displayName = 'BionicCardFooter';

export default BionicCard;
