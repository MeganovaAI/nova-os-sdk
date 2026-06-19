import { useState, type CSSProperties } from "react";
import { createRoot } from "react-dom/client";
import { Button, IconButton, Card, Composer, Toggle } from "@meganova/nova-os-ui";
import "@meganova/nova-os-ui/styles.css";

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
