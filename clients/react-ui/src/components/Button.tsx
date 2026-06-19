import type { ButtonHTMLAttributes, ReactNode } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "subtle";
  size?: "sm" | "md";
  leftIcon?: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  leftIcon,
  className,
  children,
  ...rest
}: ButtonProps) {
  const cls = ["nv-btn", `nv-btn--${variant}`, `nv-btn--${size}`, className]
    .filter(Boolean)
    .join(" ");
  return (
    <button className={cls} {...rest}>
      {leftIcon && <span className="nv-btn__icon">{leftIcon}</span>}
      {children}
    </button>
  );
}
