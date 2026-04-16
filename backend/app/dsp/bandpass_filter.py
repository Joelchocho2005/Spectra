"""
SPECTRA — Filtrado por Bandas vía IFFT
★ IMPLEMENTACIÓN PROPIA

Implementa un filtro pasa-banda ideal en el dominio de la frecuencia
y reconstruye la señal filtrada mediante la IFFT.

Esto implementa la convolución circular en el dominio del tiempo
como un producto en el dominio de la frecuencia:

    R_filtrado[k] = R[k] · H[k]

    H[k] = 1  si k ∈ [k_low, k_high] ∪ [N-k_high, N-k_low]
    H[k] = 0  en caso contrario

    r_trend[n] = IFFT(R_filtrado)[n]
"""

import numpy as np
from typing import Tuple, Optional


def bandpass_filter_ifft(
    signal: np.ndarray,
    k_low: int,
    k_high: int,
    fs: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Aplica un filtro pasa-banda ideal en el dominio de la frecuencia
    y reconstruye la señal filtrada por IFFT.
    ★ Implementación propia.

    Parameters
    ----------
    signal : np.ndarray
        Señal de entrada en el dominio del tiempo.
    k_low : int
        Índice de frecuencia inferior de la banda (inclusive).
    k_high : int
        Índice de frecuencia superior de la banda (inclusive).
    fs : float
        Frecuencia de muestreo.

    Returns
    -------
    filtered_signal : np.ndarray
        Señal filtrada en el dominio del tiempo (parte real).
    H : np.ndarray
        Máscara del filtro en el dominio de la frecuencia.
    """
    N = len(signal)

    # DFT de la señal (caja negra: numpy.fft.fft)
    R = np.fft.fft(signal)

    # Construir máscara del filtro pasa-banda ideal
    H = np.zeros(N, dtype=complex)

    # Banda positiva: [k_low, k_high]
    k_low_clamped = max(0, k_low)
    k_high_clamped = min(k_high, N // 2)
    H[k_low_clamped : k_high_clamped + 1] = 1.0

    # Banda negativa (simetría hermítica para señales reales):
    # [N - k_high, N - k_low]
    H[N - k_high_clamped : N - k_low_clamped + 1] = 1.0

    # Aplicar filtro en dominio de frecuencia (producto = convolución en tiempo)
    R_filtered = R * H

    # Reconstruir señal filtrada por IFFT (caja negra: numpy.fft.ifft)
    filtered_signal = np.real(np.fft.ifft(R_filtered))

    return filtered_signal, H


def extract_trend_component(
    signal: np.ndarray,
    dominant_freq_index: int,
    bandwidth: int = 3,
    fs: float = 1.0,
) -> np.ndarray:
    """
    Extrae la componente de tendencia centrada en el ciclo dominante.

    Parameters
    ----------
    signal : np.ndarray
        Señal de retornos logarítmicos.
    dominant_freq_index : int
        Índice k del ciclo dominante (argmax de la PSD).
    bandwidth : int
        Semi-ancho de banda alrededor del ciclo dominante.
    fs : float
        Frecuencia de muestreo.

    Returns
    -------
    trend : np.ndarray
        Componente de tendencia filtrada.
    """
    k_low = max(1, dominant_freq_index - bandwidth)
    k_high = dominant_freq_index + bandwidth

    trend, _ = bandpass_filter_ifft(signal, k_low, k_high, fs)
    return trend
