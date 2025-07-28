declare module 'lucide-react' {
  import { ComponentType, SVGProps } from 'react';
  
  export interface LucideIcon extends ComponentType<SVGProps<SVGSVGElement>> {
    displayName?: string;
  }
  
  export const Camera: LucideIcon;
  export const Upload: LucideIcon;
  export const Loader2: LucideIcon;
  export const CheckCircle: LucideIcon;
  export const AlertCircle: LucideIcon;
  export const Sparkles: LucideIcon;
  export const RotateCcw: LucideIcon;
  export const X: LucideIcon;
  export const ArrowLeft: LucideIcon;
  export const User: LucideIcon;
  export const Database: LucideIcon;
  export const Brain: LucideIcon;
  export const Zap: LucideIcon;
} 