import matplotlib as mpl


def psd(u, sr, nfft):
    """
    Helper function to compute the power spectral density (PSD) of a signal.

    Parameters
    ----------
    u : array_like
        The signal to compute the PSD of.
    sr : float
         The sample rate of `u`.
    nfft : The number of points to use in computing the fft.

    Returns
    -------
    p : array_like
        The power in the signal `u` as a function of frequency (units
        of u squared/units of sr)
    f : array_like
        Frequency (same units as sr).
    """
    p, f = mpl.mlab.psd(
        u, nfft, sr, detrend=mpl.pylab.detrend_linear, noverlap=nfft / 2)
    return f[1:], p[1:]


def coh(u1, u2, sr, nfft):
    """
    Helper function to compute the coherence between two signals.

    Parameters
    ----------
    u1 : array_like
        Signal 1.
    u2 : array_like
        Signal 2.
    sr : float
         The sample rate of `u`.
    nfft : The number of points to use in computing the fft.

    Returns
    -------
    p : array_like
        The coherence between the two signal (no units) as a function
        of frequency.
    f : array_like
        Frequency (same units as sr).
    """
    p, f = mpl.mlab.cohere(u1, u2, nfft, sr,
                           detrend=mpl.pylab.detrend_linear,
                           noverlap=nfft / 2, scale_by_freq=False)
    return f[1:], p[1:]
