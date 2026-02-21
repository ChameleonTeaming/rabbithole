import numpy as np
from utils.musical_notes import NoteConverter

class ChordDetector:
    def __init__(self):
        # 12 Notes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
        self.notes = NoteConverter.NOTES
        self.templates = self._generate_templates()

    def _generate_templates(self):
        """
        Creates binary templates for Major and Minor chords.
        """
        templates = {}
        for i, root_note in enumerate(self.notes):
            # Major (0, 4, 7)
            maj_vec = np.zeros(12)
            maj_vec[i] = 1
            maj_vec[(i + 4) % 12] = 1
            maj_vec[(i + 7) % 12] = 1
            templates[f"{root_note} Major"] = maj_vec / np.linalg.norm(maj_vec) # Normalize
            
            # Minor (0, 3, 7)
            min_vec = np.zeros(12)
            min_vec[i] = 1
            min_vec[(i + 3) % 12] = 1
            min_vec[(i + 7) % 12] = 1
            templates[f"{root_note} Minor"] = min_vec / np.linalg.norm(min_vec) # Normalize
            
        return templates

    def detect(self, frequencies, magnitudes):
        """
        Analyzes spectrum to find the most likely chord using optimized numpy operations.
        """
        # Filter out silence/noise
        mask = (magnitudes > 50) & (frequencies > 20)
        valid_freqs = frequencies[mask]
        valid_mags = magnitudes[mask]
        
        if len(valid_freqs) == 0:
            return "Silence"

        # Vectorized MIDI Note Calculation
        # Formula: n = 12 * log2(f / 440) + 69
        midi_notes = 12 * np.log2(valid_freqs / 440.0) + 69
        note_indices = np.round(midi_notes).astype(int) % 12
        
        # Build Chroma Vector
        chroma = np.zeros(12)
        np.add.at(chroma, note_indices, valid_mags)
        
        # Normalize Chroma
        norm = np.linalg.norm(chroma)
        if norm == 0:
            return "Silence"
        chroma = chroma / norm

        # Match against templates
        best_chord = "Unknown"
        best_score = 0.0
        
        for chord_name, template in self.templates.items():
            score = np.dot(chroma, template)
            if score > best_score:
                best_score = score
                best_chord = chord_name
                
        # Threshold for confidence
        return best_chord if best_score > 0.8 else "No Chord"