import { useState } from "react";

import { ExpenseCreateForm } from "../features/expenses/components/ExpenseCreateForm";
import { ExpenseImportPanel } from "../features/expenses/components/ExpenseImportPanel";
import { ExpenseList } from "../features/expenses/components/ExpenseList";

export function ExpensesPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <section className="page-surface" aria-labelledby="expenses-title">
      <div className="page-heading">
        <div>
          <p>Tracking</p>
          <h1 id="expenses-title">Expenses</h1>
        </div>
      </div>

      <div className="expenses-layout">
        <div className="expense-entry-stack">
          <ExpenseCreateForm onCreated={() => setRefreshKey((value) => value + 1)} />
          <ExpenseImportPanel onImported={() => setRefreshKey((value) => value + 1)} />
        </div>
        <ExpenseList refreshKey={refreshKey} />
      </div>
    </section>
  );
}
