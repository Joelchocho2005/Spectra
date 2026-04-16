export interface AnalyzeRequest {
  ticker: string;
  benchmark?: string;
  period?: string;
  segment_length?: number;
  entropy_threshold_low?: number;
  entropy_threshold_high?: number;
}

export interface DataRequest {
  ticker: string;
  period?: string;
}

export interface TimeSeriesData {
  dates: string[];
  prices: number[];
  returns: number[];
  trend_component?: number[];
}

export interface SpectralData {
  frequencies: number[];
  psd: number[];
  dominant_frequency: number;
  dominant_period_days: number;
  dominant_k_peak: number;
}

export interface RegimeData {
  entropy_normalized: number;
  regime: string;
  threshold_low: number;
  threshold_high: number;
}

export interface CycleData {
  period_days: number;
  frequency: number;
  phase_rad: number;
  phase_pct: number;
  energy_ratio: number;
}

export interface CoherenceData {
  frequencies: number[];
  coherence: number[];
  coherence_at_dominant: number;
  benchmark_ticker: string;
  benchmark_regime?: string;
}

export interface InvestmentSignal {
  signal: string;
  confidence_pct: number;
  rule_applied: number;
  explanation: string;
  reinforced: boolean;
}

export interface AnalyzeResponse {
  ticker: string;
  benchmark: string;
  period: string;
  analysis_date: string;
  data_points: number;
  time_series: TimeSeriesData;
  spectral: SpectralData;
  regime: RegimeData;
  coherence: CoherenceData;
  cycle: CycleData;
  signal: InvestmentSignal;
}

export interface DataResponse {
  ticker: string;
  period: string;
  dates: string[];
  prices: number[];
  returns: number[];
  data_points: number;
}
