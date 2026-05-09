import { useState } from "react";

import { ExpenseCreateForm } from "../features/expenses/components/ExpenseCreateForm";
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
        <ExpenseCreateForm onCreated={() => setRefreshKey((value) => value + 1)} />
        <ExpenseList refreshKey={refreshKey} />
      </div>
    </section>
  );
}
