Fourier Deconvolution
============================

.. _nid_fft_deconv:

Problem description
---------------------
The convolution that links the **impulse response** :math:`h(z)` to the
*logarithmic time-constant spectrum* :math:`R(\zeta)`

.. math::

   h(z)\;=\;\bigl(R \;\ast\; w_z\bigr)(z)
        \;=\;\int_{-\infty}^{\infty}
               R(\zeta)\,
               e^{\,z-\zeta-\exp(z-\zeta)}
               \,\mathrm{d}\zeta           

turns into a **simple product** in the Fourier domain:

.. math::

   \mathcal{F}\{h\}(\Phi)
   \;=\;
   V(\Phi)\,W(\Phi),

where

* :math:`\mathcal{F}\{f\}` denotes the Fourier transform of function :math:`f`,
* :math:`V(\Phi) = \mathcal{F}\{R\}(\Phi)`, is the Fourier transform of the
  *logarithmic time-constant spectrum* :math:`R(\zeta)`,
* :math:`W(\Phi) = \mathcal{F}\{w_z\}(\Phi)`, is the Fourier transform of the
  kernel :math:`w_z(z)`.

With measured data the recorded signal contains noise,

.. math::

   m(z)=h(z)+n(z) \;\Longrightarrow\;
   M(\Phi)=H(\Phi)+N(\Phi).

Division by :math:`W(\Phi)` therefore yields

.. math::

   V'(\Phi)
     \;=\;
   \frac{M(\Phi)}{W(\Phi)}
     \;=\;
   V(\Phi)
   \;+\;
   \frac{N(\Phi)}{W(\Phi)}.

Whenever :math:`|W(\Phi)|` approaches zero the noise term explodes; **high-
frequency whitening** is unavoidable.  Practical NID hence applies a
frequency-domain *window* that suppresses harmful bands before the inverse
FFT reconstructs :math:`R(\zeta)`.

**Padding**

Because the FFT assumes circular convolution, the impulse response is
normally **zero-padded** to at least twice its original length.  Padding
helps to avoid wrap-around artefacts and to match the length demanded by
the chosen window function.

.. _nid_freq_windows:

Frequency-domain windows
------------------------
Let the filtered spectrum be

.. math::

   V_\text{filtered}(\Phi)
     \;=\;
   V'(\Phi)\,F(\Phi),

with the window

.. math::

   F(\Phi)=
   \begin{cases}
     0,                       & |\Phi|>\Phi_c,\\
     F_\text{window}(\Phi),   & |\Phi|\le\Phi_c,
   \end{cases}

where :math:`\Phi_c` is the cut-off.  Below are the most common window
profiles (index :math:`n=0\dots N_W` spans the non-zero part).

* **Rectangular**

  .. math::

     F_\text{Rect}[n]=1.

* **Hann**

  .. math::

     F_\text{Hann}[n]
       \;=\;
     \sin^2\!\Bigl(\pi n/N_W\Bigr).

* **Gaussian** – width controlled by :math:`\sigma\le0.5`

  .. math::

     F_\text{Gauss}[n]
       \;=\;
     \exp\!\Bigl[
       -\tfrac12
       \bigl(\tfrac{n-N_W/2}{\sigma\,N_W/2}\bigr)^2
     \Bigr].

* **Nuttall** – four-term cosine series

  .. math::

     F_\text{Nuttall}[n] =
        0.355768
      \;-\;0.487396\cos\Bigl(\tfrac{2\pi n}{N_W}\Bigr)
      \;+\;0.144232\cos\Bigl(\tfrac{4\pi n}{N_W}\Bigr)
      \;-\;0.012604\cos\Bigl(\tfrac{6\pi n}{N_W}\Bigr).

* **Fermi–Dirac** (no finite :math:`\Phi_c`)

  .. math::

     F_\text{Fermi}(\Phi)
       \;=\;
     \frac{1}{
       \exp\!\bigl(\tfrac{|\Phi|-\mu}{\beta}\bigr)+1
     }
     \;=\;
     \frac{
       \exp\!\bigl[-(|\Phi|-\mu)/\beta\bigr]
     }{
       1+\exp\!\bigl[-(|\Phi|-\mu)/\beta\bigr]
     }.

  Parameters

  * :math:`\mu`  – half-width of the transition band,
  * :math:`\beta` – slope (small :math:`\beta` ⇒ sharper edge).

