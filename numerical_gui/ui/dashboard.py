# ui/dashboard.py
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib

# Button text  ↔  underlying numerics module
NUMERIC_MODULES = [
    ("Error Analysis",     "error_analysis"),
    ("Root Finding",       "root_finding"),
    ("Interpolation",      "interpolation"),
    ("Diff / Integral",    "diff_int"),
    ("Linear Solver",      "linear_solver"),
    ("LU Decomposition",   "lu_decomp"),
    ("Optimization",       "optimization"),
    ("ODE Solution",       "ode_solver"),
    ("Performance Stats",  "performance"),
    ("Visualization",      "visualization"),
    ("Comparison",         "comparison"),
]

class Dashboard(ctk.CTk):
    """Main application window with input box, buttons, and plot area."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Numerical Circuit Toolkit")
        self.geometry("1050x650")

        # ---------- user netlist input ----------
        self.input_box = ctk.CTkTextbox(self, height=120, wrap="none")
        self.input_box.insert("1.0", "R1 1 2 100\nV1 1 0 10")
        self.input_box.pack(fill="x", padx=10, pady=(10, 5))

        # ---------- left pane: vertical button list ----------
        btn_frame = ctk.CTkScrollableFrame(self, orientation="vertical", width=260)
        btn_frame.pack(side="left", fill="y", padx=(10, 5), pady=5)

        for text, mod in NUMERIC_MODULES:
            ctk.CTkButton(
                btn_frame, text=text,
                command=lambda m=mod: self.run_module(m)
            ).pack(fill="x", pady=3)

        # ---------- right pane: matplotlib canvas ----------
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True,
                                         padx=5, pady=5)

    # --------------------------------------------------
    def run_module(self, module_name: str) -> None:
        """Dynamically import numerics.<module_name> and execute its run()."""
        try:
            mod = importlib.import_module(f"numerics.{module_name}")
            netlist = self.input_box.get("1.0", "end-1c")
            result = mod.run(netlist, self.fig)   # fig may be used or ignored
            self.canvas.draw_idle()
            self.show_status(result)
        except Exception as exc:
            self.show_status(f"Error: {exc}")

    def show_status(self, msg: str) -> None:
        """Display a one-line status message under the buttons."""
        ctk.CTkLabel(self, text=msg, justify="left",
                     text_color="red").pack(anchor="w", padx=12)
