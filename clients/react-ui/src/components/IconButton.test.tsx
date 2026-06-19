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
