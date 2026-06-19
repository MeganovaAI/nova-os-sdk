import type { ButtonHTMLAttributes } from "react";

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
  size?: "sm" | "md";
}

export function IconButton({ size = "md", className, children, ...rest }: IconButtonProps) {
  const cls = ["nv-icon-btn", `nv-icon-btn--${size}`, className].filter(Boolean).join(" ");
  return (
    <button className={cls} {...rest}>
      {children}
    </button>
  );
}
