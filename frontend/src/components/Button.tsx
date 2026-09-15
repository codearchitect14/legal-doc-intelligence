import { type ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const variantClasses: Record<Variant, string> = {
  primary: "bg-brand-600 text-white hover:bg-brand-700 focus-visible:outline-brand-600",
  secondary:
    "bg-white text-slate-900 border border-slate-300 hover:bg-slate-50 focus-visible:outline-slate-400",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100 focus-visible:outline-slate-400",
  danger: "bg-danger-500 text-white hover:bg-danger-700 focus-visible:outline-danger-500",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", className = "", ...props }, ref) => (
    <button
      ref={ref}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:pointer-events-none ${variantClasses[variant]} ${className}`}
      {...props}
    />
  ),
);
Button.displayName = "Button";
