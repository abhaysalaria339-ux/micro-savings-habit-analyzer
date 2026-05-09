type StateMessageProps = {
  description: string;
  title: string;
  variant?: "empty" | "loading";
};

export function StateMessage({
  description,
  title,
  variant = "empty",
}: StateMessageProps) {
  return (
    <div
      aria-live={variant === "loading" ? "polite" : undefined}
      className={`state-message ${variant}`}
      role={variant === "loading" ? "status" : undefined}
    >
      {variant === "loading" ? <span className="state-spinner" aria-hidden="true" /> : null}
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}
