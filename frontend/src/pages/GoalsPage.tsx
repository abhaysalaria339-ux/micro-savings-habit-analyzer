import { useState } from "react";

import { GoalCreateForm } from "../features/goals/components/GoalCreateForm";
import { GoalList } from "../features/goals/components/GoalList";
import { GoalSuggestions } from "../features/goals/components/GoalSuggestions";

export function GoalsPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <section className="page-surface" aria-labelledby="goals-title">
      <div className="page-heading">
        <div>
          <p>Progress</p>
          <h1 id="goals-title">Goals</h1>
        </div>
      </div>

      <div className="goals-layout">
        <div className="goal-entry-stack">
          <GoalCreateForm onCreated={() => setRefreshKey((value) => value + 1)} />
          <GoalSuggestions refreshKey={refreshKey} />
        </div>
        <GoalList refreshKey={refreshKey} />
      </div>
    </section>
  );
}
