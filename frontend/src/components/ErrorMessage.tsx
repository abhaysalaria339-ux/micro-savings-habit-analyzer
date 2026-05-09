type ErrorMessageProps = {
  actionLabel?: string;
  message: string | null;
  onAction?: () => void;
  title?: string;
};

export function ErrorMessage({
  actionLabel,
  message,
  onAction,
  title = "Something went wrong",
}: ErrorMessageProps) {
  if (!message) {
    return null;
  }

  return (
    <div className="error-message" role="alert">
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
      </div>
      {actionLabel && onAction ? (
        <button className="secondary-button" onClick={onAction} type="button">
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
