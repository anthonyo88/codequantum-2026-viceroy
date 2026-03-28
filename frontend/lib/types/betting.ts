export interface BettingRequest {
  race_context: string;
  max_picks?: number;
}

export interface BetPick {
  driver_id: string;
  driver_name: string;
  bet_type: "win" | "podium" | "points_finish";
  confidence: "high" | "medium" | "low";
  reason: string;
}

export interface BettingResponse {
  summary: string;
  picks: BetPick[];
  token_count: number;
}
