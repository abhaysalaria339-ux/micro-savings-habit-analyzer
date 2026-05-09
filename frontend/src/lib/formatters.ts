const inrCurrencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});

export function formatCurrency(amount: number | string): string {
  const numericAmount = Number(amount);

  return inrCurrencyFormatter.format(Number.isFinite(numericAmount) ? numericAmount : 0);
}
