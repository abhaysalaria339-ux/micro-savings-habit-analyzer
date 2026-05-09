import { describe, expect, it } from "vitest";

import { formatCurrency } from "./formatters";

describe("formatCurrency", () => {
  it("formats amounts as Indian rupees", () => {
    expect(formatCurrency("1234.5")).toBe("₹1,234.50");
  });
});
