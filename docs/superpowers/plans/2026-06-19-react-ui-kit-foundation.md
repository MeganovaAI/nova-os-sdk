# @libraos/react-ui Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `@libraos/react-ui` slice 1 — the package, the `--nv-*` theme/token layer (Atelier as default, themeable), and five primitives (Button, IconButton, Card, Composer, Toggle).

**Architecture:** A React component library in `libraos-sdk/clients/react-ui`, sibling to the framework-agnostic `clients/typescript`. Built with tsup (ESM/CJS/types). Styling ships as ONE stylesheet (`dist/styles.css`) of `--nv-*` CSS-variable tokens (scoped under a `.nv` root class) + prefixed `.nv-*` component classes; consumers import the CSS once and rebrand by overriding variables. Icon-agnostic; no product logic.

**Tech Stack:** React 19 (peer), TypeScript (strict), tsup, Vitest + @testing-library/react + jsdom, plain CSS.

## Global Constraints

- Package name `@libraos/react-ui`, version `0.1.0-alpha.0`, `"type": "module"`.
- Class namespace **`.nv-*`**; token namespace **`--nv-*`** — both prefixed to avoid host-app collisions. Tokens live on a **`.nv` root class** (not bare `:root`).
- Peer deps only `react` / `react-dom` `^19` (no other runtime deps). Icon-agnostic — components take icon elements via props/children.
- All component CSS lives in the single `src/styles.css` (theme tokens + every component); the build copies it verbatim to `dist/styles.css`.
- Tests verify behavior (not snapshots); use plain DOM assertions (no jest-dom matchers). TS strict.
- Run all commands from `clients/react-ui` unless noted. Branch: `feat/react-ui-kit`. Commit after every task.

## File structure

- `clients/react-ui/package.json`, `tsup.config.ts`, `tsconfig.json`, `vitest.config.ts`, `README.md`, `scripts/copy-styles.mjs`
- `clients/react-ui/src/index.ts` — re-exports every component + prop type
- `clients/react-ui/src/styles.css` — theme tokens + scope accents + all component classes
- `clients/react-ui/src/components/{Button,IconButton,Card,Composer,Toggle}.tsx`
- `clients/react-ui/src/components/{Button,IconButton,Card,Composer,Toggle}.test.tsx`
- `examples/react-ui-demo/` — Vite app proving consume + theme override

---

### Task 1: Package scaffold + theme layer

**Files:**
- Create: `clients/react-ui/package.json`, `tsup.config.ts`, `tsconfig.json`, `vitest.config.ts`, `scripts/copy-styles.mjs`, `src/index.ts`, `src/styles.css`

**Interfaces:**
- Produces: an installable, buildable package whose `dist/styles.css` carries the `--nv-*` tokens under `.nv`. Later tasks add components to `src/index.ts` and append CSS to `src/styles.css`.

- [ ] **Step 1: package.json**

```json
{
  "name": "@libraos/react-ui",
  "version": "0.1.0-alpha.0",
  "description": "React UI kit for LibraOS — the Atelier design system + primitives.",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist"],
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js", "require": "./dist/index.cjs" },
    "./styles.css": "./dist/styles.css"
  },
  "scripts": {
    "build": "tsup && node scripts/copy-styles.mjs",
    "test": "vitest run",
    "typecheck": "tsc --noEmit"
  },
  "peerDependencies": { "react": "^19", "react-dom": "^19" },
  "devDependencies": {
    "@testing-library/react": "^16.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "jsdom": "^25.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tsup": "^8.5.1",
    "typescript": "^5.6.0",
    "vitest": "^3.0.0"
  }
}
```

- [ ] **Step 2: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noEmit": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: tsup.config.ts**

```ts
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  external: ["react", "react-dom", "react/jsx-runtime"],
});
```

- [ ] **Step 4: vitest.config.ts**

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { environment: "jsdom", include: ["src/**/*.test.tsx"] },
});
```

- [ ] **Step 5: scripts/copy-styles.mjs**

```js
import { copyFileSync } from "node:fs";
copyFileSync("src/styles.css", "dist/styles.css");
```

- [ ] **Step 6: src/styles.css** (theme tokens + scope accents; component blocks appended by later tasks)

```css
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Spline+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap");

/* ── LibraOS UI — Atelier theme tokens (override any --nv-* to rebrand) ── */
.nv {
  --nv-paper: #f3efe6;
  --nv-surface: #fcfaf5;
  --nv-surface-2: #efe9dd;
  --nv-ink: #211e18;
  --nv-ink-soft: #514b40;
  --nv-muted: #8a8273;
  --nv-line: rgba(33, 30, 24, 0.09);
  --nv-line-strong: rgba(33, 30, 24, 0.15);
  --nv-accent: #0d5a52;
  --nv-accent-ink: #08423c;
  --nv-accent-tint: rgba(13, 90, 82, 0.09);
  --nv-accent-glow: rgba(13, 90, 82, 0.22);
  --nv-sh-1: 0 1px 1px rgba(33, 30, 24, 0.04), 0 1px 3px rgba(33, 30, 24, 0.05);
  --nv-sh-2: 0 2px 4px rgba(33, 30, 24, 0.04), 0 6px 18px -6px rgba(33, 30, 24, 0.1);
  --nv-sh-pop: 0 14px 40px -16px var(--nv-accent-glow), 0 2px 6px -2px rgba(33, 30, 24, 0.12);
  --nv-r-sm: 10px;
  --nv-r: 14px;
  --nv-r-lg: 20px;
  --nv-ease: cubic-bezier(0.22, 1, 0.36, 1);
  --nv-ease-snap: cubic-bezier(0.4, 0, 0.2, 1);
  --nv-t-fast: 0.15s;
  --nv-font-ui: "Spline Sans", ui-sans-serif, system-ui, sans-serif;
  --nv-font-display: "Fraunces", Georgia, serif;
  --nv-font-prose: "Newsreader", Georgia, serif;
  color: var(--nv-ink);
  font-family: var(--nv-font-ui);
}
/* Personal scope = warm amber accent; corporate (teal) is the default above. */
.nv[data-nv-scope="personal"], .nv [data-nv-scope="personal"] {
  --nv-accent: #b15c19;
  --nv-accent-ink: #7c3d0d;
  --nv-accent-tint: rgba(177, 92, 25, 0.1);
  --nv-accent-glow: rgba(177, 92, 25, 0.22);
}
```

- [ ] **Step 7: src/index.ts** (empty re-export barrel; components added later)

```ts
// @libraos/react-ui — component barrel. Primitives are added per task.
export {};
```

- [ ] **Step 8: install, build, verify**

Run: `npm install`
Then: `npm run build`
Expected: completes; `dist/index.js`, `dist/index.cjs`, `dist/index.d.ts`, and `dist/styles.css` exist. Confirm the CSS copied: `grep -c "\-\-nv-accent" dist/styles.css` → at least `2`.
Run: `npm run typecheck` → no errors.

- [ ] **Step 9: Commit**

```bash
git add clients/react-ui
git commit -m "feat(react-ui): package scaffold + Atelier theme tokens"
```

### Task 2: Button

**Files:**
- Create: `clients/react-ui/src/components/Button.tsx`, `clients/react-ui/src/components/Button.test.tsx`
- Modify: `clients/react-ui/src/index.ts`, `clients/react-ui/src/styles.css`

**Interfaces:**
- Produces: `Button` + `ButtonProps { variant?: "primary"|"ghost"|"subtle"; size?: "sm"|"md"; leftIcon?: ReactNode } & ButtonHTMLAttributes<HTMLButtonElement>`.

- [ ] **Step 1: Write the failing test** — `src/components/Button.test.tsx`

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./Button";

describe("Button", () => {
  it("fires onClick and reflects its variant class", () => {
    const onClick = vi.fn();
    render(<Button variant="ghost" onClick={onClick}>Go</Button>);
    const btn = screen.getByRole("button", { name: "Go" });
    expect(btn.className).toContain("nv-btn--ghost");
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire onClick when disabled", () => {
    const onClick = vi.fn();
    render(<Button disabled onClick={onClick}>X</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run it (fails — module missing)**

Run: `npm test -- src/components/Button.test.tsx`
Expected: FAIL — cannot find `./Button`.

- [ ] **Step 3: Implement** — `src/components/Button.tsx`

```tsx
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
```

- [ ] **Step 4: Export from `src/index.ts`** — replace `export {};` (and keep appending for later tasks)

```ts
export { Button } from "./components/Button";
export type { ButtonProps } from "./components/Button";
```

- [ ] **Step 5: Append CSS to `src/styles.css`**

```css
/* ── Button ─────────────────────────────────────────────────────────── */
.nv-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  font-family: var(--nv-font-ui); font-weight: 600; cursor: pointer;
  border: 1px solid transparent; border-radius: var(--nv-r-sm);
  transition: color var(--nv-t-fast) var(--nv-ease-snap), background var(--nv-t-fast) var(--nv-ease-snap),
    border-color var(--nv-t-fast) var(--nv-ease-snap), transform var(--nv-t-fast) var(--nv-ease-snap),
    filter var(--nv-t-fast) var(--nv-ease-snap);
}
.nv-btn:active:not(:disabled) { transform: scale(0.97); }
.nv-btn:disabled { opacity: 0.45; cursor: not-allowed; box-shadow: none; }
.nv-btn__icon { display: inline-flex; }
.nv-btn--sm { padding: 7px 12px; font-size: 12.5px; }
.nv-btn--md { padding: 10px 16px; font-size: 13.5px; }
.nv-btn--primary { color: var(--nv-surface); background: linear-gradient(150deg, var(--nv-accent), var(--nv-accent-ink)); box-shadow: var(--nv-sh-pop); }
.nv-btn--primary:hover:not(:disabled) { filter: brightness(1.07); }
.nv-btn--ghost { color: var(--nv-ink-soft); background: var(--nv-surface); border-color: var(--nv-line); box-shadow: var(--nv-sh-1); }
.nv-btn--ghost:hover:not(:disabled) { color: var(--nv-ink); border-color: var(--nv-line-strong); }
.nv-btn--subtle { color: var(--nv-muted); background: transparent; }
.nv-btn--subtle:hover:not(:disabled) { color: var(--nv-ink); background: var(--nv-surface-2); }
```

- [ ] **Step 6: Run tests + typecheck**

Run: `npm test -- src/components/Button.test.tsx` → PASS (2 tests).
Run: `npm run typecheck` → no errors.

- [ ] **Step 7: Commit**

```bash
git add clients/react-ui/src
git commit -m "feat(react-ui): Button primitive"
```

### Task 3: IconButton

**Files:**
- Create: `src/components/IconButton.tsx`, `src/components/IconButton.test.tsx`
- Modify: `src/index.ts`, `src/styles.css`

**Interfaces:**
- Produces: `IconButton` + `IconButtonProps { "aria-label": string; size?: "sm"|"md" } & ButtonHTMLAttributes<HTMLButtonElement>` (children = icon element).

- [ ] **Step 1: Write the failing test** — `src/components/IconButton.test.tsx`

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { IconButton } from "./IconButton";

describe("IconButton", () => {
  it("exposes its aria-label and fires onClick", () => {
    const onClick = vi.fn();
    render(<IconButton aria-label="Send" onClick={onClick}><svg /></IconButton>);
    const btn = screen.getByRole("button", { name: "Send" });
    expect(btn.className).toContain("nv-icon-btn");
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

- [ ] **Step 2: Run it (fails)** — `npm test -- src/components/IconButton.test.tsx` → FAIL (module missing).

- [ ] **Step 3: Implement** — `src/components/IconButton.tsx`

```tsx
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
```

- [ ] **Step 4: Export from `src/index.ts`** (append)

```ts
export { IconButton } from "./components/IconButton";
export type { IconButtonProps } from "./components/IconButton";
```

- [ ] **Step 5: Append CSS to `src/styles.css`**

```css
/* ── IconButton ─────────────────────────────────────────────────────── */
.nv-icon-btn {
  display: grid; place-items: center; border-radius: var(--nv-r-sm);
  border: 1px solid transparent; background: transparent; color: var(--nv-muted); cursor: pointer;
  transition: color var(--nv-t-fast) var(--nv-ease-snap), background var(--nv-t-fast) var(--nv-ease-snap),
    border-color var(--nv-t-fast) var(--nv-ease-snap), transform var(--nv-t-fast) var(--nv-ease-snap);
}
.nv-icon-btn:hover:not(:disabled) { color: var(--nv-ink); background: var(--nv-surface-2); border-color: var(--nv-line); }
.nv-icon-btn:active:not(:disabled) { transform: scale(0.92); }
.nv-icon-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.nv-icon-btn--sm { width: 30px; height: 30px; }
.nv-icon-btn--md { width: 36px; height: 36px; }
```

- [ ] **Step 6: Run tests + typecheck** — `npm test -- src/components/IconButton.test.tsx` → PASS; `npm run typecheck` → clean.

- [ ] **Step 7: Commit**

```bash
git add clients/react-ui/src
git commit -m "feat(react-ui): IconButton primitive"
```

### Task 4: Card

**Files:**
- Create: `src/components/Card.tsx`, `src/components/Card.test.tsx`
- Modify: `src/index.ts`, `src/styles.css`

**Interfaces:**
- Produces: `Card` + `CardProps { title?: ReactNode; className?: string; children?: ReactNode }`.

- [ ] **Step 1: Write the failing test** — `src/components/Card.test.tsx`

```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card } from "./Card";

describe("Card", () => {
  it("renders the title and children", () => {
    render(<Card title="Sources"><div>body</div></Card>);
    expect(screen.getByText("Sources").className).toContain("nv-card__title");
    expect(screen.getByText("body")).toBeTruthy();
  });

  it("omits the title node when no title is given", () => {
    const { container } = render(<Card><div>only body</div></Card>);
    expect(container.querySelector(".nv-card__title")).toBeNull();
  });
});
```

- [ ] **Step 2: Run it (fails)** — `npm test -- src/components/Card.test.tsx` → FAIL.

- [ ] **Step 3: Implement** — `src/components/Card.tsx`

```tsx
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
```

- [ ] **Step 4: Export from `src/index.ts`** (append)

```ts
export { Card } from "./components/Card";
export type { CardProps } from "./components/Card";
```

- [ ] **Step 5: Append CSS to `src/styles.css`**

```css
/* ── Card ───────────────────────────────────────────────────────────── */
.nv-card { background: var(--nv-surface); border: 1px solid var(--nv-line); border-radius: var(--nv-r-lg); padding: 20px; box-shadow: var(--nv-sh-1); }
.nv-card__title { margin: 0 0 14px; font-size: 10.5px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--nv-muted); display: flex; align-items: center; gap: 7px; }
```

- [ ] **Step 6: Run tests + typecheck** — `npm test -- src/components/Card.test.tsx` → PASS; `npm run typecheck` → clean.

- [ ] **Step 7: Commit**

```bash
git add clients/react-ui/src
git commit -m "feat(react-ui): Card primitive"
```

### Task 5: Toggle

**Files:**
- Create: `src/components/Toggle.tsx`, `src/components/Toggle.test.tsx`
- Modify: `src/index.ts`, `src/styles.css`

**Interfaces:**
- Produces: `Toggle` + `ToggleOption { value: string; label: ReactNode }` + `ToggleProps { options: ToggleOption[]; value: string; onChange: (v: string) => void }`.

- [ ] **Step 1: Write the failing test** — `src/components/Toggle.test.tsx`

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Toggle } from "./Toggle";

const opts = [
  { value: "corporate", label: "Corporate" },
  { value: "personal", label: "Personal" },
];

describe("Toggle", () => {
  it("marks the active option and calls onChange with the clicked value", () => {
    const onChange = vi.fn();
    render(<Toggle options={opts} value="corporate" onChange={onChange} />);
    const corporate = screen.getByRole("tab", { name: "Corporate" });
    const personal = screen.getByRole("tab", { name: "Personal" });
    expect(corporate.getAttribute("aria-selected")).toBe("true");
    expect(personal.getAttribute("aria-selected")).toBe("false");
    fireEvent.click(personal);
    expect(onChange).toHaveBeenCalledWith("personal");
  });
});
```

- [ ] **Step 2: Run it (fails)** — `npm test -- src/components/Toggle.test.tsx` → FAIL.

- [ ] **Step 3: Implement** — `src/components/Toggle.tsx`

```tsx
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
```

- [ ] **Step 4: Export from `src/index.ts`** (append)

```ts
export { Toggle } from "./components/Toggle";
export type { ToggleProps, ToggleOption } from "./components/Toggle";
```

- [ ] **Step 5: Append CSS to `src/styles.css`**

```css
/* ── Toggle (segmented sliding control) ─────────────────────────────── */
.nv-toggle { position: relative; display: inline-flex; padding: 3px; border-radius: 999px; background: var(--nv-surface-2); border: 1px solid var(--nv-line); box-shadow: inset 0 1px 2px rgba(33, 30, 24, 0.04); }
.nv-toggle__opt { position: relative; z-index: 1; display: inline-flex; align-items: center; justify-content: center; gap: 7px; flex: 1; padding: 8px 15px; border: 0; background: transparent; cursor: pointer; font-family: var(--nv-font-ui); font-size: 12.5px; font-weight: 600; color: var(--nv-muted); border-radius: 999px; white-space: nowrap; transition: color 0.28s var(--nv-ease); }
.nv-toggle__opt.is-active { color: var(--nv-surface); }
.nv-toggle__slider { position: absolute; top: 3px; bottom: 3px; left: 3px; border-radius: 999px; background: linear-gradient(150deg, var(--nv-accent), var(--nv-accent-ink)); box-shadow: var(--nv-sh-pop); transition: transform 0.4s var(--nv-ease), background 0.45s var(--nv-ease); }
```

- [ ] **Step 6: Run tests + typecheck** — `npm test -- src/components/Toggle.test.tsx` → PASS; `npm run typecheck` → clean.

- [ ] **Step 7: Commit**

```bash
git add clients/react-ui/src
git commit -m "feat(react-ui): Toggle primitive"
```

### Task 6: Composer

**Files:**
- Create: `src/components/Composer.tsx`, `src/components/Composer.test.tsx`
- Modify: `src/index.ts`, `src/styles.css`

**Interfaces:**
- Produces: `Composer` + `ComposerProps { value: string; onChange: (v: string) => void; onSubmit: () => void; placeholder?: string; actions?: ReactNode; disabled?: boolean }`.

- [ ] **Step 1: Write the failing test** — `src/components/Composer.test.tsx`

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Composer } from "./Composer";

describe("Composer", () => {
  it("calls onChange on input", () => {
    const onChange = vi.fn();
    render(<Composer value="" onChange={onChange} onSubmit={() => {}} placeholder="Ask…" />);
    fireEvent.change(screen.getByPlaceholderText("Ask…"), { target: { value: "hi" } });
    expect(onChange).toHaveBeenCalledWith("hi");
  });

  it("submits on Enter but inserts a newline on Shift+Enter", () => {
    const onSubmit = vi.fn();
    render(<Composer value="hi" onChange={() => {}} onSubmit={onSubmit} placeholder="Ask…" />);
    const ta = screen.getByPlaceholderText("Ask…");
    fireEvent.keyDown(ta, { key: "Enter", shiftKey: true });
    expect(onSubmit).not.toHaveBeenCalled();
    fireEvent.keyDown(ta, { key: "Enter" });
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("renders the actions slot", () => {
    render(<Composer value="" onChange={() => {}} onSubmit={() => {}} actions={<button>send</button>} />);
    expect(screen.getByRole("button", { name: "send" })).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run it (fails)** — `npm test -- src/components/Composer.test.tsx` → FAIL.

- [ ] **Step 3: Implement** — `src/components/Composer.tsx`

```tsx
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
```

- [ ] **Step 4: Export from `src/index.ts`** (append)

```ts
export { Composer } from "./components/Composer";
export type { ComposerProps } from "./components/Composer";
```

- [ ] **Step 5: Append CSS to `src/styles.css`**

```css
/* ── Composer (floating pill input) ─────────────────────────────────── */
.nv-composer {
  display: flex; align-items: flex-end; gap: 11px; padding: 10px 10px 10px 22px; border-radius: 28px;
  background: var(--nv-surface); border: 1px solid var(--nv-line-strong);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55), 0 1px 2px rgba(33, 30, 24, 0.04), 0 22px 48px -24px rgba(33, 30, 24, 0.32);
  transition: border-color var(--nv-t-fast) var(--nv-ease-snap), box-shadow 0.3s var(--nv-ease), transform 0.3s var(--nv-ease);
}
.nv-composer:focus-within { border-color: color-mix(in srgb, var(--nv-accent) 46%, var(--nv-line)); box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55), 0 22px 52px -22px var(--nv-accent-glow), 0 0 0 4px var(--nv-accent-tint); transform: translateY(-1px); }
.nv-composer__input { flex: 1; border: 0; outline: 0; resize: none; background: transparent; font-family: var(--nv-font-ui); font-size: 15.5px; line-height: 1.55; color: var(--nv-ink); max-height: 180px; padding: 11px 0; }
.nv-composer__input::placeholder { color: var(--nv-muted); }
.nv-composer__actions { display: inline-flex; align-items: center; gap: 8px; }
```

- [ ] **Step 6: Run full suite + typecheck + build**

Run: `npm test` → all component tests pass.
Run: `npm run typecheck` → clean.
Run: `npm run build` → emits `dist/index.js/.cjs/.d.ts` + `dist/styles.css`; confirm `grep -c "nv-composer" dist/styles.css` ≥ 1 and `dist/index.d.ts` exports all five components.

- [ ] **Step 7: Commit**

```bash
git add clients/react-ui/src
git commit -m "feat(react-ui): Composer floating-pill primitive"
```

### Task 7: Demo app (consume + theme override)

**Files:**
- Create: `examples/react-ui-demo/package.json`, `vite.config.ts`, `index.html`, `src/main.tsx`, `tsconfig.json`

**Interfaces:**
- Consumes: every exported primitive + `@libraos/react-ui/styles.css`.

- [ ] **Step 1: package.json** — `examples/react-ui-demo/package.json`

```json
{
  "name": "react-ui-demo",
  "private": true,
  "type": "module",
  "scripts": { "dev": "vite", "build": "tsc -b && vite build" },
  "dependencies": {
    "@libraos/react-ui": "file:../../clients/react-ui",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.6.0",
    "vite": "^7.0.0"
  }
}
```

- [ ] **Step 2: vite.config.ts + tsconfig.json + index.html**

`vite.config.ts`:
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()] });
```

`tsconfig.json`:
```json
{
  "compilerOptions": { "target": "ES2022", "lib": ["DOM", "DOM.Iterable", "ES2022"], "module": "ESNext", "moduleResolution": "Bundler", "jsx": "react-jsx", "strict": true, "skipLibCheck": true, "noEmit": true },
  "include": ["src"]
}
```

`index.html`:
```html
<!doctype html>
<html lang="en">
  <head><meta charset="UTF-8" /><title>nova-os-ui demo</title></head>
  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
```

- [ ] **Step 3: src/main.tsx** — render all primitives + a theme override

```tsx
import { useState, type CSSProperties } from "react";
import { createRoot } from "react-dom/client";
import { Button, IconButton, Card, Composer, Toggle } from "@libraos/react-ui";
import "@libraos/react-ui/styles.css";

function Demo() {
  const [scope, setScope] = useState("corporate");
  const [text, setText] = useState("");
  return (
    <div className="nv" data-nv-scope={scope} style={{ minHeight: "100vh", background: "var(--nv-paper)", padding: 40, display: "flex", flexDirection: "column", gap: 20, maxWidth: 720, margin: "0 auto" }}>
      <Toggle
        options={[{ value: "corporate", label: "Corporate" }, { value: "personal", label: "Personal" }]}
        value={scope}
        onChange={setScope}
      />
      <div style={{ display: "flex", gap: 10 }}>
        <Button variant="primary">Primary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="subtle">Subtle</Button>
        <IconButton aria-label="icon">★</IconButton>
      </div>
      <Card title="Sources">Cited knowledge appears here.</Card>
      <Composer
        value={text}
        onChange={setText}
        onSubmit={() => setText("")}
        placeholder="Ask for a brief, draft, or summary…"
        actions={<IconButton aria-label="Send">↑</IconButton>}
      />
      {/* Rebrand proof: a violet accent override scoped to one subtree */}
      <div className="nv" style={{ "--nv-accent": "#5b4bdb", "--nv-accent-ink": "#3f33a8" } as CSSProperties}>
        <Button variant="primary">Rebranded accent</Button>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<Demo />);
```

- [ ] **Step 4: Install + build the demo**

Run (from `examples/react-ui-demo`): `npm install` then `npm run build`.
Expected: the demo type-checks and builds against the published `dist` of `@libraos/react-ui` (run `npm run build` in `clients/react-ui` first so `dist` exists). Confirms the consume path: import components + `styles.css`, `.nv` theme, `data-nv-scope`, and a `--nv-accent` override all resolve.

- [ ] **Step 5: Commit**

```bash
git add examples/react-ui-demo
git commit -m "feat(react-ui): demo app proving consume + theme override"
```

## Verification (whole plan)

- `clients/react-ui`: `npm run build` emits ESM/CJS/`.d.ts` + `dist/styles.css`; `npm run typecheck` clean; `npm test` green (Button/IconButton/Card/Toggle/Composer behavior).
- `examples/react-ui-demo` builds against the package, rendering all five primitives with the `.nv` theme, the `data-nv-scope` switch, and a `--nv-accent` override.

## Out of scope (later slices)

- Chat/AG-UI components (`useNovaChat`, `ChatThread`), the Tiptap canvas + export, the persona/model picker, the Sources panel, a docs/Storybook site, public publishing.
