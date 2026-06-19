import type { CSSProperties, ReactNode } from "react";

export interface ToggleOption {
  value: string;
  label: ReactNode;
}

export interface ToggleProps {
  options: ToggleOption[];
  value: string;
  onChange: (value: string) => void;
}

export function Toggle({ options, value, onChange }: ToggleProps) {
  const idx = Math.max(0, options.findIndex((o) => o.value === value));
  const sliderStyle: CSSProperties = {
    width: `calc((100% - 6px) / ${options.length})`,
    transform: `translateX(${idx * 100}%)`,
  };
  return (
    <div className="nv-toggle" role="tablist">
      <span className="nv-toggle__slider" style={sliderStyle} />
      {options.map((o) => (
        <button
          key={o.value}
          role="tab"
          type="button"
          aria-selected={o.value === value}
          className={"nv-toggle__opt" + (o.value === value ? " is-active" : "")}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
