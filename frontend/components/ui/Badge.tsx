import { cn } from "@/lib/utils/cn";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "active" | "retired" | "accent" | "gold" | "neutral";
  className?: string;
}

export function Badge({ children, variant = "neutral", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full",
        variant === "active" && "bg-status-active-bg text-status-active",
        variant === "retired" && "bg-surface-elevated text-status-retired",
        variant === "accent" && "bg-accent-muted text-accent",
        variant === "gold" && "bg-gold-muted text-gold",
        variant === "neutral" && "bg-surface-elevated text-text-secondary",
        className
      )}
    >
      {variant === "active" && (
        <span className="w-1.5 h-1.5 rounded-full bg-status-active" />
      )}
      {children}
    </span>
  );
}
