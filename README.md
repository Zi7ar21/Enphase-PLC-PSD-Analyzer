# Enphase PLC PSD Analyzer

Turn your Enphase IQ Gateway into a oscilloscope and real-time spectrum analyzer Python script that computes and plots an FFT of samples from the Power Line Communication (PLC) Power Spectral Distribution (PSD) sampler at /stream/psd.

## Background

Ordinarily, a spectrum analysis of the PLC noise can be viewed at `https://enlighten.enphaseenergy.com/app/system_dashboard/sites/<SITE_ID>/plc-noise-detection` or by [https://support.enphase.com/s/article/checking-plc-noise-levels-using-the-enphase-installer-app](using the installer app), but it requires sending requests to Amazon Web Services to get the FFT back.

## Details

- I've only tested this on my Envoy IQ Gateway (part number `800-00555-r03`, software version `D8.2.4345 (3f3de0)`), so your milage may vary (and the PSD data may look different).
- It appears the ADC has a sample rate of 500 kHz (250 kHz bandwidth) and /stream/psd usually sends 57.5 milliseconds of data (28750 samples), probably centered around zero crossing, it's not clear why but sometimes less samples are returned.
- According to [https://support.enphase.com/s/question/0D53m00008qay3cCAA/how-to-interpret-the-stream-from-streampsd](this forum post), the units returned by /stream/psd are "arbitrary", but the scale looks nearly identical to that on the Enlighten System Dashboard (`https://enlighten.enphaseenergy.com/app/system_dashboard/sites/<SITE_ID>/plc-noise-detection`) which is "dBuV rms", so this is probably the same scale (though the FFT may be multiplied by a factor of 1/sqrt(2) or sqrt(2), but this script will plot the FFT as-is with no multiplication)
- Sometimes the buffer catches PLC signals, I'm not sure if the Envoy uses the same ADC to demod/decode them as it does for the PLC Noise Analysis.
