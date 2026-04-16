import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { CycleData, InvestmentSignal, RegimeData } from "../types/spectra";

interface Props {
  cycle: CycleData;
  signal: InvestmentSignal;
  regime: RegimeData;
}

export const Panel4_Signal: React.FC<Props> = ({ cycle, signal, regime }) => {
  const phaseGaugeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!phaseGaugeRef.current) return;
    d3.select(phaseGaugeRef.current).selectAll("*").remove();

    const width = 200;
    const height = 120;
    const radius = Math.min(width, height * 2) / 2;

    const svg = d3
      .select(phaseGaugeRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2},${height})`);

    // Arc generator for the gauge background
    const arc = d3
      .arc<void>()
      .innerRadius(radius - 20)
      .outerRadius(radius)
      .startAngle(-Math.PI / 2)
      .endAngle(Math.PI / 2);

    svg
      .append("path")
      .attr("d", arc())
      .attr("fill", "var(--bg-lighter)")
      .attr("stroke", "var(--border-color)");

    // Define colors for the gauge
    const arcColor = d3
      .scaleLinear<string>()
      .domain([0, 50, 100])
      .range(["#10b981", "#fbbf24", "#ef4444"]); // green -> yellow -> red

    // Value arc
    const valueArc = d3
      .arc<void>()
      .innerRadius(radius - 20)
      .outerRadius(radius)
      .startAngle(-Math.PI / 2)
      .endAngle(-Math.PI / 2 + (cycle.phase_pct / 100) * Math.PI);

    svg
      .append("path")
      .attr("d", valueArc())
      .attr("fill", arcColor(cycle.phase_pct));

    // Needle
    const angle = -Math.PI / 2 + (cycle.phase_pct / 100) * Math.PI;
    const needleLength = radius - 5;
    const nx = Math.sin(angle) * needleLength;
    const ny = -Math.cos(angle) * needleLength;

    svg
      .append("line")
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", nx)
      .attr("y2", ny)
      .attr("stroke", "var(--text-primary)")
      .attr("stroke-width", 3)
      .style("filter", "drop-shadow(0 2px 2px rgba(0,0,0,0.5))");
      
    svg.append("circle").attr("cx", 0).attr("cy", 0).attr("r", 5).attr("fill", "var(--text-primary)");

  }, [cycle.phase_pct]);

  const signalColorClass =
    signal.signal === "COMPRAR"
      ? "signal-buy"
      : signal.signal === "VENDER"
      ? "signal-sell"
      : "signal-wait";

  return (
    <div className="panel signal-panel">
      <div className="panel-header">
        <h3>Panel 4: Señal de Inversión y Ciclo</h3>
        <p>Interpretación del análisis espectral mediante reglas LTI.</p>
      </div>

      <div className="signal-content">
        <div className="phase-gauge-container">
          <h4>Fase del Ciclo ({cycle.period_days.toFixed(1)}d)</h4>
          <div ref={phaseGaugeRef} className="gauge"></div>
          <p className="phase-value">{cycle.phase_pct.toFixed(0)}% completado</p>
          <p className="confidence-value">Confianza Espectral: {signal.confidence_pct.toFixed(1)}%</p>
        </div>

        <div className="signal-decision">
          <div className="regime-badge">
            Régimen: <span className={`regime-${regime.regime.toLowerCase()}`}>{regime.regime}</span>
            <span className="entropy-val">(Entropía: {regime.entropy_normalized.toFixed(2)})</span>
          </div>

          <div className={`final-signal-box ${signalColorClass}`}>
            <span className="signal-text">{signal.signal}</span>
            {signal.reinforced && <span className="reinforced-badge">REFORZADO POR MERCADO</span>}
          </div>

          <div className="explanation-box">
            <span className="rule-badge">Regla Técnica #{signal.rule_applied}</span>
            <p>{signal.explanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
