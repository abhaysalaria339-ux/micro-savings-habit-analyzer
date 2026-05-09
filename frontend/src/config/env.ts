const localApiBaseUrl = "http://127.0.0.1:8000/api/v1";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ??
  (["development", "test"].includes(import.meta.env.MODE)
    ? localApiBaseUrl
    : undefined);

if (!apiBaseUrl) {
  throw new Error("VITE_API_BASE_URL is required.");
}

export const env = {
  apiBaseUrl,
};
