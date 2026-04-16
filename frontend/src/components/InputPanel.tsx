import React, { useState } from "react";
import { AnalyzeRequest } from "../types/spectra";

interface Props {
  onAnalyze: (params: AnalyzeRequest) => void;
  isLoading: boolean;
}

export const InputPanel: React.FC<Props> = ({ onAnalyze, isLoading }) => {
  const [ticker, setTicker] = useState("NVDA");
  const [benchmark, setBenchmark] = useState("^GSPC");
  const [period, setPeriod] = useState("1y");
  const [segmentLength, setSegmentLength] = useState(256);
  const [entropyLow, setEntropyLow] = useState(0.45);
  const [entropyHigh, setEntropyHigh] = useState(0.65);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyze({
      ticker: ticker.toUpperCase(),
      benchmark: benchmark.toUpperCase(),
      period,
      segment_length: segmentLength,
      entropy_threshold_low: entropyLow,
      entropy_threshold_high: entropyHigh,
    });
  };

  return (
    <div className="input-panel">
      <form onSubmit={handleSubmit} className="controls-form">
        <div className="input-group">
          <label>Activo (Ticker)</label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="ej. AAPL, NVDA"
            required
          />
        </div>
        <div className="input-group">
          <label>Benchmark</label>
          <input
            type="text"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value)}
            placeholder="ej. ^GSPC"
            required
          />
        </div>
        <div className="input-group">
          <label>Ventana Temporal</label>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="3mo">3 Meses</option>
            <option value="6mo">6 Meses</option>
            <option value="1y">1 Año</option>
            <option value="2y">2 Años</option>
            <option value="5y">5 Años</option>
          </select>
        </div>
        <div className="input-group">
          <label>Resolución Welch (N={segmentLength})</label>
          <input
            type="range"
            min="64"
            max="1024"
            step="64"
            value={segmentLength}
            onChange={(e) => setSegmentLength(Number(e.target.value))}
          />
        </div>
        <button type="submit" disabled={isLoading} className="btn-analyze">
          {isLoading ? (
            <span className="spinner">⟳ Calculando...</span>
          ) : (
            <span>⚡ Ejecutar Análisis Espectral</span>
          )}
        </button>
      </form>
    </div>
  );
};
