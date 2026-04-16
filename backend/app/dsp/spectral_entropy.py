"""
SPECTRA — Entropía Espectral Normalizada
★ IMPLEMENTACIÓN PROPIA

Calcula la entropía espectral normalizada de una PSD para clasificar el
régimen del mercado:
    - SE_norm < 0.45  →  TENDENCIAL  (energía concentrada)
    - SE_norm ∈ [0.45, 0.65]  →  MEDIA-REVERSIVO  (ciclos balanceados)
    - SE_norm > 0.65  →  RUIDOSO  (energía distribuida uniformemente)

La entropía de Shannon aplicada al espectro mide qué tan "plano" o
"concentrado" es el perfil energético de la señal.

Referencia:
    Shannon, C.E. (1948). A Mathematical Theory of Communication.
"""

import numpy as np
from typing import Tuple


# Umbrales de clasificación de régimen (calibrados heurísticamente)
THRESHOLD_TENDENCIAL = 0.45
THRESHOLD_RUIDOSO = 0.65


def spectral_entropy_normalized(
    psd: np.ndarray,
    threshold_low: float = THRESHOLD_TENDENCIAL,
    threshold_high: float = THRESHOLD_RUIDOSO,
) -> Tuple[float, str]:
    """
    Calcula la entropía espectral normalizada y clasifica el régimen de mercado.
    ★ Implementación propia.

    Pasos:
        1. Normalizar la PSD como distribución de probabilidad discreta:
           p[k] = P_Welch[k] / Σ P_Welch[k],  con Σ p[k] = 1
        2. Calcular la entropía de Shannon espectral:
           SE = −Σ p[k] · log₂(p[k])
        3. Normalizar respecto al máximo teórico (distribución uniforme):
           SE_norm = SE / log₂(N/2)

    Parameters
    ----------
    psd : np.ndarray
        Densidad de Potencia Espectral (salida de welch_psd).
        Solo la parte positiva del espectro (excluyendo DC si es posible).
    threshold_low : float
        Umbral inferior de entropía. SE_norm < threshold_low → TENDENCIAL.
    threshold_high : float
        Umbral superior de entropía. SE_norm > threshold_high → RUIDOSO.

    Returns
    -------
    se_norm : float
        Entropía espectral normalizada (0 a 1).
    regime : str
        Clasificación del régimen: "TENDENCIAL", "MEDIA-REVERSIVO" o "RUIDOSO".
    """
    # Excluir el componente DC (k=0) para el cálculo de entropía
    psd_no_dc = psd[1:]

    # Número de bins de frecuencia
    N_bins = len(psd_no_dc)

    if N_bins == 0:
        return 1.0, "RUIDOSO"

    # Paso 1: Normalizar como distribución de probabilidad
    total_energy = np.sum(psd_no_dc)
    if total_energy == 0:
        return 1.0, "RUIDOSO"

    p = psd_no_dc / total_energy

    # Paso 2: Entropía de Shannon espectral
    # Evitar log₂(0) reemplazando ceros con un valor muy pequeño
    p_safe = np.where(p > 0, p, 1e-30)
    se = -np.sum(p * np.log2(p_safe))

    # Paso 3: Normalizar
    se_max = np.log2(N_bins)
    if se_max == 0:
        return 1.0, "RUIDOSO"

    se_norm = se / se_max

    # Clasificar régimen
    if se_norm < threshold_low:
        regime = "TENDENCIAL"
    elif se_norm > threshold_high:
        regime = "RUIDOSO"
    else:
        regime = "MEDIA-REVERSIVO"

    return float(se_norm), regime
