export const expenseDataChangedEvent = "micro-savings:expense-data-changed";

export function notifyExpenseDataChanged(): void {
  window.dispatchEvent(new Event(expenseDataChangedEvent));
}

export function subscribeToExpenseDataChanged(callback: () => void): () => void {
  window.addEventListener(expenseDataChangedEvent, callback);

  return () => {
    window.removeEventListener(expenseDataChangedEvent, callback);
  };
}
