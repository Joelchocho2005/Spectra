"""
SPECTRA — API Principal (FastAPI)

Spectral Pattern & Cycle Trading Regime Analyzer

Endpoints:
    POST /api/analyze   — Ejecuta el pipeline completo de análisis espectral
    POST /api/data      — Devuelve datos históricos y retornos logarítmicos
    GET  /api/health    — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time

from .models.requests import AnalyzeRequest, DataRequest
from .models.responses import AnalyzeResponse, DataResponse
from .services.pipeline import run_analysis_pipeline
from .services.data_service import get_financial_data

app = FastAPI(
    title="SPECTRA API",
    description=(
        "Spectral Pattern & Cycle Trading Regime Analyzer — "
        "Sistema de análisis espectral de señales financieras para la "
        "generación de señales de inversión basadas en la Teoría de "
        "Sistemas Lineales e Invariantes en el Tiempo."
    ),
    version="1.0.0",
    docs_url="/docs",
)

# CORS — permitir conexiones desde el frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check del servidor."""
    return {
        "status": "ok",
        "service": "SPECTRA API",
        "version": "1.0.0",
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Ejecuta el pipeline completo de análisis espectral de SPECTRA.

    Flujo:
        [Datos] → [Retornos log] → [Welch PSD] → [Entropía → Régimen]
        → [Ciclo + Fase] → [Coherencia] → [Filtrado IFFT] → [Decisión]

    Returns
    -------
    AnalyzeResponse
        Resultado completo con datos para los 4 paneles del frontend.
    """
    try:
        start_time = time.time()

        result = run_analysis_pipeline(
            ticker=request.ticker,
            benchmark=request.benchmark,
            period=request.period,
            segment_length=request.segment_length,
            entropy_threshold_low=request.entropy_threshold_low,
            entropy_threshold_high=request.entropy_threshold_high,
        )

        elapsed = time.time() - start_time
        result["processing_time_ms"] = round(elapsed * 1000, 1)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en el pipeline de análisis: {str(e)}",
        )


@app.post("/api/data", response_model=DataResponse)
async def get_data(request: DataRequest):
    """
    Obtiene datos históricos y retornos logarítmicos de un activo.

    Returns
    -------
    DataResponse
        Datos históricos con precios y retornos.
    """
    try:
        data = get_financial_data(request.ticker, request.period)

        return {
            "ticker": request.ticker.upper(),
            "period": request.period,
            "dates": data["dates"],
            "prices": data["prices"].tolist(),
            "returns": data["returns"].tolist(),
            "data_points": len(data["returns"]),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo datos: {str(e)}",
        )
