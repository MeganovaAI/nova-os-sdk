# @libraos/react-ui — Foundation (package + theme + primitives) design

**Date:** 2026-06-19 · **Status:** Approved design, pre-implementation ·
**Repo:** `libraos-sdk` · **Slice 1 of a multi-slice kit** (later: chat/AG-UI
layer, canvas, persona picker, docs site — each its own spec).

## Goal

A shared, themeable React UI kit so any Nova-OS-based product can install one
package, apply the theme, and get the polished "Atelier" look — instead of each
project re-building buttons/inputs/cards. This first slice ships the **package
itself**, the **theme/token layer**, and the **core primitives**.

## Why a kit (and what it is NOT)

Distilled from the `nova-os-employee-assistant` employee-ui, whose *product*
surfaces (department personas, dual-scope governance, approval queue, branding)
stay in that product. This kit is only the **reusable layer**: design tokens +
themeable primitives. Chat/AG-UI components, the canvas, and the persona picker
are later slices. Generic chat-only projects can still use LibreChat/Open WebUI;
this kit is for products that want the Atelier design language as components.

## Boundaries

- Lives in `libraos-sdk` (the shared SDK), a sibling of the existing
  framework-agnostic client `clients/typescript` (`@libraos/client`).
- **React-specific** (the client stays framework-agnostic; this kit is the React
  layer). No product logic, no LibraOS API calls in this slice.
- Private package (the SDK is private); no public publishing.
- Icon-agnostic — components accept icon elements as props/children; the kit does
  not depend on an icon library.

## Package

- Path: `clients/react-ui` · name `@libraos/react-ui` · `0.1.0-alpha.0`
  (matches the client's alpha line) · `"type": "module"`.
- Build with **tsup** (consistent with `clients/typescript`): emits
  `dist/index.js` (ESM), `dist/index.cjs` (CJS), `dist/index.d.ts`, and a
  bundled `dist/styles.css`.
- `package.json` exports:
  - `"."` → types + import (`dist/index.js`) + require (`dist/index.cjs`)
  - `"./styles.css"` → `dist/styles.css`
- Peer deps: `react` `^19`, `react-dom` `^19`. Dev deps: `tsup`, `typescript`,
  `vitest`, `@testing-library/react`, `jsdom`, `@types/react(-dom)`.

## Theme / token layer

- `src/theme.css` — the Atelier palette as **`--nv-*` CSS variables**, scoped
  under a **`.nv` root class** (so the kit never fights a host app's globals):
  - surfaces: `--nv-paper`, `--nv-surface`, `--nv-surface-2`
  - ink/text: `--nv-ink`, `--nv-ink-soft`, `--nv-muted`
  - lines: `--nv-line`, `--nv-line-strong`
  - accent: `--nv-accent`, `--nv-accent-ink`, `--nv-accent-tint`, `--nv-accent-glow`
  - shadows: `--nv-sh-1`, `--nv-sh-2`, `--nv-sh-pop`
  - radii: `--nv-r-sm`, `--nv-r`, `--nv-r-lg`
  - motion: `--nv-ease`, `--nv-ease-snap`, `--nv-t-fast`
  - fonts: `--nv-font-ui`, `--nv-font-display`, `--nv-font-prose`
- Scope accents (Corporate teal / Personal amber) under `[data-nv-scope="corporate"|"personal"]`.
- Ships the Fraunces / Spline Sans / Newsreader `@import` so it renders correctly
  out of the box; the `--nv-font-*` vars let a consumer swap fonts.
- **Theming contract:** wrap a subtree in `<div className="nv">` (or apply `.nv`
  to the app root) and override any `--nv-*` variable to rebrand. No JS theme
  provider in this slice — pure CSS variables.

## Primitives

Each component is one focused file under `src/components/`, applies prefixed
`.nv-*` classes, takes minimal props, and is fully themeable via the tokens.

- `Button` — `props: { variant?: "primary"|"ghost"|"subtle"; size?: "sm"|"md";
  leftIcon?: ReactNode; ...buttonHTMLAttributes }`. The snappy hover-fill +
  tactile `:active` press.
- `IconButton` — `props: { "aria-label": string; size?: "sm"|"md";
  ...buttonHTMLAttributes }`, children = the icon element. Square, hover-fill.
- `Card` — `props: { title?: ReactNode; children }`. The airier surface card
  (label heading + body), used for sidebars/panels.
- `Composer` — `props: { value: string; onChange: (v: string) => void;
  onSubmit: () => void; placeholder?: string; actions?: ReactNode;
  disabled?: boolean }`. The floating warm-paper pill input: auto-growing
  textarea, embedded `actions` slot (e.g. a send IconButton), Enter-to-submit
  (Shift+Enter newline), focus glow. Layout only — no network.
- `Toggle` — `props: { options: { value: string; label: ReactNode }[];
  value: string; onChange: (v: string) => void }`. The segmented sliding toggle
  (the scope-toggle), with the animated slider.

`src/index.ts` re-exports all components + their prop types.

## Build / styling pipeline

- All component CSS lives in a single `src/styles.css` (theme tokens first, then
  one block per primitive appended); the build copies it verbatim to
  `dist/styles.css` via `scripts/copy-styles.mjs` (single import for consumers).
  *(Implemented as one file rather than the per-file split originally sketched —
  it satisfies the binding constraint and avoids a CSS-bundling build step.)*
- Class namespace `.nv-*`; token namespace `--nv-*` — both prefixed to avoid
  collisions in a host app.

## Testing

- Vitest + `@testing-library/react` (jsdom): behavior, not snapshots —
  `Button` fires onClick and reflects `variant`; `IconButton` requires
  `aria-label`; `Toggle` calls `onChange` with the clicked value and marks the
  active option; `Composer` calls `onSubmit` on Enter and `onChange` on input,
  newline on Shift+Enter; a render smoke for `Card`.
- `examples/react-ui-demo` — a tiny Vite app that installs `@libraos/react-ui`
  (file: link), imports `@libraos/react-ui/styles.css`, renders every
  primitive, and overrides `--nv-accent` to prove the consume + rebrand path.

## File structure

- `clients/react-ui/package.json`, `tsup.config.ts`, `tsconfig.json`, `vitest.config.ts`, `README.md`
- `clients/react-ui/src/index.ts`
- `clients/react-ui/src/components/{Button,IconButton,Card,Composer,Toggle}.tsx`
- `clients/react-ui/src/styles.css` (theme tokens + all component blocks) + `clients/react-ui/scripts/copy-styles.mjs`
- `clients/react-ui/src/components/*.test.tsx`
- `examples/react-ui-demo/` (Vite app: index.html, src/main.tsx, package.json, vite.config.ts)

## Verification

- `tsup` build emits ESM/CJS/types + `dist/styles.css`; `tsc --noEmit` clean;
  Vitest suite green.
- The demo app builds and renders all primitives with a working `--nv-accent`
  override (the consume + theme path proven).

## Out of scope (later slices)

- Chat/AG-UI components (`useNovaChat`, `ChatThread`), the Tiptap canvas + export,
  the persona/model picker, the Sources panel.
- A JS theme provider / multiple packaged themes, a Storybook/docs site,
  public npm publishing.
