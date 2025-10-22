import { useEffect, useRef, MutableRefObject } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const useGSAP = (
  animationFn: (ctx: gsap.Context) => void,
  dependencies: any[] = []
) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      animationFn(ctx);
    }, ref);

    return () => ctx.revert();
  }, dependencies);

  return ref;
};

// Predefined animation helpers
export const fadeIn = (element: string | Element, options = {}) => {
  return gsap.from(element, {
    opacity: 0,
    duration: 0.6,
    ease: 'power2.out',
    ...options,
  });
};

export const slideUp = (element: string | Element, options = {}) => {
  return gsap.from(element, {
    y: 50,
    opacity: 0,
    duration: 0.8,
    ease: 'power3.out',
    ...options,
  });
};

export const slideIn = (element: string | Element, direction: 'left' | 'right' = 'left', options = {}) => {
  const x = direction === 'left' ? -50 : 50;
  return gsap.from(element, {
    x,
    opacity: 0,
    duration: 0.8,
    ease: 'power3.out',
    ...options,
  });
};

export const scaleIn = (element: string | Element, options = {}) => {
  return gsap.from(element, {
    scale: 0.8,
    opacity: 0,
    duration: 0.6,
    ease: 'back.out(1.7)',
    ...options,
  });
};

export const staggerFadeIn = (elements: string, options = {}) => {
  return gsap.from(elements, {
    opacity: 0,
    y: 30,
    duration: 0.6,
    stagger: 0.1,
    ease: 'power2.out',
    ...options,
  });
};

export const parallax = (element: string | Element, options = {}) => {
  return gsap.to(element, {
    y: (i, target) => -ScrollTrigger.maxScroll(window) * target.dataset.speed,
    ease: 'none',
    scrollTrigger: {
      start: 0,
      end: 'max',
      invalidateOnRefresh: true,
      scrub: 0,
    },
    ...options,
  });
};

export const hoverScale = (element: Element, scale = 1.05) => {
  element.addEventListener('mouseenter', () => {
    gsap.to(element, { scale, duration: 0.3, ease: 'power2.out' });
  });
  
  element.addEventListener('mouseleave', () => {
    gsap.to(element, { scale: 1, duration: 0.3, ease: 'power2.out' });
  });
};

