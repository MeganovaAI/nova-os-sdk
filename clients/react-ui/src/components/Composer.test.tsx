import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { Composer } from "./Composer";

describe("Composer", () => {
  afterEach(() => cleanup());

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
