# font_engine/font_model.py

from typing import List, Tuple
import numpy as np

class FontCharacter:
    """Represents a single character with its original and current editable outline."""
    def __init__(self, character: str, original_points: List[Tuple[int, int]]):
        self.character = character
        self._original_points = [np.array(p) for p in original_points] # Store as NumPy arrays
        self._current_points = list(self._original_points) # Editable copy

    def get_current_points(self) -> List[Tuple[int, int]]:
        """Returns the current state of the character's outline points as integer tuples."""
        return [tuple(p.astype(int)) for p in self._current_points]

    def reset_to_original(self):
        """Resets the character to its original shape."""
        self._current_points = list(self._original_points)

    def update_points(self, new_points: List[Tuple[int, int]]):
        """Updates the character's outline points."""
        self._current_points = [np.array(p) for p in new_points]
    
    def get_center(self) -> Tuple[int, int]:
        """Calculates the approximate center of the character."""
        if not self._current_points:
            return (0,0)
        
        x_coords = [p[0] for p in self._current_points]
        y_coords = [p[1] for p in self._current_points]
        return (int(np.mean(x_coords)), int(np.mean(y_coords)))


# Example: A simple 'K' character definition for demonstration
# In a real system, you'd load this from a font file (e.g., via FontTools)
def load_default_k_character() -> FontCharacter:
    """
    Loads a default 'K' character with a simple polygon representation.
    For production, this would involve parsing vector outlines.
    """
    # Define points that roughly form a 'K'
    # These would be control points for Bezier curves in a real font
    k_outline_points = [
        (100, 100), (120, 100), (120, 180), (200, 100), (220, 100), 
        (140, 200), (220, 300), (200, 300), (120, 220), (100, 300)
    ]
    return FontCharacter('K', k_outline_points)