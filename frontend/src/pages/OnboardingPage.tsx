import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Cpu, FolderGit2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/stores/app-store";
import { useDemoLogin, useUpdateSettings } from "@/hooks/use-api";
import { toast } from "sonner";

const providers = [
  { id: "ollama", name: "Ollama", desc: "Free & local — recommended", local: true },
  { id: "lmstudio", name: "LM Studio", desc: "Local OpenAI-compatible", local: true },
  { id: "openai", name: "OpenAI", desc: "Cloud · BYOK", local: false },
  { id: "anthropic", name: "Anthropic", desc: "Cloud · BYOK", local: false },
];

const steps = ["Welcome", "AI Provider", "Connect Git", "Repository", "Ready"];

export function OnboardingPage() {
  const [params] = useSearchParams();
  const [step, setStep] = useState(0);
  const [aiProvider, setAiProvider] = useState("ollama");
  const [gitProvider, setGitProvider] = useState(params.get("provider") ?? "github");
  const [repoPath, setRepoPath] = useState("~/AIReviewer/repos");
  const navigate = useNavigate();
  const { setOnboardingDone, setUser } = useAppStore();
  const demoLogin = useDemoLogin();
  const updateSettings = useUpdateSettings();

  const next = () => setStep((s) => Math.min(s + 1, steps.length - 1));
  const back = () => setStep((s) => Math.max(s - 1, 0));

  const finish = async () => {
    try {
      const user = await demoLogin.mutateAsync();
      setUser(user);
      await updateSettings.mutateAsync({
        ai_provider: aiProvider,
        repos_path: repoPath,
        onboarding_completed: true,
      });
      setOnboardingDone(true);
      toast.success("You're ready to review.");
      navigate("/app");
    } catch {
      // Backend may be offline — still allow local demo
      setOnboardingDone(true);
      toast.message("Continuing in offline demo mode");
      navigate("/app");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-xl">
        <div className="mb-8 flex items-center justify-center gap-2">
          {steps.map((label, i) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium ${
                  i <= step ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                }`}
              >
                {i < step ? <Check className="h-3.5 w-3.5" /> : i + 1}
              </div>
              {i < steps.length - 1 && (
                <div className={`h-px w-6 sm:w-10 ${i < step ? "bg-primary" : "bg-border"}`} />
              )}
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-border bg-card/80 p-8 shadow-xl backdrop-blur">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.2 }}
            >
              {step === 0 && (
                <div className="text-center">
                  <Sparkles className="mx-auto h-10 w-10 text-primary" />
                  <h1 className="mt-4 font-display text-3xl font-semibold">Welcome to Open Review</h1>
                  <p className="mt-3 text-muted-foreground">
                    Your code stays on your machine. Let&apos;s set up a private AI review workspace
                    in under a minute.
                  </p>
                </div>
              )}

              {step === 1 && (
                <div>
                  <div className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-primary" />
                    <h1 className="font-display text-2xl font-semibold">Choose AI provider</h1>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Ollama is recommended for a completely free, offline-capable setup.
                  </p>
                  <div className="mt-6 grid gap-2">
                    {providers.map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setAiProvider(p.id)}
                        className={`flex items-center justify-between rounded-lg border px-4 py-3 text-left transition ${
                          aiProvider === p.id
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-accent"
                        }`}
                      >
                        <div>
                          <div className="font-medium">{p.name}</div>
                          <div className="text-xs text-muted-foreground">{p.desc}</div>
                        </div>
                        {p.local && (
                          <span className="text-[10px] uppercase tracking-wide text-primary">Local</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div>
                  <h1 className="font-display text-2xl font-semibold">Connect Git</h1>
                  <p className="mt-2 text-sm text-muted-foreground">
                    OAuth with PKCE uses a localhost callback — no hosted auth server.
                  </p>
                  <div className="mt-6 grid gap-3 sm:grid-cols-2">
                    <button
                      type="button"
                      onClick={() => setGitProvider("github")}
                      className={`flex flex-col items-center gap-2 rounded-xl border p-6 ${
                        gitProvider === "github" ? "border-primary bg-primary/10" : "border-border"
                      }`}
                    >
                      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-muted font-mono text-sm font-bold">
                        GH
                      </span>
                      <span className="font-medium">GitHub</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setGitProvider("gitlab")}
                      className={`flex flex-col items-center gap-2 rounded-xl border p-6 ${
                        gitProvider === "gitlab" ? "border-primary bg-primary/10" : "border-border"
                      }`}
                    >
                      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-muted font-mono text-sm font-bold">
                        GL
                      </span>
                      <span className="font-medium">GitLab</span>
                    </button>
                  </div>
                  <p className="mt-4 text-xs text-muted-foreground">
                    For local development you can continue with a demo session and connect OAuth later
                    in Settings.
                  </p>
                </div>
              )}

              {step === 3 && (
                <div>
                  <div className="flex items-center gap-2">
                    <FolderGit2 className="h-5 w-5 text-primary" />
                    <h1 className="font-display text-2xl font-semibold">Repository folder</h1>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Clones and imports live under your local repos directory.
                  </p>
                  <label className="mt-6 block text-xs text-muted-foreground">Local path</label>
                  <Input
                    className="mt-1"
                    value={repoPath}
                    onChange={(e) => setRepoPath(e.target.value)}
                  />
                </div>
              )}

              {step === 4 && (
                <div className="text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/15 text-primary">
                    <Check className="h-7 w-7" />
                  </div>
                  <h1 className="mt-4 font-display text-3xl font-semibold">You&apos;re ready</h1>
                  <p className="mt-3 text-muted-foreground">
                    {aiProvider} · {gitProvider} · {repoPath}
                  </p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          <div className="mt-8 flex justify-between">
            <Button variant="ghost" onClick={back} disabled={step === 0}>
              Back
            </Button>
            {step < steps.length - 1 ? (
              <Button onClick={next}>Continue</Button>
            ) : (
              <Button onClick={() => void finish()} disabled={demoLogin.isPending}>
                Open Dashboard
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
