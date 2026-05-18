import { ChangeEvent, useState } from "react";

import { ErrorMessage } from "../../../components/ErrorMessage";
import { ApiError } from "../../../lib/api/apiError";
import { ExpenseImportResponse, importExpensesFromCsv } from "../api/expenseApi";

type ExpenseImportPanelProps = {
  onImported?: () => void;
};

export function ExpenseImportPanel({ onImported }: ExpenseImportPanelProps) {
  const [fileName, setFileName] = useState("");
  const [csvContent, setCsvContent] = useState("");
  const [result, setResult] = useState<ExpenseImportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    setResult(null);
    setError(null);

    if (!file) {
      setFileName("");
      setCsvContent("");
      return;
    }

    try {
      const text = await file.text();
      setFileName(file.name);
      setCsvContent(text);
    } catch {
      setError("Unable to read the selected CSV file.");
    }
  }

  async function handleImport() {
    if (!csvContent.trim()) {
      setError("Choose a CSV file before importing.");
      return;
    }

    setIsImporting(true);
    setError(null);
    setResult(null);

    try {
      const response = await importExpensesFromCsv(csvContent);
      setResult(response);
      if (response.imported_count > 0) {
        onImported?.();
      }
    } catch (caughtError) {
      setError(toImportErrorMessage(caughtError));
    } finally {
      setIsImporting(false);
    }
  }

  return (
    <section className="form-panel import-panel" aria-labelledby="expense-import-title">
      <div className="panel-heading">
        <div>
          <p>Bulk entry</p>
          <h2 id="expense-import-title">Import CSV</h2>
        </div>
      </div>

      <div className="csv-format-note">
        <strong>Required columns</strong>
        <span>amount, category, spent_at</span>
        <small>Optional: description</small>
      </div>

      <label className="file-picker">
        <span>{fileName || "Choose CSV file"}</span>
        <input accept=".csv,text/csv" onChange={handleFileChange} type="file" />
      </label>

      <ErrorMessage message={error} title="Import failed" />

      {result ? (
        <div className="import-result" role="status">
          <strong>{result.imported_count} imported</strong>
          <span>
            {result.failed_count} failed, {result.skipped_count} skipped
          </span>
          {result.failed_count > 0 ? (
            <ul>
              {result.results
                .filter((row) => row.status === "failed")
                .slice(0, 3)
                .map((row) => (
                  <li key={row.row_number}>
                    Row {row.row_number}: {row.error}
                  </li>
                ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      <button
        className="secondary-button"
        disabled={isImporting || !csvContent.trim()}
        onClick={() => void handleImport()}
        type="button"
      >
        {isImporting ? "Importing..." : "Import expenses"}
      </button>
    </section>
  );
}

function toImportErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Unable to import expenses. Check the CSV format and try again.";
}
