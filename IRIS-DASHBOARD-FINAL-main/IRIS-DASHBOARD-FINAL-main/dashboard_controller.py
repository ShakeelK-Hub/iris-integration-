import time
import random
import PySimpleGUI as Sg
import threading
from view import DashboardView
from ws_client import DashboardWebSocketClient

class ButtonController:
    """Controls button text, color, and window background based on driver state."""
    def __init__(self, window, circle_progress):
        self.window = window
        self.circle_progress = circle_progress

    def update(self, driver_state):
        """Update button, progress, circle, and window colors based on driver state."""
        if driver_state == "awake":
            text = "Alert,Looking Good! 😁"
            color = "green"

            progress = 1.0  # full progress
        elif driver_state == "sleepy":
            text = "Fatigue detected,Be Careful! 😐"
            color = "#ffc40c"

            progress = 0.5
        else:  # falling asleep
            text = "Drowsy,Danger😴"
            color = "red"
            progress = 0.1

        # Update GUI elements
        self.window["-BUTTON-"].update(text=text, button_color=("white", color))
        self.circle_progress.set(progress)  # update circular progress
        #self.window.TKroot.configure(bg=color)

class DashboardController:
    def __init__(self):
        self.view = DashboardView()
        self.session_start_time = time.time()
        self._running = True

        # Generate a session ID at startup
        self.session_id = f"IRIS{random.randint(1000, 9999)}"
        self.view.set_session_id(self.session_id)

        # --- Instantiate ButtonController with window and circular progress ---
        self.button_ctrl = ButtonController(self.view.window, self.view.circle_progress)

        # Initialize WebSocket client
        self.ws_client = DashboardWebSocketClient()
        self.ws_client.on_message = self.handle_backend_update

        # Run listener in background thread
        threading.Thread(target=self.ws_client.start, daemon=True).start()

    def run(self):
        try:
            while self._running:
                # The `values` variable will contain the dictionary we sent
                event, values = self.view.read(timeout=100) # Use a shorter timeout

                if event in (Sg.WINDOW_CLOSED, "Exit"):
                    break

                # --- NEW: Handle the event from the WebSocket thread ---
                if event == "-WS_UPDATE-":
                    # Unpack the data from the event
                    status = values["status"]
                    connected = values["connected"]
                    duration = values["duration"]

                    # Update GUI elements safely from the main thread
                    self.view.set_bt_status(connected)
                    self.view.set_session_duration(int(duration))

                    # Convert backend statuses to dashboard button visuals
                    if status == "Looking good":
                        driver_state = "awake"
                    elif status == "Be careful":
                        driver_state = "sleepy"
                    else:
                        driver_state = "falling_asleep"

                    self.button_ctrl.update(driver_state)

                # Update session duration (this can be removed if the backend sends it)
                duration = int(time.time() - self.session_start_time)
                self.view.set_session_duration(duration)

            self.view.close()
        except KeyboardInterrupt:
            self.view.close()

    def handle_backend_update(self, state):
        """Receive state from backend and post an event to the GUI thread."""
        connected = state.get("connected", False)
        duration = state.get("duration", 0)
        status = state.get("status", "Unknown")

        # --- THIS IS THE CRITICAL CHANGE ---
        # Instead of updating the GUI directly, write an event with the data.
        # The main loop will catch this event and update the GUI safely.
        self.view.window.write_event_value(
            "-WS_UPDATE-",  # A unique key for this event
            {"status": status, "connected": connected, "duration": duration}
        )
