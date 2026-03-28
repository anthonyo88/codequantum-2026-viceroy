"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Bot, User } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { chatSearch, chatRecommend } from "@/lib/api/chat";
import { useDriver } from "@/lib/hooks/useDriver";
import { DriverCard } from "@/components/drivers/DriverCard";
import type { ChatQueryResponse } from "@/lib/types/chat";

type Mode = "search" | "recommend";

interface Message {
  role: "user" | "assistant";
  content: string;
  driverIds?: string[];
}

export default function ChatPage() {
  const [mode, setMode] = useState<Mode>("search");
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const search = useMutation({
    mutationFn: () =>
      mode === "search"
        ? chatSearch({ query, limit: 5 })
        : chatRecommend({ criteria: query, max_results: 5 }),
    onSuccess: (data: ChatQueryResponse) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          driverIds: data.driver_ids_referenced,
        },
      ]);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || search.isPending) return;
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    search.mutate();
    setQuery("");
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <PageContainer className="flex flex-col h-[calc(100vh-4rem)] py-6 gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-accent" />
            AI Search
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Find drivers using natural language
          </p>
        </div>

        <div className="flex items-center gap-1 bg-surface-elevated border border-border rounded-lg p-1 self-start sm:self-auto">
          <button
            onClick={() => setMode("search")}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              mode === "search"
                ? "bg-surface text-text-primary shadow-sm"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            Search
          </button>
          <button
            onClick={() => setMode("recommend")}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              mode === "recommend"
                ? "bg-surface text-text-primary shadow-sm"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            Recommend
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 min-h-0">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-3">
            <Bot className="w-12 h-12 text-border" />
            <p className="text-text-secondary text-sm max-w-sm">
              {mode === "search"
                ? "Ask anything about drivers — e.g. \"Find aggressive drivers with strong wet weather performance\""
                : "Describe your criteria — e.g. \"Young driver under 25, multiple wins, ready for F1\""}
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === "user"
                  ? "bg-accent/20 border border-accent/30"
                  : "bg-surface-elevated border border-border"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-3.5 h-3.5 text-accent" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-text-secondary" />
              )}
            </div>

            <div className={`flex flex-col gap-3 max-w-2xl ${msg.role === "user" ? "items-end" : ""}`}>
              <div
                className={`px-4 py-3 rounded-lg text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-accent text-white rounded-tr-sm"
                    : "bg-surface border border-border text-text-primary rounded-tl-sm"
                }`}
              >
                {msg.content}
              </div>

              {msg.driverIds && msg.driverIds.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 w-full">
                  {msg.driverIds.map((dId) => (
                    <DriverCardById key={dId} driverId={dId} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {search.isPending && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-surface-elevated border border-border flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5 text-text-secondary animate-pulse" />
            </div>
            <div className="bg-surface border border-border rounded-lg rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center">
                <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="flex gap-2 flex-shrink-0 border-t border-border pt-4"
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            mode === "search"
              ? "Search for drivers…"
              : "Describe the driver you need…"
          }
          className="flex-1 bg-surface border border-border rounded-lg px-4 py-2.5 text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent transition-colors"
        />
        <Button type="submit" loading={search.isPending} disabled={!query.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </form>
    </PageContainer>
  );
}

function DriverCardById({ driverId }: { driverId: string }) {
  const { data: driver } = useDriver(driverId);
  if (!driver) return null;
  return (
    <DriverCard
      driver={{
        id: driver.id,
        full_name: driver.full_name,
        nationality: driver.nationality,
        active_status: driver.active_status,
        career_stats: driver.career_stats,
      }}
    />
  );
}
