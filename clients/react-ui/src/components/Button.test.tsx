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
    fireEvent.click(screen.getByRole("button", { name: "X" }));
    expect(onClick).not.toHaveBeenCalled();
  });
});
