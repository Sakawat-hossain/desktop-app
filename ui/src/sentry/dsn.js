// Diagnostic reports are sent only when a Sentry DSN of our own is set at
// build time (VITE_SENTRY_DSN); empty disables them.
export const DSN = import.meta.env.VITE_SENTRY_DSN || "";
