# main.py
import customtkinter as ctk
from ui.dashboard import Dashboard   

def run() -> None:
    """Application entry point."""
    ctk.set_appearance_mode("System")         # Follows OS light/dark
    ctk.set_default_color_theme("dark-blue")  # Pre-made palette
    app = Dashboard()
    app.mainloop()

if __name__ == "__main__":
    run()
