"""
SPECTRA — Modelos Pydantic de Solicitudes de la API
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """Solicitud de análisis espectral de un activo."""

    ticker: str = Field(
        ...,
        description="Símbolo bursátil del activo (ej. AAPL, BTC-USD, SPY)",
        examples=["AAPL", "NVDA", "BTC-USD"],
    )
    benchmark: str = Field(
        default="^GSPC",
        description="Símbolo del benchmark de referencia para coherencia cruzada",
    )
    period: str = Field(
        default="1y",
        description="Ventana temporal: 3mo, 6mo, 1y, 2y, 5y",
        pattern="^(3mo|6mo|1y|2y|5y)$",
    )
    segment_length: int = Field(
        default=256,
        ge=64,
        le=4096,
        description="Tamaño del segmento FFT en el estimador de Welch (potencia de 2)",
    )
    entropy_threshold_low: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Umbral inferior de entropía (TENDENCIAL si SE < este valor)",
    )
    entropy_threshold_high: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
        description="Umbral superior de entropía (RUIDOSO si SE > este valor)",
    )


class DataRequest(BaseModel):
    """Solicitud de datos históricos de un activo."""

    ticker: str = Field(
        ...,
        description="Símbolo bursátil del activo",
    )
    period: str = Field(
        default="1y",
        description="Ventana temporal",
        pattern="^(3mo|6mo|1y|2y|5y)$",
    )
