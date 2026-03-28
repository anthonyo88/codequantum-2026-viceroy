"use client";

import { useState } from "react";
import { TrendingUp, Sparkles } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { BetPickCard } from "@/components/betting/BetPickCard";
import { getBettingPrediction } from "@/lib/api/betting";
import type { BettingResponse } from "@/lib/types/betting";

const EXAMPLE_CONTEXTS = [
  "Monaco GP 2024, street circuit, historically favours experience over raw pace",
  "Spa-Francorchamps, mixed conditions expected, high-speed corners",
  "Bahrain GP, dry desert track, strong tire degradation",
];

export default function BettingPage() {
  const [raceContext, setRaceContext] = useState("");
  const [result, setResult] = useState<BettingResponse | null>(null);

  const predict = useMutation({
    mutationFn: () => getBettingPrediction({ race_context: raceContext, max_picks: 5 }),
    onSuccess: (data) => setResult(data),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!raceContext.trim() || predict.isPending) return;
    setResult(null);
    predict.mutate();
  }

  return (
    <PageContainer className="flex flex-col gap-6 py-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-accent" />
          F1 Betting Picks
        </h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Describe an upcoming race and the AI will recommend the best bets based on driver history
        </p>
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={raceContext}
          onChange={(e) => setRaceContext(e.target.value)}
          rows={3}
          placeholder="Describe the race context — e.g. 'Monaco GP 2024, wet conditions, street circuit'"
          className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent transition-colors resize-none"
        />

        {/* Example prompts */}
        {!raceContext && (
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_CONTEXTS.map((ctx) => (
              <button
                key={ctx}
                type="button"
                onClick={() => setRaceContext(ctx)}
                className="text-xs text-text-muted border border-border rounded px-2.5 py-1 hover:text-text-secondary hover:border-accent/30 transition-colors"
              >
                {ctx}
              </button>
            ))}
          </div>
        )}

        <div className="flex justify-end">
          <Button type="submit" loading={predict.isPending} disabled={!raceContext.trim()}>
            <Sparkles className="w-4 h-4 mr-1.5" />
            Get Picks
          </Button>
        </div>
      </form>

      {/* Loading state */}
      {predict.isPending && (
        <div className="bg-surface border border-border rounded-lg px-4 py-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-text-secondary animate-pulse" />
          <div className="flex gap-1 items-center">
            <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
          <span className="text-text-muted text-sm">Analysing driver data…</span>
        </div>
      )}

      {/* Error state */}
      {predict.isError && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
          Failed to get predictions. Please try again.
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="flex flex-col gap-4">
          {/* LLM summary */}
          <div className="bg-surface border border-border rounded-lg px-4 py-3 text-text-primary text-sm leading-relaxed">
            {result.summary}
          </div>

          {/* Picks grid */}
          {result.picks.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {result.picks.map((pick, i) => (
                <BetPickCard key={`${pick.driver_id}-${i}`} pick={pick} />
              ))}
            </div>
          ) : (
            <p className="text-text-muted text-sm text-center py-4">
              No picks returned. Try a more specific race context.
            </p>
          )}

          <p className="text-text-muted text-xs text-right">
            {result.token_count} tokens used
          </p>
        </div>
      )}

      {/* Empty state */}
      {!result && !predict.isPending && (
        <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
          <TrendingUp className="w-12 h-12 text-border" />
          <p className="text-text-secondary text-sm max-w-sm">
            Enter a race context above to get AI-powered betting recommendations based on driver performance data
          </p>
        </div>
      )}
    </PageContainer>
  );
}
