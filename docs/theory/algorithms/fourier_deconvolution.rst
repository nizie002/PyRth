Fourier Deconvolution
======================

Fourier Deconvolution is one of the key methods in PyRth for calculating the time constant spectrum from thermal impedance measurements.

Algorithm Description
-----------------------------------

The Fourier deconvolution approach uses the frequency domain to solve the convolution integral that relates the time constant spectrum to the thermal impedance derivative. Key steps include:

1. Transform the impedance derivative to the frequency domain using FFT
2. Divide by the transfer function in the frequency domain
3. Apply a spectral filter to reduce noise amplification
4. Transform back to the time domain to obtain the time constant spectrum

Mathematical Formulation
--------------------------------------

The thermal impedance can be expressed as a convolution of the time constant spectrum :math:`R(\tau)` with a weight function :math:`w(t, \tau)`:

.. math::

    Z_{th}(t) = \int_{0}^{\infty} R(\tau) \cdot w(t, \tau) d\tau

The derivative with respect to logarithmic time is:

.. math::

    \frac{dZ_{th}}{d\ln(t)} = \int_{0}^{\infty} R(\tau) \cdot \frac{\partial w(t, \tau)}{\partial \ln(t)} d\tau

In the frequency domain, this becomes:

.. math::

    \mathcal{F}\left\{\frac{dZ_{th}}{d\ln(t)}\right\} = \mathcal{F}\{R(\tau)\} \cdot \mathcal{F}\left\{\frac{\partial w(t, \tau)}{\partial \ln(t)}\right\}

Thus, we can isolate the time constant spectrum:

.. math::

    \mathcal{F}\{R(\tau)\} = \frac{\mathcal{F}\left\{\frac{dZ_{th}}{d\ln(t)}\right\}}{\mathcal{F}\left\{\frac{\partial w(t, \tau)}{\partial \ln(t)}\right\}} \cdot \mathcal{F}\{Filter\}

Then, we apply the inverse Fourier transform:

.. math::

    R(\tau) = \mathcal{F}^{-1}\left\{\mathcal{F}\{R(\tau)\}\right\}

Implementation Details
-----------------------------------

In PyRth, the FFT deconvolution is implemented through these steps:

1. Calculate the FFT of the impedance derivative
2. Calculate the FFT of the weight function
3. Divide the FFT of the derivative by the FFT of the weight function
4. Apply a filter (e.g., Hann, Gauss, Fermi) to suppress high-frequency noise
5. Calculate the inverse FFT to obtain the time constant spectrum

The implementation is divided across several functions in the `transient_core.py` file:

- `fft_signal`: Calculates the Fourier transform of the impedance derivative
- `fft_weight`: Calculates the Fourier transform of the weight function
- `fft_time_spec`: Performs the deconvolution and applies the selected filter

Filter Options
----------------------------

PyRth provides several filter types for Fourier deconvolution:

- **Rectangular**: Simple rectangular window (no filtering)
- **Hann**: Standard Hann window, good general-purpose filter
- **Blackman-Harris**: Provides excellent sidelobe suppression
- **Nuttall**: Similar to Blackman-Harris with different coefficients
- **Gaussian**: Gaussian shaped filter with adjustable width
- **Fermi**: Fermi function filter with adjustable transition width

Code Example
--------------------------

.. code-block:: python

    # Calculate FFT of impedance derivative
    self.fft_idi = fftpack.fft(self.imp_deriv_interp)
    
    # Calculate FFT of weight function
    self.fft_wgt = fftpack.fft(self.trans_weight) * self.log_time_delta
    
    # Get filter based on selected type
    self.current_filter = flt.give_current_filter(
        self.filter_name, self.fft_freq, self.filter_range, self.filter_parameter
    )
    
    # Perform deconvolution and apply filter
    self.deconv_t = (self.fft_idi / self.fft_wgt) * self.current_filter
    
    # Transform back to time domain
    self.time_spec = np.real(fftpack.ifft(self.deconv_t))

Advantages and Limitations
----------------------------------------

**Advantages:**
- Fast computation through FFT algorithms
- Flexibility in filter selection to adjust noise sensitivity
- Simple interpretation in frequency domain

**Limitations:**
- Sensitive to noise at high frequencies
- Filter selection can significantly impact results
- May introduce artifacts if filter parameters are improperly chosen