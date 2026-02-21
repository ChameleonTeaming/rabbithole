import math

class NoteConverter:
    # A4 = 440Hz
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    @staticmethod
    def freq_to_note(freq):
        if freq <= 0:
            return "N/A"
        
        # Formula: n = 12 * log2(f / 440) + 69
        # where 69 is the MIDI note number for A4
        n = 12 * math.log2(freq / 440.0) + 69
        n = round(n)
        
        octave = (n // 12) - 1
        note_idx = n % 12
        return f"{NoteConverter.NOTES[note_idx]}{octave}"
