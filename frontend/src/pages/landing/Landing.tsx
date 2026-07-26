import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Sparkles,
  Target,
  BarChart3,
  FileText,
  Map as MapIcon,
  UploadCloud,
  MessageSquare,
  ClipboardCheck,
} from "lucide-react";

const features = [
  {
    icon: Target,
    title: "Adaptive questioning",
    description:
      "Every question depends on your last answer, your resume, and the role — never a fixed script.",
  },
  {
    icon: Sparkles,
    title: "Real evaluation",
    description: "Each answer is scored and reasoned about before the next question is chosen.",
  },
  {
    icon: FileText,
    title: "Resume-aware",
    description: "Questions are grounded in what you've actually built, not generic prompts.",
  },
  {
    icon: BarChart3,
    title: "Detailed reports",
    description: "Technical, communication, confidence, and problem-solving scores, broken down.",
  },
  {
    icon: MapIcon,
    title: "Learning roadmap",
    description: "Weak areas turn into a concrete plan, not just a number to feel bad about.",
  },
  {
    icon: ClipboardCheck,
    title: "Practice on your terms",
    description: "Pick the role and difficulty. Review every past session, anytime.",
  },
];

const steps = [
  {
    icon: UploadCloud,
    title: "Upload your resume",
    description: "One PDF. InterviAI parses your skills, projects, and experience.",
  },
  {
    icon: MessageSquare,
    title: "Take the interview",
    description: "Answer adaptive questions shaped by your background and the role you chose.",
  },
  {
    icon: BarChart3,
    title: "Get your report",
    description: "A full breakdown of strengths, weaknesses, and what to work on next.",
  },
];

const fadeUp = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.5, ease: "easeOut" as const },
};

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg">
      <header className="sticky top-0 z-10 border-b border-border-subtle bg-bg/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="h-5 w-5 rounded-md bg-accent" />
            <span className="font-mono text-sm tracking-wide text-text-secondary">interviai</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-sm text-text-secondary transition-colors duration-150 hover:text-text-primary"
            >
              Sign in
            </Link>
            <Link
              to="/register"
              className="flex h-9 items-center rounded-md bg-accent px-4 text-sm font-medium text-bg transition-colors duration-150 hover:bg-accent-hover"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-24 pt-20 sm:pt-28">
        <div
          className="pointer-events-none absolute left-1/2 top-0 h-[480px] w-[900px] -translate-x-1/2 opacity-20 blur-3xl"
          style={{ background: "radial-gradient(ellipse, var(--color-accent) 0%, transparent 70%)" }}
        />

        <div className="relative mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-1.5 rounded-full border border-border-subtle bg-surface px-3 py-1 font-mono text-xs text-text-secondary"
          >
            <Sparkles className="h-3 w-3 text-accent" />
            AI-powered mock interviews
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mt-6 text-4xl font-semibold leading-tight text-text-primary sm:text-5xl"
          >
            Practice interviews that actually adapt to you
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-text-secondary"
          >
            Upload your resume, pick a role, and get interviewed by an AI that reads your answers
            and decides what to ask next — then get a real report on where you stand.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Link
              to="/register"
              className="flex h-11 items-center gap-1.5 rounded-md bg-accent px-5 text-sm font-medium text-bg transition-colors duration-150 hover:bg-accent-hover"
            >
              Start practicing
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/login"
              className="flex h-11 items-center rounded-md border border-border px-5 text-sm font-medium text-text-secondary transition-colors duration-150 hover:text-text-primary"
            >
              Sign in
            </Link>
          </motion.div>
        </div>

        {/* Live preview mockup */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="relative mx-auto mt-16 max-w-2xl rounded-lg border border-border bg-surface p-6"
        >
          <p className="font-mono text-xs uppercase tracking-widest text-text-muted">
            Session preview
          </p>
          <div className="mt-5 flex flex-col gap-3">
            <div className="max-w-md self-start rounded-lg border border-border bg-surface-raised px-4 py-3 text-sm text-text-primary">
              Walk me through how you'd design a rate limiter for a public API.
            </div>
            <div className="max-w-md self-end rounded-lg border border-accent-muted bg-accent-soft px-4 py-3 text-sm text-text-primary">
              I'd start with a token bucket per client, backed by Redis for shared state...
            </div>
            <div className="max-w-md self-start rounded-lg border border-border bg-surface-raised px-4 py-3 text-sm text-text-primary">
              Good. How does that hold up under a thundering-herd scenario?
            </div>
          </div>
          <div className="mt-5 flex items-center justify-between border-t border-border-subtle pt-4">
            <span className="font-mono text-xs text-text-muted">Technical depth: strong</span>
            <span className="rounded-full border border-accent-muted bg-accent-soft px-2.5 py-1 font-mono text-xs text-accent">
              evaluating…
            </span>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <motion.div {...fadeUp} className="mx-auto max-w-xl text-center">
          <h2 className="text-2xl font-semibold text-text-primary">Built like a real interview</h2>
          <p className="mt-3 text-sm text-text-secondary">
            Not a quiz. Not a script. A conversation that responds to what you actually say.
          </p>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: (i % 3) * 0.08 }}
              className="rounded-lg border border-border bg-surface p-5"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-md bg-surface-raised">
                <feature.icon className="h-4 w-4 text-accent" />
              </div>
              <p className="mt-4 text-sm font-medium text-text-primary">{feature.title}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-text-secondary">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-border-subtle bg-surface/40 px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <motion.div {...fadeUp} className="mx-auto max-w-xl text-center">
            <h2 className="text-2xl font-semibold text-text-primary">How it works</h2>
            <p className="mt-3 text-sm text-text-secondary">
              Three steps, in order — your resume comes first because everything after it depends
              on it.
            </p>
          </motion.div>

          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.4, delay: i * 0.12 }}
                className="relative flex flex-col items-center text-center"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-full border border-accent-muted bg-accent-soft">
                  <step.icon className="h-5 w-5 text-accent" />
                </div>
                <p className="mt-1 font-mono text-xs text-text-muted">Step {i + 1}</p>
                <p className="mt-2 text-sm font-medium text-text-primary">{step.title}</p>
                <p className="mt-1.5 max-w-[220px] text-sm leading-relaxed text-text-secondary">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 py-24">
        <motion.div
          {...fadeUp}
          className="mx-auto flex max-w-2xl flex-col items-center rounded-lg border border-border bg-surface px-8 py-14 text-center"
        >
          <h2 className="text-2xl font-semibold text-text-primary">
            Your next interview shouldn't be the first real one
          </h2>
          <p className="mt-3 max-w-md text-sm text-text-secondary">
            Upload your resume and take your first adaptive mock interview in a few minutes.
          </p>
          <Link
            to="/register"
            className="mt-7 flex h-11 items-center gap-1.5 rounded-md bg-accent px-5 text-sm font-medium text-bg transition-colors duration-150 hover:bg-accent-hover"
          >
            Get started for free
            <ArrowRight className="h-4 w-4" />
          </Link>
        </motion.div>
      </section>

      <footer className="border-t border-border-subtle px-6 py-8">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded bg-accent" />
            <span className="font-mono text-xs text-text-muted">interviai</span>
          </div>
          <p className="text-xs text-text-muted">A Collaborative Effort.</p>
        </div>
      </footer>
    </div>
  );
}