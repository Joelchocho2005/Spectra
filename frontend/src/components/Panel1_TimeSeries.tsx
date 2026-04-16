import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { TimeSeriesData, CycleData } from "../types/spectra";

interface Props {
  data: TimeSeriesData;
  cycleInfo: CycleData;
}

export const Panel1_TimeSeries: React.FC<Props> = ({ data, cycleInfo }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data.dates.length || !containerRef.current) return;

    // Clear prev
    d3.select(containerRef.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 30, left: 50 };
    const width = containerRef.current.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3
      .select(containerRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const parseDate = d3.timeParse("%Y-%m-%d");
    const formattedDates = data.dates.map((d) => parseDate(d) as Date);

    const x = d3
      .scaleTime()
      .domain(d3.extent(formattedDates) as [Date, Date])
      .range([0, width]);

    const y = d3
      .scaleLinear()
      .domain([d3.min(data.prices) as number, d3.max(data.prices) as number])
      .range([height, 0]);

    // Grid lines
    svg
      .append("g")
      .attr("class", "grid")
      .attr("color", "var(--border-color)")
      .attr("stroke-dasharray", "3,3")
      .call(d3.axisLeft(y).tickSize(-width).tickFormat(() => ""))
      .select(".domain").remove();

    // Axes
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5))
      .attr("color", "var(--text-secondary)");

    svg
      .append("g")
      .call(d3.axisLeft(y).ticks(6))
      .attr("color", "var(--text-secondary)");

    // Define line
    const line = d3
      .line<number>()
      .x((_, i) => x(formattedDates[i]))
      .y((d) => y(d));

    // Glow filter
    const defs = svg.append("defs");
    const filter = defs.append("filter").attr("id", "glow");
    filter.append("feGaussianBlur").attr("stdDeviation", "2").attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Price path
    svg
      .append("path")
      .datum(data.prices)
      .attr("fill", "none")
      .attr("stroke", "var(--primary-color)")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Trend component path (if exists)
    if (data.trend_component && cycleInfo.frequency > 0) {
      // Scale trend to match price magnitude roughly for visual super-position (trend is from log returns usually, needs scaling or it's centered around 0)
      // Visualizer logic: trend_component is actually the reconstructed log-returns trend. 
      // To overlay it meaningfully on price, we either plot it on a sec axis or integrate.
      // Based on the pdf "Señal de tendencia filtrada visible sobre el precio original",
      // we'll center it on the moving average of price.
      const meanPrice = d3.mean(data.prices) || 0;
      const stdPrice = d3.deviation(data.prices) || 1;
      const stdTrend = d3.deviation(data.trend_component) || 1;
      const scaleFactor = stdPrice / stdTrend * 0.5; // Arbitrary visual scaling factor
      
      const scaledTrendLine = d3
        .line<number>()
        .x((_, i) => x(formattedDates[i]))
        .y((d) => y(meanPrice + d * scaleFactor))
        //.curve(d3.curveBasis);

      svg
        .append("path")
        .datum(data.trend_component)
        .attr("fill", "none")
        .attr("stroke", "var(--secondary-color)")
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", "4,4")
        .style("filter", "url(#glow)")
        .attr("d", scaledTrendLine);
    }
  }, [data, cycleInfo]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h3>Panel 1: Señal de Tiempo y Tendencia</h3>
        <p>Precio de cierre y proyección de tendencia espectral filtrada por IFFT.</p>
      </div>
      <div className="svg-container" ref={containerRef} />
    </div>
  );
};
