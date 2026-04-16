"""
SPECTRA — Servicio de Datos Financieros

Descarga datos OHLCV de Yahoo Finance (yfinance) y calcula
los retornos logarítmicos del activo.

r[n] = ln(P[n] / P[n-1]),  n = 1, 2, ..., N-1
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Tuple, Dict
from datetime import datetime


def download_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Descarga datos OHLCV de Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Símbolo bursátil (ej. AAPL, BTC-USD, SPY).
    period : str
        Ventana temporal (3mo, 6mo, 1y, 2y, 5y).

    Returns
    -------
    pd.DataFrame
        DataFrame con columnas Open, High, Low, Close, Adj Close, Volume.

    Raises
    ------
    ValueError
        Si el ticker no devuelve datos.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if df.empty:
        raise ValueError(
            f"No se encontraron datos para el ticker '{ticker}' "
            f"en el período '{period}'. Verifique que el símbolo sea válido."
        )

    return df


def compute_log_returns(prices: np.ndarray) -> np.ndarray:
    """
    Calcula los retornos logarítmicos de una serie de precios.

    Fórmula:
        r[n] = ln(P[n] / P[n-1]),  n = 1, 2, ..., N-1

    Los retornos logarítmicos se usan porque:
    1. La serie r[n] es aproximadamente estacionaria (requerido para DFT)
    2. r[n] puede modelarse como salida de un sistema LTI

    Parameters
    ----------
    prices : np.ndarray
        Vector de precios de cierre ajustados.

    Returns
    -------
    np.ndarray
        Vector de retornos logarítmicos (N-1 valores).
    """
    prices = np.array(prices, dtype=float)
    # Evitar log(0) o log(negativo)
    prices = np.maximum(prices, 1e-10)
    log_returns = np.diff(np.log(prices))
    return log_returns


def get_financial_data(ticker: str, period: str = "1y") -> Dict:
    """
    Obtiene datos financieros completos: precios, fechas y retornos.

    Parameters
    ----------
    ticker : str
        Símbolo bursátil.
    period : str
        Ventana temporal.

    Returns
    -------
    dict con:
        - dates : list[str] — Fechas en formato ISO
        - prices : np.ndarray — Precios de cierre
        - returns : np.ndarray — Retornos logarítmicos
        - df : pd.DataFrame — DataFrame original
    """
    df = download_data(ticker, period)

    # Usar precio de cierre
    prices = df["Close"].values.astype(float)
    dates = [d.strftime("%Y-%m-%d") for d in df.index]

    # Retornos logarítmicos
    log_returns = compute_log_returns(prices)

    # Las fechas de retornos empiezan desde el segundo día
    return_dates = dates[1:]

    return {
        "dates": dates,
        "return_dates": return_dates,
        "prices": prices,
        "returns": log_returns,
        "df": df,
    }
