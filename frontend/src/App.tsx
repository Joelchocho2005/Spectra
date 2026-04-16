import React, { useState } from "react";
import "./index.css";
import { AnalyzeRequest, AnalyzeResponse } from "./types/spectra";
import { SpectraService } from "./services/api";
import { InputPanel } from "./components/InputPanel";
import { Panel1_TimeSeries } from "./components/Panel1_TimeSeries";
import { Panel2_Spectral } from "./components/Panel2_Spectral";
import { Panel3_Coherence } from "./components/Panel3_Coherence";
import { Panel4_Signal } from "./components/Panel4_Signal";

function App() {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (params: AnalyzeRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await SpectraService.analyze(params);
      setData(result);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Error al conectar con la API."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <h1>SPECTRA</h1>
          <div className="subtitle">
            Spectral Pattern & Cycle Trading Regime Analyzer
          </div>
        </div>
      </header>

      <InputPanel onAnalyze={handleAnalyze} isLoading={loading} />

      {error && (
        <div style={{ color: "var(--danger-color)", padding: "1rem", border: "1px solid var(--danger-color)", borderRadius: 8 }}>
          <strong>Error de Análisis:</strong> {error}
        </div>
      )}

      {data && (
        <div className="dashboard-grid">
          <Panel1_TimeSeries data={data.time_series} cycleInfo={data.cycle} />
          <Panel2_Spectral data={data.spectral} />
          <Panel3_Coherence data={data.coherence} />
          <Panel4_Signal cycle={data.cycle} signal={data.signal} regime={data.regime} />
        </div>
      )}
    </div>
  );
}

export default App;
