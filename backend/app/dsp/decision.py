"""
SPECTRA — Función de Decisión de Inversión
★ IMPLEMENTACIÓN PROPIA

Combina los resultados del análisis espectral en una señal de inversión
accionable: COMPRAR / VENDER / ESPERAR.

Reglas de decisión (tabla §2.4 de la propuesta técnica):

# | Condición                                           | Señal
--|------------------------------------------------------|-------
1 | TENDENCIAL ∧ Fase < 50% ∧ Confianza > 60%           | COMPRAR
2 | TENDENCIAL ∧ Fase > 70% ∧ Confianza > 60%           | VENDER
3 | REVERSIVO  ∧ Fase > 80%                              | COMPRAR
4 | Coherencia(f_dom) > 0.75 ∧ Benchmark TENDENCIAL     | COMPRAR (reforzado)
5 | RUIDOSO (cualquier fase)                              | ESPERAR
6 | Confianza < 30% (cualquier régimen)                   | ESPERAR
"""

from typing import Dict, Optional


def investment_decision(
    regime: str,
    phase_pct: float,
    confidence: float,
    coherence_at_dominant: float = 0.0,
    benchmark_regime: Optional[str] = None,
) -> Dict:
    """
    Genera la señal de inversión basada en el análisis espectral.
    ★ Implementación propia.

    Parameters
    ----------
    regime : str
        Régimen detectado: "TENDENCIAL", "MEDIA-REVERSIVO" o "RUIDOSO".
    phase_pct : float
        Fase del ciclo dominante (0-100%).
    confidence : float
        Confianza espectral = energía relativa del ciclo dominante (0-1).
    coherence_at_dominant : float
        Coherencia espectral en la frecuencia del ciclo dominante (0-1).
    benchmark_regime : str, optional
        Régimen del benchmark (si fue calculado).

    Returns
    -------
    dict con:
        - signal : str — "COMPRAR", "VENDER" o "ESPERAR"
        - confidence_pct : float — Confianza como porcentaje (0-100%)
        - rule_applied : int — Número de la regla que se activó
        - explanation : str — Explicación técnica de la señal
        - reinforced : bool — Si la señal fue reforzada por coherencia con benchmark
    """
    confidence_pct = confidence * 100.0
    reinforced = False
    explanation = ""

    # Regla 6: Confianza baja (prioridad alta — anula todo)
    if confidence_pct < 30.0:
        return {
            "signal": "ESPERAR",
            "confidence_pct": round(confidence_pct, 1),
            "rule_applied": 6,
            "explanation": (
                f"Aunque se detectó un ciclo dominante, su energía relativa "
                f"es solo del {confidence_pct:.1f}%. La señal es débil y el "
                f"riesgo de falsa señal es alto. Se recomienda esperar."
            ),
            "reinforced": False,
        }

    # Regla 5: Régimen ruidoso
    if regime == "RUIDOSO":
        return {
            "signal": "ESPERAR",
            "confidence_pct": round(confidence_pct, 1),
            "rule_applied": 5,
            "explanation": (
                f"El mercado se encuentra en régimen RUIDOSO. No existe "
                f"estructura espectral explotable — la energía está distribuida "
                f"uniformemente en frecuencia. El precio se comporta como ruido. "
                f"Operar en esta condición es especulación sin base técnica."
            ),
            "reinforced": False,
        }

    # Regla 1: Tendencial + fase temprana + confianza alta → COMPRAR
    if regime == "TENDENCIAL" and phase_pct < 50.0 and confidence_pct > 60.0:
        signal = "COMPRAR"
        rule = 1
        explanation = (
            f"El activo está en régimen TENDENCIAL con un ciclo dominante bien "
            f"definido (confianza: {confidence_pct:.1f}%). Se encuentra en la primera "
            f"mitad del ciclo (fase: {phase_pct:.1f}%), lo que indica fase ascendente. "
            f"La estructura de frecuencia sugiere continuación de la tendencia."
        )

        # Verificar refuerzo por Regla 4
        if coherence_at_dominant > 0.75 and benchmark_regime == "TENDENCIAL":
            reinforced = True
            rule = 4
            explanation += (
                f" REFORZADO: El activo muestra alta coherencia espectral con el "
                f"mercado ({coherence_at_dominant:.2f}). El ciclo no es específico "
                f"del activo sino una tendencia de mercado amplio, lo que reduce el riesgo."
            )

        return {
            "signal": signal,
            "confidence_pct": round(confidence_pct, 1),
            "rule_applied": rule,
            "explanation": explanation,
            "reinforced": reinforced,
        }

    # Regla 2: Tendencial + fase madura → VENDER
    if regime == "TENDENCIAL" and phase_pct > 70.0 and confidence_pct > 60.0:
        return {
            "signal": "VENDER",
            "confidence_pct": round(confidence_pct, 1),
            "rule_applied": 2,
            "explanation": (
                f"El activo está en régimen TENDENCIAL pero el ciclo dominante "
                f"está maduro (fase: {phase_pct:.1f}%). La segunda mitad del ciclo "
                f"tiende a revertir. Momento de tomar ganancias. "
                f"Confianza espectral: {confidence_pct:.1f}%."
            ),
            "reinforced": False,
        }

    # Regla 3: Media-reversivo + fase alta → COMPRAR (mean reversion)
    if regime == "MEDIA-REVERSIVO" and phase_pct > 80.0:
        signal = "COMPRAR"
        rule = 3
        explanation = (
            f"El activo oscila alrededor de su media (régimen MEDIA-REVERSIVO). "
            f"La fase actual ({phase_pct:.1f}%) indica que el precio está en el "
            f"extremo del ciclo y se espera reversión. Se compra el rebote. "
            f"Confianza espectral: {confidence_pct:.1f}%."
        )

        # Verificar refuerzo por Regla 4
        if coherence_at_dominant > 0.75 and benchmark_regime == "TENDENCIAL":
            reinforced = True
            explanation += (
                f" REFORZADO por alta coherencia con el benchmark ({coherence_at_dominant:.2f})."
            )

        return {
            "signal": signal,
            "confidence_pct": round(confidence_pct, 1),
            "rule_applied": rule,
            "explanation": explanation,
            "reinforced": reinforced,
        }

    # Caso por defecto: condiciones no cubiertas → ESPERAR
    return {
        "signal": "ESPERAR",
        "confidence_pct": round(confidence_pct, 1),
        "rule_applied": 0,
        "explanation": (
            f"Las condiciones espectrales actuales (régimen: {regime}, "
            f"fase: {phase_pct:.1f}%, confianza: {confidence_pct:.1f}%) "
            f"no cumplen los criterios para una señal clara de COMPRAR o VENDER. "
            f"Se recomienda esperar a una configuración espectral más definida."
        ),
        "reinforced": False,
    }
