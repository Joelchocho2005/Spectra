import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { CoherenceData } from "../types/spectra";

interface Props {
  data: CoherenceData;
}

export const Panel3_Coherence: React.FC<Props> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data.frequencies.length || !containerRef.current) return;

    d3.select(containerRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = containerRef.current.clientWidth - margin.left - margin.right;
    const height = 250 - margin.top - margin.bottom;

    const svg = d3
      .select(containerRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3
      .scaleLinear()
      .domain([0, d3.max(data.frequencies) as number])
      .range([0, width]);

    // Coherence is between 0 and 1
    const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

    // Reference line at 0.75 (threshold)
    svg
      .append("line")
      .attr("x1", 0)
      .attr("y1", y(0.75))
      .attr("x2", width)
      .attr("y2", y(0.75))
      .attr("stroke", "var(--danger-color)")
      .attr("stroke-dasharray", "4,4")
      .attr("stroke-width", 1.5)
      .style("opacity", 0.5);

    svg
      .append("text")
      .attr("x", width - 5)
      .attr("y", y(0.75) - 5)
      .attr("text-anchor", "end")
      .attr("fill", "var(--danger-color)")
      .style("font-size", "10px")
      .text("Umbral Sincronización > 0.75");

    // Line generator
    const line = d3
      .line<number>()
      .x((_, i) => x(data.frequencies[i]))
      .y((d) => y(d))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(data.coherence)
      .attr("fill", "none")
      .attr("stroke", "var(--tertiary-color)")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Axes
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .attr("color", "var(--text-secondary)");

    svg
      .append("g")
      .call(d3.axisLeft(y).ticks(5))
      .attr("color", "var(--text-secondary)");

  }, [data]);

  return (
    <div className="panel coherence-panel">
      <div className="panel-header">
        <h3>Panel 3: Coherencia Cruzada vs {data.benchmark_ticker}</h3>
        <p>Sincronización espectral entre el activo y su índice de referencia.</p>
      </div>
      <div className="svg-container" ref={containerRef} />
      <div className="coherence-stats">
        <div className="stat-box">
          <span className="stat-label">Coherencia en Ciclo Dominante</span>
          <span className={`stat-value ${data.coherence_at_dominant > 0.75 ? "highlight-good" : ""}`}>
            {(data.coherence_at_dominant * 100).toFixed(1)}%
          </span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Régimen {data.benchmark_ticker}</span>
          <span className={`stat-value regime-${data.benchmark_regime?.toLowerCase() || 'unknown'}`}>
            {data.benchmark_regime || "NO CALCULADO"}
          </span>
        </div>
      </div>
    </div>
  );
};
