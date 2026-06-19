import type { ReactNode } from "react";

export interface CardProps {
  title?: ReactNode;
  className?: string;
  children?: ReactNode;
}

export function Card({ title, className, children }: CardProps) {
  const cls = ["nv-card", className].filter(Boolean).join(" ");
  return (
    <div className={cls}>
      {title != null && <h4 className="nv-card__title">{title}</h4>}
      {children}
    </div>
  );
}
