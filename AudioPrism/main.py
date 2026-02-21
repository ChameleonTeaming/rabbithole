import pyaudio
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from colorama import Fore, Style, init
from engine.fft_analyzer import FFTAnalyzer
from engine.chord_detector import ChordDetector
from utils.musical_notes import NoteConverter

init(autoreset=True)

class AudioPrism:
    def __init__(self, chunk_size=2048, rate=44100):
        self.chunk_size = chunk_size
        self.rate = rate
        self.pa = pyaudio.PyAudio()
        self.analyzer = FFTAnalyzer(rate, chunk_size)
        self.chord_detector = ChordDetector()
        
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

    def start_cli_visualizer(self):
        print(f"{Fore.CYAN}AudioPrism Listening... Press Ctrl+C to stop.{Style.RESET_ALL}")
        try:
            while True:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                freqs, mags = self.analyzer.analyze(data)
                
                # Get the strongest frequency
                peak_f = self.analyzer.get_peak_frequency(freqs, mags)
                note = NoteConverter.freq_to_note(peak_f)
                
                # Detect Chord
                chord = self.chord_detector.detect(freqs, mags)
                
                # Create a simple ASCII bar chart for a few frequency bands
                self._draw_bars(mags, peak_f, note, chord)
                
        except KeyboardInterrupt:
            self.stop()

    def start_gui_visualizer(self):
        print(f"{Fore.CYAN}Launching AudioPrism GUI...{Style.RESET_ALL}")
        
        # Setup Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.canvas.manager.set_window_title('AudioPrism - Real-Time Spectrum Analyzer')
        ax.set_facecolor('black')
        fig.patch.set_facecolor('#1e1e1e')
        
        # Initial X/Y data
        line, = ax.plot([], [], color='#00ff00', lw=1.5)
        
        # Labels and Grid
        ax.set_ylim(0, 5000)
        ax.set_xlim(20, 4000) # Human voice/music range focus
        ax.set_xlabel('Frequency (Hz)', color='white')
        ax.set_ylabel('Magnitude', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.3)
        
        peak_text = ax.text(0.05, 0.9, '', transform=ax.transAxes, color='yellow', fontsize=12, fontweight='bold')
        note_text = ax.text(0.05, 0.85, '', transform=ax.transAxes, color='cyan', fontsize=14, fontweight='bold')
        chord_text = ax.text(0.05, 0.80, '', transform=ax.transAxes, color='magenta', fontsize=16, fontweight='bold')

        def update(frame):
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                freqs, mags = self.analyzer.analyze(data)
                
                # Filter to View Range
                mask = freqs <= 4000
                display_freqs = freqs[mask]
                display_mags = mags[mask]

                # Update Line
                line.set_data(display_freqs, display_mags)
                
                # Peak Info
                peak_f = self.analyzer.get_peak_frequency(freqs, mags)
                note = NoteConverter.freq_to_note(peak_f)
                
                # Detect Chord
                chord = self.chord_detector.detect(freqs, mags)
                
                if peak_f > 0:
                    peak_text.set_text(f"Peak Freq: {peak_f:.1f} Hz")
                    note_text.set_text(f"Note: {note}")
                    chord_text.set_text(f"Chord: {chord}")
                
                return line, peak_text, note_text, chord_text
            except Exception as e:
                print(e)
                return line,

        ani = FuncAnimation(fig, update, blit=True, interval=20)
        plt.show()
        self.stop()

    def _draw_bars(self, magnitudes, peak_f, note, chord):
        # We'll visualize 50 bands from 0Hz to 4000Hz
        num_bars = 50
        max_freq = 4000
        step = max_freq // num_bars
        
        # Clear screen (approximate)
        sys.stdout.write("\033[H")
        
        display = []
        for i in range(num_bars):
            f_start = i * step
            f_end = (i + 1) * step
            # Find max magnitude in this band
            mask = (magnitudes >= f_start) & (magnitudes < f_end)
            band_val = np.mean(magnitudes[mask]) if any(mask) else 0
            
            # Scale bar height
            bar_h = int(min(band_val / 500, 20)) 
            char = "█" if bar_h > 0 else " "
            color = Fore.GREEN if f_start < 500 else (Fore.YELLOW if f_start < 2000 else Fore.RED)
            display.append(f"{color}{char * bar_h}")

        # Print Peak Info
        header = f"{Fore.MAGENTA}Peak: {peak_f:7.1f} Hz | Note: {Fore.WHITE}{Style.BRIGHT}{note:4}{Style.RESET_ALL} | Chord: {Fore.MAGENTA}{Style.BRIGHT}{chord}"
        sys.stdout.write(header + "\n")
        
        for i, bar in enumerate(display):
             sys.stdout.write(bar + "\n")
        
        sys.stdout.flush()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        print("\nAudioPrism Terminated.")

if __name__ == "__main__":
    prism = AudioPrism()
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        prism.start_gui_visualizer()
    else:
        print("Run with '--gui' for graphical mode.")
        prism.start_cli_visualizer()
