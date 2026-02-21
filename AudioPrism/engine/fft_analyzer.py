import numpy as np
from scipy.fft import rfft, rfftfreq

class FFTAnalyzer:
    def __init__(self, sample_rate=44100, chunk_size=2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        # Hanning window reduces spectral leakage
        self.window = np.hanning(chunk_size)

    def analyze(self, audio_data):
        """
        Performs FFT on audio chunk and returns (frequencies, magnitudes)
        """
        # Convert buffer to numpy array
        if isinstance(audio_data, bytes):
            audio_data = np.frombuffer(audio_data, dtype=np.int16)
        
        # Apply windowing
        windowed_data = audio_data * self.window
        
        # Perform Real FFT
        magnitudes = np.abs(rfft(windowed_data))
        frequencies = rfftfreq(self.chunk_size, 1 / self.sample_rate)
        
        return frequencies, magnitudes

    def get_peak_frequency(self, frequencies, magnitudes):
        """Finds the loudest frequency in the chunk."""
        idx = np.argmax(magnitudes)
        return frequencies[idx]
