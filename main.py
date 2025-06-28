# main.py

import cv2
import sys
import time

from config import AppConfig
from exceptions import CameraError, GestureRecognitionError, FontManipulationError
from event_bus import EventBus

# Import modules
from vision.camera_manager import CameraManager
from vision.hand_tracker import HandTracker
from vision.gesture_recognizer import GestureRecognizer
from font_engine.font_model import load_default_k_character
from font_engine.font_manipulator import FontManipulator
from ui.renderer import UIRenderer

class Application:
    """Main application class to manage the lifecycle and interaction of components."""
    def __init__(self):
        self.camera_manager = CameraManager()
        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer()
        
        # Load initial font character
        self.font_character = load_default_k_character()
        self.font_manipulator = FontManipulator(self.font_character)

        self.renderer = UIRenderer()
        self.renderer.set_font_character(self.font_character)
        self.renderer.set_initial_parameters(
            self.font_manipulator.get_current_smoothness(),
            self.font_manipulator.get_current_distortion(),
            self.gesture_recognizer.current_mode # Initial mode
        )

        self.running = False

    def _setup_event_listeners(self):
        """Sets up all event listeners for the application."""
        # This is a good practice to centralize event subscriptions
        # For now, they are handled in each component's __init__
        pass

    def run(self):
        """Starts the main application loop."""
        try:
            self.camera_manager.start()
            self.running = True
            print("Application started. Press 'q' to quit.")

            while self.running:
                # The main loop is now leaner. The rendering logic is self-contained in the renderer
                # and triggered by events. We just need to display the final frame.
                display_frame = self.renderer.render_frame()

                if display_frame is not None:
                    cv2.imshow(AppConfig.WINDOW_NAME, display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('r'):
                    # Reset font and parameters
                    self.font_character.reset_to_original()
                    if self.font_manipulator:
                        self.font_manipulator.smoothness_value = 0.0
                        self.font_manipulator.distortion_value = 0.0
                    # We should also reset the UI display values
                    if self.renderer:
                        self.renderer.set_initial_parameters(0.0, 0.0, self.gesture_recognizer.current_mode)
                    print("Font character and parameters reset to original.")


        except CameraError as e:
            print(f"FATAL ERROR: Camera initialization failed: {e}", file=sys.stderr)
            self._shutdown()
            sys.exit(1)
        except (GestureRecognitionError, FontManipulationError) as e:
            print(f"RUNTIME ERROR: {e}", file=sys.stderr)
            # Depending on severity, you might choose to continue or shut down
            # For now, we'll continue but log the error
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            self._shutdown()
            sys.exit(1)
        finally:
            self._shutdown()

    def _shutdown(self):
        """Performs graceful shutdown of all components."""
        print("Shutting down application...")
        self.camera_manager.stop()
        self.hand_tracker.close()
        cv2.destroyAllWindows()
        print("Application shut down cleanly.")

if __name__ == "__main__":
    app = Application()
    app.run()