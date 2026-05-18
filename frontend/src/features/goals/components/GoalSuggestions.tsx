import { useEffect, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { StateMessage } from "../../../components/StateMessage";
import { ApiError } from "../../../lib/api/apiError";
import { formatCurrency } from "../../../lib/formatters";
import { getGoalSuggestions, GoalSuggestion } from "../api/goalApi";

type GoalSuggestionsProps = {
  refreshKey: number;
};

export function GoalSuggestions({ refreshKey }: GoalSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<GoalSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;

    async function loadSuggestions() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getGoalSuggestions();
        if (!ignore) {
          setSuggestions(response.suggestions);
        }
      } catch (caughtError) {
        if (!ignore) {
          setError(toGoalSuggestionErrorMessage(caughtError));
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadSuggestions();

    return () => {
      ignore = true;
    };
  }, [refreshKey]);

  return (
    <section className="dashboard-panel goal-suggestions-panel" aria-labelledby="goal-suggestions-title">
      <div className="panel-heading">
        <div>
          <p>Recommended</p>
          <h2 id="goal-suggestions-title">Goal suggestions</h2>
        </div>
      </div>

      <ErrorMessage message={error} title="Suggestions unavailable" />

      {isLoading ? (
        <StateMessage
          description="Finding goal ideas from current savings opportunities."
          title="Loading suggestions"
          variant="loading"
        />
      ) : null}

      {!isLoading && suggestions.length === 0 ? (
        <StateMessage
          description="Add more expenses to generate smart goal suggestions."
          title="No suggestions yet"
        />
      ) : null}

      <ul className="goal-suggestion-list">
        {suggestions.map((suggestion) => (
          <li key={`${suggestion.suggestion_type}-${suggestion.title}`}>
            <div>
              <span>{suggestion.confidence}</span>
              <strong>{suggestion.title}</strong>
              <p>{suggestion.message}</p>
            </div>
            <aside>{formatCurrency(suggestion.suggested_amount)}</aside>
          </li>
        ))}
      </ul>
    </section>
  );
}

function toGoalSuggestionErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to load goal suggestions. Check your connection and try again.";
}
