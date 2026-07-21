import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Shield,
  Cpu,
  GitBranch,
  Lock,
  Zap,
  Server,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const features = [
  {
    icon: Lock,
    title: "Local-first by design",
    body: "Source, tokens, and reviews stay on your machine. No hosted backend. No cloud database.",
  },
  {
    icon: Cpu,
    title: "BYOK & provider agnostic",
    body: "Ollama by default, plus LM Studio, vLLM, OpenAI, Anthropic, and OpenRouter.",
  },
  {
    icon: GitBranch,
    title: "GitHub & GitLab",
    body: "OAuth with PKCE and a localhost callback — never a hosted auth server.",
  },
  {
    icon: Zap,
    title: "Multi-agent reviews",
    body: "Security, performance, architecture, style, and maintainability specialists merge into one review.",
  },
];

const faqs = [
  {
    q: "Does my code leave my machine?",
    a: "Not unless you choose a cloud AI provider. With Ollama, LM Studio, or vLLM, inference stays local.",
  },
  {
    q: "Do I need to deploy anything?",
    a: "No. Open Review is a desktop app with an embedded FastAPI backend. Zero maintainer infrastructure.",
  },
  {
    q: "Can I use my own API keys?",
    a: "Yes. Bring your own keys for OpenAI, Anthropic, or OpenRouter. Keys are encrypted at rest locally.",
  },
  {
    q: "What about offline use?",
    a: "Fully supported with local models via Ollama. Clone repos, review diffs, and work without internet.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <Link to="/" className="flex items-center gap-2 font-display font-semibold tracking-tight">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-primary text-xs font-bold">
              OR
            </span>
            Open Review
          </Link>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <a href="https://github.com/AayushGokhale2005/open-review" target="_blank" rel="noreferrer">
                Documentation
              </a>
            </Button>
            <Button size="sm" asChild>
              <Link to="/onboarding">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero — brand first, one composition */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(45,212,191,0.12),_transparent_60%)]" />
        <div className="relative mx-auto flex min-h-[88vh] max-w-6xl flex-col items-center justify-center px-6 text-center">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="font-display text-5xl font-bold tracking-tight sm:text-7xl md:text-8xl"
          >
            Open Review
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mt-6 max-w-2xl text-xl text-muted-foreground sm:text-2xl"
          >
            Your code stays on your machine.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-4 max-w-xl text-sm text-muted-foreground/80"
          >
            Local-first AI code review for developers who refuse to ship their source to someone else&apos;s cloud.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-3"
          >
            <Button size="lg" asChild>
              <Link to="/onboarding">Get Started</Link>
            </Button>
            <Button size="lg" variant="secondary" asChild>
              <Link to="/onboarding?provider=github">Connect GitHub</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/onboarding?provider=gitlab">Connect GitLab</Link>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-16 w-full max-w-4xl overflow-hidden rounded-xl border border-border bg-card/80 shadow-2xl"
          >
            <div className="flex items-center gap-2 border-b border-border px-4 py-2">
              <span className="h-2.5 w-2.5 rounded-full bg-destructive/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/70" />
              <span className="ml-3 text-xs text-muted-foreground font-mono">review · PR #42</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] text-left">
              <div className="border-r border-border p-3 text-xs font-mono text-muted-foreground space-y-1">
                <div className="text-foreground">engine.py</div>
                <div>base.py</div>
                <div>ReviewPage.tsx</div>
              </div>
              <pre className="overflow-x-auto p-4 text-xs font-mono leading-relaxed text-muted-foreground">
                <span className="text-success">+ class ReviewEngine:</span>
                {"\n"}
                <span className="text-success">+     async def run(self, *, title, files):</span>
                {"\n"}
                <span className="text-success">+         for agent in self.pipeline_agents:</span>
                {"\n"}
                <span className="text-warning">  ⚠ security · potential injection risk · L42</span>
              </pre>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-24">
        <h2 className="font-display text-3xl font-semibold tracking-tight">Features</h2>
        <p className="mt-2 text-muted-foreground">Everything you need for private AI code review.</p>
        <div className="mt-10 grid gap-6 sm:grid-cols-2">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="rounded-xl border border-border bg-card/50 p-6"
            >
              <f.icon className="h-5 w-5 text-primary" />
              <h3 className="mt-4 font-display font-medium">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="border-y border-border bg-muted/40 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex items-start gap-4">
            <Shield className="h-8 w-8 text-primary shrink-0" />
            <div>
              <h2 className="font-display text-3xl font-semibold tracking-tight">Privacy</h2>
              <p className="mt-3 max-w-2xl text-muted-foreground">
                Telemetry is off by default. Tokens are encrypted at rest. Reviews run through an
                embedded localhost API — never a SaaS control plane owned by this project.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-24">
        <h2 className="font-display text-3xl font-semibold tracking-tight">How it works</h2>
        <ol className="mt-10 grid gap-6 sm:grid-cols-4">
          {["Choose AI", "Connect Git", "Import repos", "Review PRs"].map((step, i) => (
            <li key={step} className="relative rounded-xl border border-border bg-card/40 p-5">
              <span className="font-mono text-xs text-primary">0{i + 1}</span>
              <p className="mt-2 font-medium">{step}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="font-display text-3xl font-semibold tracking-tight">Supported AI providers</h2>
        <div className="mt-8 flex flex-wrap gap-3">
          {["Ollama", "LM Studio", "vLLM", "OpenAI", "Anthropic", "OpenRouter"].map((p) => (
            <span key={p} className="rounded-md border border-border bg-card px-4 py-2 text-sm">
              {p}
            </span>
          ))}
        </div>
        <h2 className="mt-16 font-display text-3xl font-semibold tracking-tight">Supported Git providers</h2>
        <div className="mt-8 flex flex-wrap gap-3">
          {["GitHub", "GitLab"].map((p) => (
            <span key={p} className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-4 py-2 text-sm">
              <Server className="h-4 w-4 text-muted-foreground" />
              {p}
            </span>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-24">
        <h2 className="font-display text-3xl font-semibold tracking-tight text-center">FAQ</h2>
        <div className="mt-10 space-y-3">
          {faqs.map((f) => (
            <FaqItem key={f.q} q={f.q} a={f.a} />
          ))}
        </div>
      </section>

      <footer className="border-t border-border py-10 text-center text-sm text-muted-foreground">
        Open Review · Apache 2.0 · Your code stays on your machine.
      </footer>
    </div>
  );
}

function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <button
      type="button"
      onClick={() => setOpen((v) => !v)}
      className="w-full rounded-xl border border-border bg-card/50 px-5 py-4 text-left transition hover:bg-card"
    >
      <div className="flex items-center justify-between gap-4">
        <span className="font-medium">{q}</span>
        <ChevronDown className={`h-4 w-4 shrink-0 transition ${open ? "rotate-180" : ""}`} />
      </div>
      {open && <p className="mt-3 text-sm text-muted-foreground">{a}</p>}
    </button>
  );
}
