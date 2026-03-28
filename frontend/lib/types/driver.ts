export interface DriverCareerStats {
  total_race_starts: number;
  total_wins: number;
  total_podiums: number;
  total_pole_positions: number;
  total_fastest_laps: number;
  total_championship_points: number;
  championships_won: number;
  career_win_rate: number;
  career_podium_rate: number;
  dnf_rate: number;
  avg_qualifying_position: number | null;
  avg_finish_position: number | null;
  seasons_active: number[];
  teams_driven_for: string[];
  active_status: boolean;
  last_race_date: string | null;
}

export interface DriverSummaryOut {
  id: string;
  full_name: string;
  nationality: string;
  active_status: boolean;
  career_stats: DriverCareerStats;
}

export interface DriverSeason {
  season_year: number;
  championship_position: number | null;
  points: number;
  wins: number;
  podiums: number;
  poles: number;
  fastest_laps: number;
  races_entered: number;
  dnfs: number;
  team_name?: string;
  teammate_qualifying_delta: number | null;
  teammate_race_delta: number | null;
}

export interface DriverOut extends DriverSummaryOut {
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  biography: string | null;
  profile_image_url: string | null;
  license_grade: string | null;
  ergast_driver_id: string | null;
  seasons: DriverSeason[];
  created_at: string;
  updated_at: string;
}

export interface DriverListResponse {
  total: number;
  page: number;
  limit: number;
  drivers: DriverSummaryOut[];
}

export type SortBy =
  | "win_rate"
  | "total_wins"
  | "total_podiums"
  | "championships_won";

export interface DriversQueryParams {
  nationality?: string;
  min_age?: number;
  max_age?: number;
  min_wins?: number;
  max_wins?: number;
  min_podiums?: number;
  min_championships?: number;
  active_only?: boolean;
  sort_by?: SortBy;
  sort_order?: "asc" | "desc";
  page?: number;
  limit?: number;
}

export interface DriverFilterRequest extends DriversQueryParams {}
