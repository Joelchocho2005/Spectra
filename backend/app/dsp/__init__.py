# SPECTRA DSP Engine — Implementación propia de algoritmos de procesamiento de señales
# Todos los módulos en este paquete son implementación manual del equipo (★)
# Solo se usa numpy.fft.fft como caja negra para la FFT base

from .welch import welch_psd
from .spectral_entropy import spectral_entropy_normalized
from .coherence import spectral_coherence
from .bandpass_filter import bandpass_filter_ifft
from .cycle_detector import detect_dominant_cycle
from .decision import investment_decision
