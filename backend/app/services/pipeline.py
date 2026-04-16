"""
SPECTRA — Pipeline de Análisis Espectral

Orquesta la ejecución secuencial de todos los módulos DSP:
1. Welch PSD
2. Entropía espectral → Régimen
3. Ciclo dominante + Fase
4. Coherencia cruzada con benchmark
5. Filtrado por bandas (tendencia)
6. Función de decisión → Señal de inversión
"""

import numpy as np
from datetime import datetime
from typing import Dict

from ..dsp.welch import welch_psd
from ..dsp.spectral_entropy import spectral_entropy_normalized
from ..dsp.coherence import spectral_coherence
from ..dsp.bandpass_filter import extract_trend_component
from ..dsp.cycle_detector import detect_dominant_cycle
from ..dsp.decision import investment_decision
from .data_service import get_financial_data


def run_analysis_pipeline(
    ticker: str,
    benchmark: str = "^GSPC",
    period: str = "1y",
    segment_length: int = 256,
    entropy_threshold_low: float = 0.45,
    entropy_threshold_high: float = 0.65,
) -> Dict:
    """
    Ejecuta el pipeline completo de análisis espectral de SPECTRA.

    Flujo:
        [Datos yfinance] → [Retornos log] → [Welch PSD] → [Entropía] → [Régimen]
        → [Ciclo dominante + Fase] → [Coherencia cruzada] → [Filtrado IFFT]
        → [Función de decisión] → [Señal de inversión]

    Parameters
    ----------
    ticker : str
        Símbolo del activo a analizar.
    benchmark : str
        Símbolo del benchmark de referencia.
    period : str
        Ventana temporal.
    segment_length : int
        Tamaño del segmento para Welch.
    entropy_threshold_low : float
        Umbral inferior de entropía.
    entropy_threshold_high : float
        Umbral superior de entropía.

    Returns
    -------
    dict
        Resultado completo del análisis (compatible con AnalyzeResponse).
    """
    # ============================================================
    # 1. OBTENER DATOS
    # ============================================================
    asset_data = get_financial_data(ticker, period)
    returns = asset_data["returns"]
    prices = asset_data["prices"]
    dates = asset_data["dates"]

    # Ajustar segment_length si la señal es corta
    actual_segment_length = min(segment_length, len(returns))
    # Asegurar que sea potencia de 2
    actual_segment_length = 2 ** int(np.floor(np.log2(actual_segment_length)))
    actual_segment_length = max(32, actual_segment_length)  # Mínimo 32

    # ============================================================
    # 2. WELCH PSD del activo
    # ============================================================
    freqs, psd = welch_psd(
        signal=returns,
        segment_length=actual_segment_length,
        overlap_fraction=0.5,
        fs=1.0,  # 1 sample/día
    )

    # ============================================================
    # 3. ENTROPÍA ESPECTRAL → RÉGIMEN
    # ============================================================
    se_norm, regime = spectral_entropy_normalized(
        psd=psd,
        threshold_low=entropy_threshold_low,
        threshold_high=entropy_threshold_high,
    )

    # ============================================================
    # 4. CICLO DOMINANTE + FASE
    # ============================================================
    cycle_info = detect_dominant_cycle(
        signal=returns,
        freqs=freqs,
        psd=psd,
        fs=1.0,
    )

    # ============================================================
    # 5. COHERENCIA CRUZADA CON BENCHMARK
    # ============================================================
    try:
        benchmark_data = get_financial_data(benchmark, period)
        benchmark_returns = benchmark_data["returns"]

        # Alinear longitudes
        min_len = min(len(returns), len(benchmark_returns))
        returns_aligned = returns[:min_len]
        benchmark_returns_aligned = benchmark_returns[:min_len]

        coh_segment = min(actual_segment_length, min_len)
        coh_segment = 2 ** int(np.floor(np.log2(coh_segment)))
        coh_segment = max(32, coh_segment)

        coh_freqs, coherence = spectral_coherence(
            signal_a=returns_aligned,
            signal_b=benchmark_returns_aligned,
            segment_length=coh_segment,
            overlap_fraction=0.5,
            fs=1.0,
        )

        # Coherencia en la frecuencia del ciclo dominante
        if cycle_info["frequency"] > 0 and len(coh_freqs) > 0:
            freq_diff = np.abs(coh_freqs - cycle_info["frequency"])
            closest_idx = np.argmin(freq_diff)
            coherence_at_dominant = float(coherence[closest_idx])
        else:
            coherence_at_dominant = 0.0

        # Calcular régimen del benchmark
        _, benchmark_psd = welch_psd(
            signal=benchmark_returns_aligned,
            segment_length=coh_segment,
            overlap_fraction=0.5,
            fs=1.0,
        )
        _, benchmark_regime = spectral_entropy_normalized(
            psd=benchmark_psd,
            threshold_low=entropy_threshold_low,
            threshold_high=entropy_threshold_high,
        )

    except Exception:
        # Si falla el benchmark, continuar sin coherencia
        coh_freqs = freqs
        coherence = np.zeros_like(freqs)
        coherence_at_dominant = 0.0
        benchmark_regime = None

    # ============================================================
    # 6. FILTRADO POR BANDAS VÍA IFFT (tendencia)
    # ============================================================
    try:
        trend_component = extract_trend_component(
            signal=returns,
            dominant_freq_index=cycle_info["k_peak"],
            bandwidth=3,
            fs=1.0,
        )
        trend_list = trend_component.tolist()
    except Exception:
        trend_list = None

    # ============================================================
    # 7. FUNCIÓN DE DECISIÓN → SEÑAL DE INVERSIÓN
    # ============================================================
    decision = investment_decision(
        regime=regime,
        phase_pct=cycle_info["phase_pct"],
        confidence=cycle_info["energy_ratio"],
        coherence_at_dominant=coherence_at_dominant,
        benchmark_regime=benchmark_regime,
    )

    # ============================================================
    # CONSTRUIR RESPUESTA
    # ============================================================
    return {
        "ticker": ticker.upper(),
        "benchmark": benchmark,
        "period": period,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "data_points": len(returns),
        "time_series": {
            "dates": dates,
            "prices": prices.tolist(),
            "returns": returns.tolist(),
            "trend_component": trend_list,
        },
        "spectral": {
            "frequencies": freqs.tolist(),
            "psd": psd.tolist(),
            "dominant_frequency": cycle_info["frequency"],
            "dominant_period_days": cycle_info["period_days"],
            "dominant_k_peak": cycle_info["k_peak"],
        },
        "regime": {
            "entropy_normalized": se_norm,
            "regime": regime,
            "threshold_low": entropy_threshold_low,
            "threshold_high": entropy_threshold_high,
        },
        "coherence": {
            "frequencies": coh_freqs.tolist() if isinstance(coh_freqs, np.ndarray) else coh_freqs,
            "coherence": coherence.tolist() if isinstance(coherence, np.ndarray) else coherence,
            "coherence_at_dominant": coherence_at_dominant,
            "benchmark_ticker": benchmark,
            "benchmark_regime": benchmark_regime,
        },
        "cycle": {
            "period_days": cycle_info["period_days"],
            "frequency": cycle_info["frequency"],
            "phase_rad": cycle_info["phase_rad"],
            "phase_pct": cycle_info["phase_pct"],
            "energy_ratio": cycle_info["energy_ratio"],
        },
        "signal": decision,
    }
