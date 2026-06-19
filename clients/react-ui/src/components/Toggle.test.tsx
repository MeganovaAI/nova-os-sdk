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
