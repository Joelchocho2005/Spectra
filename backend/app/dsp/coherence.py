"""
SPECTRA — Coherencia Espectral Cruzada y Densidad Espectral Cruzada (CSD)
★ IMPLEMENTACIÓN PROPIA

Calcula la coherencia espectral entre el activo objetivo y su benchmark
para detectar si los ciclos de ambos están sincronizados.

Fórmulas:
    CSD:  S_AB[k] = (1/K) · Σ_i R*_A,i[k] · R_B,i[k]
    Coherencia:  Coh_AB[k] = |S_AB[k]|² / (P_A[k] · P_B[k])

Coh_AB[k] ∈ [0, 1] donde 1 = sincronización perfecta en frecuencia k.

Referencia:
    Wiener-Khinchin theorem aplicado a correlación cruzada.
"""

import numpy as np
from typing import Tuple
from .welch import hanning_window


def cross_spectral_density(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    segment_length: int = 256,
    overlap_fraction: float = 0.5,
    fs: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcula la densidad espectral cruzada (CSD), la PSD de A y la PSD de B
    usando segmentos de Welch.
    ★ Implementación propia.

    Parameters
    ----------
    signal_a : np.ndarray
        Señal del activo objetivo (retornos logarítmicos).
    signal_b : np.ndarray
        Señal del benchmark (retornos logarítmicos).
    segment_length : int
        Longitud del segmento de Welch.
    overlap_fraction : float
        Fracción de solapamiento (default 0.5).
    fs : float
        Frecuencia de muestreo.

    Returns
    -------
    freqs : np.ndarray
        Vector de frecuencias.
    csd : np.ndarray
        Densidad espectral cruzada (compleja).
    psd_a : np.ndarray
        PSD del activo A.
    psd_b : np.ndarray
        PSD del activo B.
    """
    # Asegurar que ambas señales tengan la misma longitud
    min_len = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:min_len]
    signal_b = signal_b[:min_len]

    N = min_len
    M = segment_length

    if N < M:
        raise ValueError(
            f"Las señales (N={N}) son más cortas que el tamaño de segmento (M={M})."
        )

    # Ventana de Hanning propia
    window = hanning_window(M)
    U = np.sum(window ** 2) / M

    hop = int(M * (1.0 - overlap_fraction))
    num_segments = (N - M) // hop + 1

    if num_segments < 1:
        num_segments = 1

    num_freq_bins = M // 2 + 1

    csd_accum = np.zeros(num_freq_bins, dtype=complex)
    psd_a_accum = np.zeros(num_freq_bins)
    psd_b_accum = np.zeros(num_freq_bins)

    for i in range(num_segments):
        start = i * hop
        end = start + M

        # Segmentos ventaneados
        seg_a = signal_a[start:end] * window
        seg_b = signal_b[start:end] * window

        # DFT de cada segmento (caja negra: numpy.fft.fft)
        fft_a = np.fft.fft(seg_a, n=M)[:num_freq_bins]
        fft_b = np.fft.fft(seg_b, n=M)[:num_freq_bins]

        # CSD: conjugado(A) · B
        csd_accum += np.conj(fft_a) * fft_b

        # PSD individuales: |X|²
        psd_a_accum += np.abs(fft_a) ** 2
        psd_b_accum += np.abs(fft_b) ** 2

    # Normalizar por número de segmentos y factor de ventana
    scale = 1.0 / (num_segments * M * U)
    csd = csd_accum * scale
    psd_a = psd_a_accum * scale
    psd_b = psd_b_accum * scale

    freqs = np.fft.rfftfreq(M, d=1.0 / fs)

    return freqs, csd, psd_a, psd_b


def spectral_coherence(
    signal_a: np.ndarray,
    signal_b: np.ndarray,
    segment_length: int = 256,
    overlap_fraction: float = 0.5,
    fs: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula la función de coherencia espectral entre dos señales.
    ★ Implementación propia — no usa scipy.signal.coherence.

    Fórmula:
        Coh_AB[k] = |S_AB[k]|² / (P_A[k] · P_B[k])

    Parameters
    ----------
    signal_a : np.ndarray
        Señal del activo objetivo.
    signal_b : np.ndarray
        Señal del benchmark.
    segment_length : int
        Longitud del segmento de Welch.
    overlap_fraction : float
        Fracción de solapamiento.
    fs : float
        Frecuencia de muestreo.

    Returns
    -------
    freqs : np.ndarray
        Vector de frecuencias.
    coherence : np.ndarray
        Coherencia espectral en cada frecuencia (0 a 1).
    """
    freqs, csd, psd_a, psd_b = cross_spectral_density(
        signal_a, signal_b, segment_length, overlap_fraction, fs
    )

    # Evitar división por cero
    denominator = psd_a * psd_b
    denominator = np.where(denominator > 0, denominator, 1e-30)

    # Coherencia: |CSD|² / (PSD_A · PSD_B)
    coherence = np.abs(csd) ** 2 / denominator

    # Clamp a [0, 1]
    coherence = np.clip(coherence, 0.0, 1.0)

    return freqs, coherence
