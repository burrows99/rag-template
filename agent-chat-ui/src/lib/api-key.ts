export function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("lg:chat:apiKey");
}

export function setApiKey(key: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("lg:chat:apiKey", key);
}

export function removeApiKey(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("lg:chat:apiKey");
}
