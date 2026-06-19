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
