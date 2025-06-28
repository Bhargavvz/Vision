# ui/renderer.py

import cv2
import numpy as np
from typing import List, Tuple
from config import AppConfig
from event_bus import EventBus
from font_engine.font_model import FontCharacter

class UIRenderer:
    """Responsible for drawing all visual elements onto the frame."""
    def __init__(self):
        self.current_frame = None
        self.hand_landmarks = None
        self.font_character = None # Will be set by main
        self.current_mode = "SMOOTHNESS" # Default
        self.smoothness_val = 0.0
        self.distortion_val = 0.0

        print("UIRenderer initialized.")
        EventBus.subscribe('frame_ready', self._update_frame)
        EventBus.subscribe('hand_landmarks_detected', self._update_landmarks)
        EventBus.subscribe('mode_changed', self._update_mode)
        EventBus.subscribe('smoothness_changed', lambda d: self._update_smoothness(d, add=True)) # Take delta, not final value
        EventBus.subscribe('distortion_changed', lambda d: self._update_distortion(d, add=True)) # Take delta, not final value
        # For initial values, we need a way to get them, maybe pass them during init or a separate event

    def set_font_character(self, character: FontCharacter):
        self.font_character = character

    def set_initial_parameters(self, smoothness: float, distortion: float, mode: str):
        self.smoothness_val = smoothness
        self.distortion_val = distortion
        self.current_mode = mode

    def _update_frame(self, frame: np.ndarray):
        self.current_frame = frame.copy()

    def _update_landmarks(self, landmarks: List[Tuple[int, int, float]] | None):
        self.hand_landmarks = landmarks

    def _update_mode(self, mode: str):
        self.current_mode = mode
    
    # These update methods should ideally receive the *final* value, not the delta.
    # The FontManipulator is responsible for the delta application and clamping.
    # Re-subscribing with final value is more robust.
    # For now, let's assume the delta is small enough or we adjust how this works.
    def _update_smoothness(self, delta: float, add: bool = False):
        if add: self.smoothness_val += delta
        # Else: self.smoothness_val = delta (if event passed final value)
        self.smoothness_val = max(AppConfig.SMOOTHNESS_MIN, min(AppConfig.SMOOTHNESS_MAX, self.smoothness_val))

    def _update_distortion(self, delta: float, add: bool = False):
        if add: self.distortion_val += delta
        # Else: self.distortion_val = delta
        self.distortion_val = max(AppConfig.DISTORTION_MIN, min(AppConfig.DISTORTION_MAX, self.distortion_val))

    def render_frame(self) -> np.ndarray | None:
        """Draws all elements onto the current frame and returns it."""
        if self.current_frame is None:
            return None

        display_frame = self.current_frame.copy()

        # 1. Draw Hand Landmarks (if any)
        # We need the HandTracker instance to draw. Best practice: Renderer should not depend on Tracker.
        # So, HandTracker should publish drawn frame, or Renderer redraws based on raw landmarks.
        # For simplicity here, let's assume HandTracker draws onto the frame it publishes.
        # OR: Pass mp_drawing and mp_hands to renderer for drawing.

        # Let's adjust: HandTracker publishes raw landmarks. Renderer needs to draw them.
        # This requires Renderer to have access to mp_drawing and mp_hands if we want to use MP's helper.
        # Alternatively, manually draw circles and lines. For production, manual drawing gives more control.
        if self.hand_landmarks:
            for i, (x, y, z) in enumerate(self.hand_landmarks):
                cv2.circle(display_frame, (x, y), AppConfig.LINE_THICKNESS, (0, 255, 0), -1) # Draw dots
                # Optionally draw lines for connections manually if not using MP's helper
                # e.g., cv2.line(display_frame, self.hand_landmarks[0][:2], self.hand_landmarks[1][:2], (0,0,255), 2)

        # 2. Draw Font Character
        if self.font_character:
            font_points = self.font_character.get_current_points()
            
            # Draw the 'K' by connecting its points (if it's a polygonal character)
            # For Bezier, you'd get the interpolated points from BezierCurve.get_curve_points
            for i in range(len(font_points) - 1):
                cv2.line(display_frame, font_points[i], font_points[i+1], 
                         AppConfig.FONT_COLOR, AppConfig.LINE_THICKNESS)
            
            # Example for drawing a closed shape if points define a polygon
            # if len(font_points) > 2:
            #     cv2.polylines(display_frame, [np.array(font_points)], True, AppConfig.FONT_COLOR, AppConfig.LINE_THICKNESS)
            if len(font_points) > 2:
                cv2.polylines(display_frame, [np.array(font_points)], isClosed=True, color=AppConfig.FONT_COLOR, thickness=AppConfig.LINE_THICKNESS)


        # 3. Draw UI Text
        cv2.putText(display_frame, f"MODE: {self.current_mode}", AppConfig.UI_STATUS_POS,
                    cv2.FONT_HERSHEY_SIMPLEX, AppConfig.UI_FONT_SCALE, AppConfig.UI_TEXT_COLOR, AppConfig.UI_FONT_THICKNESS)
        
        cv2.putText(display_frame, f"SMOOTHNESS: {self.smoothness_val:.1f}", AppConfig.UI_SMOOTHNESS_POS,
                    cv2.FONT_HERSHEY_SIMPLEX, AppConfig.UI_FONT_SCALE, AppConfig.UI_TEXT_COLOR, AppConfig.UI_FONT_THICKNESS)
        
        cv2.putText(display_frame, f"DISTORTION: {self.distortion_val:.1f}", AppConfig.UI_DISTORTION_POS,
                    cv2.FONT_HERSHEY_SIMPLEX, AppConfig.UI_FONT_SCALE, AppConfig.UI_TEXT_COLOR, AppConfig.UI_FONT_THICKNESS)

        return display_frame