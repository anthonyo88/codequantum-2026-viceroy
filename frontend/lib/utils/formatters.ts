export function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value: number): string {
  return value.toLocaleString();
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function calcAge(dob: string): number {
  const birth = new Date(dob);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age--;
  return age;
}

export function nationalityFlag(nationality: string): string {
  const map: Record<string, string> = {
    British: "🇬🇧",
    German: "🇩🇪",
    Finnish: "🇫🇮",
    Dutch: "🇳🇱",
    Spanish: "🇪🇸",
    Brazilian: "🇧🇷",
    French: "🇫🇷",
    Australian: "🇦🇺",
    Austrian: "🇦🇹",
    Mexican: "🇲🇽",
    Canadian: "🇨🇦",
    Italian: "🇮🇹",
    Danish: "🇩🇰",
    Chinese: "🇨🇳",
    American: "🇺🇸",
    Japanese: "🇯🇵",
    Thai: "🇹🇭",
    Monegasque: "🇲🇨",
    Swiss: "🇨🇭",
    Belgian: "🇧🇪",
    Polish: "🇵🇱",
    Argentinian: "🇦🇷",
    Hungarian: "🇭🇺",
    "New Zealander": "🇳🇿",
    "South African": "🇿🇦",
  };
  return map[nationality] ?? "🏁";
}
