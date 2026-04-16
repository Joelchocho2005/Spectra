"""
SPECTRA — Estimador de Welch para Densidad de Potencia Espectral (PSD)
★ IMPLEMENTACIÓN PROPIA

Implementa el método de Welch para estimar la PSD de una señal discreta:
1. Genera ventana de Hanning manualmente (sin numpy.hanning)
2. Segmenta la señal con solapamiento del 50%
3. Aplica la DFT a cada segmento (usa numpy.fft.fft como caja negra)
4. Calcula el periodograma de cada segmento
5. Promedia los periodogramas para reducir varianza

Referencia:
    Welch, P.D. (1967). The Use of Fast Fourier Transform for the
    Estimation of Power Spectra. IEEE Trans. Audio Electroacoust., 15(2), 70–73.
"""

import numpy as np
from typing import Tuple


def hanning_window(M: int) -> np.ndarray:
    """
    Genera una ventana de Hanning de M puntos.
    ★ Implementación propia — no usa numpy.hanning ni scipy.signal.windows.

    Fórmula:
        w[m] = 0.5 * (1 - cos(2π·m / (M-1))),  m = 0, 1, ..., M-1

    Parameters
    ----------
    M : int
        Número de puntos de la ventana.

    Returns
    -------
    np.ndarray
        Vector de M puntos con los coeficientes de la ventana de Hanning.
    """
    m = np.arange(M)
    w = 0.5 * (1.0 - np.cos(2.0 * np.pi * m / (M - 1)))
    return w


def welch_psd(
    signal: np.ndarray,
    segment_length: int = 256,
    overlap_fraction: float = 0.5,
    fs: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estima la Densidad de Potencia Espectral (PSD) usando el método de Welch.
    ★ Implementación propia — no usa scipy.signal.welch.

    Pasos:
        1. Genera ventana de Hanning de segment_length puntos
        2. Segmenta la señal con solapamiento del 50%
        3. Aplica ventana a cada segmento
        4. Calcula la DFT de cada segmento ventaneado (numpy.fft.fft)
        5. Calcula el periodograma de cada segmento: (1/(M·U)) · |R_i[k]|²
        6. Promedia los periodogramas sobre todos los segmentos

    Parameters
    ----------
    signal : np.ndarray
        Señal de entrada (1-D). Típicamente retornos logarítmicos.
    segment_length : int
        Longitud M de cada segmento y de la ventana de Hanning.
        Debe ser potencia de 2 para eficiencia de la FFT.
    overlap_fraction : float
        Fracción de solapamiento entre segmentos. Default 0.5 (50%).
    fs : float
        Frecuencia de muestreo (samples/día para datos financieros).
        Default 1.0 (frecuencia normalizada).

    Returns
    -------
    freqs : np.ndarray
        Vector de frecuencias correspondientes a la PSD (solo parte positiva).
    psd : np.ndarray
        Estimación de la PSD en cada frecuencia.

    Raises
    ------
    ValueError
        Si la señal es más corta que segment_length.
    """
    N = len(signal)
    M = segment_length

    if N < M:
        raise ValueError(
            f"La señal (N={N}) es más corta que el tamaño de segmento (M={M}). "
            f"Reduzca el tamaño de segmento o use una ventana temporal más larga."
        )

    # Paso 1: Generar ventana de Hanning
    window = hanning_window(M)

    # Factor de corrección de energía de la ventana: U = (1/M) * Σ w²[m]
    U = np.sum(window ** 2) / M

    # Paso 2: Calcular el paso (hop) y el número de segmentos
    hop = int(M * (1.0 - overlap_fraction))
    num_segments = (N - M) // hop + 1

    if num_segments < 1:
        num_segments = 1

    # Número de bins de frecuencia (solo parte positiva del espectro)
    num_freq_bins = M // 2 + 1

    # Acumulador para los periodogramas
    psd_accum = np.zeros(num_freq_bins)

    # Pasos 3-5: Para cada segmento, aplicar ventana, DFT y periodograma
    for i in range(num_segments):
        start = i * hop
        end = start + M

        # Extraer segmento
        segment = signal[start:end]

        # Aplicar ventana de Hanning al segmento
        windowed_segment = segment * window

        # DFT del segmento ventaneado (usa numpy.fft.fft como caja negra)
        spectrum = np.fft.fft(windowed_segment, n=M)

        # Tomar solo la parte positiva del espectro (0 a N/2)
        spectrum_pos = spectrum[:num_freq_bins]

        # Periodograma del segmento: (1 / (M · U)) · |R_i[k]|²
        periodogram = (1.0 / (M * U)) * np.abs(spectrum_pos) ** 2

        # Compensar por la simetría del espectro (duplicar en bins no-DC y no-Nyquist)
        periodogram[1:-1] *= 2.0

        psd_accum += periodogram

    # Paso 6: Promediar sobre todos los segmentos
    psd = psd_accum / num_segments

    # Generar vector de frecuencias
    freqs = np.fft.rfftfreq(M, d=1.0 / fs)

    return freqs, psd
