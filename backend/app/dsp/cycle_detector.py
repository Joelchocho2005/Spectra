"""
SPECTRA — Detector de Fase del Ciclo Dominante
★ IMPLEMENTACIÓN PROPIA

Identifica el ciclo dominante del activo a partir de la PSD e infiere
la fase actual del precio dentro de ese ciclo.

Fórmulas:
    k_peak = argmax P_Welch[k]  (excluyendo DC)
    T_dom = N / (k_peak · Fs)   (período en días de trading)
    φ_rad = angle(R[k_peak]) = atan2(Im(R[k_peak]), Re(R[k_peak]))
    φ_pct = (φ_rad + π) / (2π) · 100%  (normalizado a [0, 100%])
"""

import numpy as np
from typing import Dict


def detect_dominant_cycle(
    signal: np.ndarray,
    freqs: np.ndarray,
    psd: np.ndarray,
    fs: float = 1.0,
) -> Dict:
    """
    Detecta el ciclo dominante y su fase actual en la señal.
    ★ Implementación propia.

    Parameters
    ----------
    signal : np.ndarray
        Señal original en el dominio del tiempo (retornos logarítmicos).
    freqs : np.ndarray
        Vector de frecuencias de la PSD (salida de welch_psd).
    psd : np.ndarray
        Densidad de potencia espectral (salida de welch_psd).
    fs : float
        Frecuencia de muestreo (1.0 para datos diarios).

    Returns
    -------
    dict con:
        - k_peak : int — Índice del ciclo dominante
        - frequency : float — Frecuencia del ciclo dominante
        - period_days : float — Período en días de trading
        - phase_rad : float — Fase en radianes (-π a π)
        - phase_pct : float — Fase normalizada (0 a 100%)
        - energy_ratio : float — Energía relativa del ciclo dominante (confianza)
    """
    # Excluir DC (k=0) para encontrar el pico
    psd_no_dc = psd[1:].copy()
    freqs_no_dc = freqs[1:]

    if len(psd_no_dc) == 0:
        return _empty_result()

    # k_peak: índice del máximo de la PSD (excluyendo DC)
    k_peak_relative = np.argmax(psd_no_dc)
    k_peak = k_peak_relative + 1  # +1 porque excluimos DC

    # Frecuencia del ciclo dominante
    dominant_freq = freqs[k_peak]

    # Período en días de trading: T_dom = 1 / f_peak
    if dominant_freq > 0:
        period_days = 1.0 / dominant_freq
    else:
        period_days = float('inf')

    # Calcular la DFT de la señal completa para obtener la fase
    N = len(signal)
    R = np.fft.fft(signal)

    # Mapear k_peak de la PSD de Welch al índice correspondiente en la DFT completa
    # La frecuencia del pico es dominant_freq, que corresponde a k = dominant_freq * N / fs
    k_full = int(round(dominant_freq * N / fs))
    k_full = max(1, min(k_full, N // 2 - 1))  # Clamp

    # Fase del coeficiente DFT en el ciclo dominante
    phase_rad = np.angle(R[k_full])  # atan2(Im, Re)

    # Normalizar fase a [0, 100%]
    phase_pct = (phase_rad + np.pi) / (2.0 * np.pi) * 100.0

    # Energía relativa del ciclo dominante (confianza espectral)
    # E_dom / E_total
    total_energy = np.sum(psd[1:])  # Excluir DC
    if total_energy > 0:
        # Tomar una banda alrededor del pico (±2 bins)
        k_start = max(1, k_peak - 2)
        k_end = min(len(psd) - 1, k_peak + 2)
        dominant_energy = np.sum(psd[k_start : k_end + 1])
        energy_ratio = dominant_energy / total_energy
    else:
        energy_ratio = 0.0

    return {
        "k_peak": int(k_peak),
        "frequency": float(dominant_freq),
        "period_days": float(period_days),
        "phase_rad": float(phase_rad),
        "phase_pct": float(phase_pct),
        "energy_ratio": float(min(energy_ratio, 1.0)),
    }


def _empty_result() -> Dict:
    """Resultado vacío cuando no se puede detectar un ciclo."""
    return {
        "k_peak": 0,
        "frequency": 0.0,
        "period_days": float('inf'),
        "phase_rad": 0.0,
        "phase_pct": 50.0,
        "energy_ratio": 0.0,
    }
