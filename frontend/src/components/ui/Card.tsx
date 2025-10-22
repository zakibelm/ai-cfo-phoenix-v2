import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glass?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = false,
  glass = false,
  onClick,
}) => {
  const baseClasses = 'rounded-lg transition-all duration-200';
  
  const variantClasses = glass
    ? 'glass shadow-lg'
    : 'bg-card-bg border border-border-color shadow-sm';
  
  const hoverClasses = hover
    ? 'hover:shadow-lg hover:border-primary-accent/30 hover:-translate-y-1 cursor-pointer'
    : '';
  
  const Component = onClick ? motion.div : 'div';
  
  const motionProps = onClick
    ? {
        whileHover: { scale: 1.02 },
        whileTap: { scale: 0.98 },
      }
    : {};
  
  return (
    <Component
      className={clsx(baseClasses, variantClasses, hoverClasses, className)}
      onClick={onClick}
      {...motionProps}
    >
      {children}
    </Component>
  );
};

export default Card;

