import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

// Looping, ambient preview of what an interview exchange looks like —
// grounds the auth screen in the actual product rather than a generic hero.
const previewExchange = [
  { role: "ai", text: "Walk me through how you'd design a rate limiter for a public API." },
  { role: "user", text: "I'd start with a token bucket per client, backed by Redis for shared state..." },
  { role: "ai", text: "Good. How does that hold up under a thundering-herd scenario?" },
];

function PreviewPanel() {
  return (
    <div className="relative hidden h-full flex-col justify-center overflow-hidden border-l border-border-subtle bg-surface px-14 lg:flex">
      {/* ambient glow, restrained */}
      <div
        className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full opacity-20 blur-3xl"
        style={{ background: "radial-gradient(circle, var(--color-accent) 0%, transparent 70%)" }}
      />

      <p className="mb-8 font-mono text-xs uppercase tracking-widest text-text-muted">
        Live session preview
      </p>

      <div className="flex flex-col gap-4">
        {previewExchange.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 + i * 0.35, ease: "easeOut" }}
            className={`max-w-md rounded-lg border px-4 py-3 text-sm leading-relaxed ${
              msg.role === "ai"
                ? "self-start border-border bg-surface-raised text-text-primary"
                : "self-end border-accent-muted bg-accent-soft text-text-primary"
            }`}
          >
            {msg.text}
          </motion.div>
        ))}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.4 }}
          className="mt-1 flex items-center gap-1.5 self-start pl-1"
        >
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted" />
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted [animation-delay:150ms]" />
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-text-muted [animation-delay:300ms]" />
        </motion.div>
      </div>
    </div>
  );
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="grid min-h-screen bg-bg lg:grid-cols-2">
      <div className="flex flex-col justify-center px-6 py-12 sm:px-12 lg:px-20">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-accent" />
            <span className="font-mono text-sm tracking-wide text-text-secondary">interviai</span>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          >
            <h1 className="text-2xl font-semibold text-text-primary">{title}</h1>
            <p className="mt-1.5 text-sm text-text-secondary">{subtitle}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
            className="mt-8"
          >
            {children}
          </motion.div>
        </div>
      </div>

      <PreviewPanel />
    </div>
  );
}
