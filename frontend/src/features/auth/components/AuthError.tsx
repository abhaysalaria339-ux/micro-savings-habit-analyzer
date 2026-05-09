import { ErrorMessage } from "../../../components/ErrorMessage";

type AuthErrorProps = {
  message: string | null;
};

export function AuthError({ message }: AuthErrorProps) {
  return <ErrorMessage message={message} title="Authentication failed" />;
}
