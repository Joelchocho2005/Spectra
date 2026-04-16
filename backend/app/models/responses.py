"""
SPECTRA — Modelos Pydantic de Respuestas de la API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TimeSeriesData(BaseModel):
    """Datos de series de tiempo."""
    dates: List[str]
    prices: List[float]
    returns: List[float]
    trend_component: Optional[List[float]] = None


class SpectralData(BaseModel):
    """Datos del análisis espectral."""
    frequencies: List[float]
    psd: List[float]
    dominant_frequency: float
    dominant_period_days: float
    dominant_k_peak: int


class RegimeData(BaseModel):
    """Datos del régimen de mercado."""
    entropy_normalized: float
    regime: str  # "TENDENCIAL", "MEDIA-REVERSIVO", "RUIDOSO"
    threshold_low: float
    threshold_high: float


class CycleData(BaseModel):
    """Datos del ciclo dominante."""
    period_days: float
    frequency: float
    phase_rad: float
    phase_pct: float
    energy_ratio: float


class CoherenceData(BaseModel):
    """Datos de coherencia espectral cruzada."""
    frequencies: List[float]
    coherence: List[float]
    coherence_at_dominant: float
    benchmark_ticker: str
    benchmark_regime: Optional[str] = None


class InvestmentSignal(BaseModel):
    """Señal de inversión accionable."""
    signal: str  # "COMPRAR", "VENDER", "ESPERAR"
    confidence_pct: float
    rule_applied: int
    explanation: str
    reinforced: bool


class AnalyzeResponse(BaseModel):
    """Respuesta completa del análisis espectral."""
    ticker: str
    benchmark: str
    period: str
    analysis_date: str
    data_points: int

    # Panel 1 — Señal de tiempo
    time_series: TimeSeriesData

    # Panel 2 — Análisis espectral
    spectral: SpectralData
    regime: RegimeData

    # Panel 3 — Coherencia cruzada
    coherence: CoherenceData

    # Panel 4 — Ciclo dominante y señal de inversión
    cycle: CycleData
    signal: InvestmentSignal


class DataResponse(BaseModel):
    """Respuesta con datos históricos."""
    ticker: str
    period: str
    dates: List[str]
    prices: List[float]
    returns: List[float]
    data_points: int
