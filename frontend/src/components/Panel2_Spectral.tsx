import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { SpectralData } from "../types/spectra";

interface Props {
  data: SpectralData;
}

export const Panel2_Spectral: React.FC<Props> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data.frequencies.length || !containerRef.current) return;

    d3.select(containerRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = containerRef.current.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3
      .select(containerRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Only plot positive frequencies
    const x = d3
      .scaleLinear()
      .domain([0, d3.max(data.frequencies) as number])
      .range([0, width]);

    // Use logarithmic scale for PSD to see peaks better, or linear if log not specified. 
    // Usually PSD is plotted in dB or semi-log y
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data.psd) as number])
      .range([height, 0]);

    // Area generator for PSD
    const area = d3
      .area<number>()
      .x((_, i) => x(data.frequencies[i]))
      .y0(height)
      .y1((d) => y(d))
      .curve(d3.curveMonotoneX);

    // Defs for gradient
    const defs = svg.append("defs");
    const gradient = defs
      .append("linearGradient")
      .attr("id", "psd-gradient")
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "0%")
      .attr("y2", "100%");

    gradient.append("stop").attr("offset", "0%").attr("stop-color", "var(--secondary-color)").attr("stop-opacity", 0.6);
    gradient.append("stop").attr("offset", "100%").attr("stop-color", "var(--background-color)").attr("stop-opacity", 0.1);

    // Grid lines
    svg
      .append("g")
      .attr("class", "grid")
      .attr("color", "var(--border-color)")
      .attr("stroke-dasharray", "3,3")
      .call(d3.axisBottom(x).tickSize(height).tickFormat(() => ""))
      .select(".domain").remove();

    // Plot area
    svg
      .append("path")
      .datum(data.psd)
      .attr("fill", "url(#psd-gradient)")
      .attr("stroke", "var(--secondary-color)")
      .attr("stroke-width", 2)
      .attr("d", area);

    // Highlight dominant frequency
    if (data.dominant_frequency > 0) {
      svg
        .append("line")
        .attr("x1", x(data.dominant_frequency))
        .attr("y1", 0)
        .attr("x2", x(data.dominant_frequency))
        .attr("y2", height)
        .attr("stroke", "var(--accent-color)")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "4,4")
        .style("filter", "drop-shadow(0 0 5px var(--accent-color))");

      svg
        .append("circle")
        .attr("cx", x(data.dominant_frequency))
        .attr("cy", y(data.psd[data.dominant_k_peak - 1] || data.psd[data.dominant_k_peak] || 0))
        .attr("r", 5)
        .attr("fill", "var(--accent-color)")
        .style("filter", "drop-shadow(0 0 8px var(--accent-color))");

      // Label
      svg
        .append("text")
        .attr("x", x(data.dominant_frequency) + 10)
        .attr("y", 20)
        .attr("fill", "var(--text-primary)")
        .style("font-size", "12px")
        .style("font-weight", "600")
        .text(`Ciclo: ${data.dominant_period_days.toFixed(1)} días`);
    }

    // Axes
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .attr("color", "var(--text-secondary)");

    svg
      .append("text")
      .attr("text-anchor", "middle")
      .attr("x", width / 2)
      .attr("y", height + 35)
      .attr("fill", "var(--text-secondary)")
      .style("font-size", "12px")
      .text("Frecuencia (1/días)");

    svg
      .append("g")
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d3.format(".1e")(d as number)))
      .attr("color", "var(--text-secondary)");

  }, [data]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h3>Panel 2: Densidad de Potencia Espectral (Welch)</h3>
        <p>Distribución de la energía de la señal en el dominio de la frecuencia.</p>
      </div>
      <div className="svg-container" ref={containerRef} />
    </div>
  );
};
