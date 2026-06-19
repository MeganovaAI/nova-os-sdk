import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

export interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  actions?: ReactNode;
  disabled?: boolean;
}

export function Composer({ value, onChange, onSubmit, placeholder, actions, disabled }: ComposerProps) {
  const ref = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    const ta = ref.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
  }, [value]);

  return (
    <div className="nv-composer">
      <textarea
        ref={ref}
        className="nv-composer__input"
        rows={1}
        placeholder={placeholder}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSubmit();
          }
        }}
      />
      {actions && <div className="nv-composer__actions">{actions}</div>}
    </div>
  );
}
