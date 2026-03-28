import { cn } from "@/lib/utils/cn";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export function Card({ children, className, hover, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-surface border border-border rounded-lg p-4 shadow-card",
        hover &&
          "hover:shadow-card-hover hover:border-accent/20 transition-all duration-200 cursor-pointer",
        className
      )}
    >
      {children}
    </div>
  );
}
