# ui/dashboard.py
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib
from ui.param_panel import ParamPanel     #  << yeni
from pathlib import Path

# Button metni  ↔  modül adı
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
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Numerical Circuit Toolkit")
        self.geometry("1200x680")
        self.minsize(1000, 600)

        # ------------- parameter panel (left) ------------------------------
        self.current_params = {}       # will store latest values
        self.param_panel = ParamPanel(self, on_change=self._update_params)
        self.param_panel.pack(side="left", fill="y", padx=(10, 5), pady=5)

        # ------------- buttons frame ---------------------------------------
        btn_frame = ctk.CTkScrollableFrame(self, orientation="vertical", width=180)
        btn_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)

        for text, mod in NUMERIC_MODULES:
            ctk.CTkButton(
                btn_frame, text=text,
                command=lambda m=mod: self.run_module(m)
            ).pack(fill="x", pady=3)

        # ------------- netlist textbox (top) -------------------------------
        self.input_box = ctk.CTkTextbox(self, height=110, wrap="none")
        self.input_box.insert("1.0", "R1 1 2 100\nR2 2 0 1000\nV1 1 0 10")
        self.input_box.pack(fill="x", padx=10, pady=(10, 5))

        # ------------- matplotlib canvas (right) ---------------------------
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both",
                                         expand=True, padx=5, pady=5)

    # -------------------------- helpers ------------------------------------
    def _update_params(self, param_dict: dict):
        """Callback from ParamPanel."""
        self.current_params = param_dict

    def run_module(self, module_name: str):
        try:
            mod = importlib.import_module(f"numerics.{module_name}")
            netlist = self.input_box.get("1.0", "end-1c")
            # Pass params to every module
            result = mod.run(netlist, self.fig, self.current_params)
            self.canvas.draw_idle()
            self._show_status(result)
        except Exception as exc:
            self._show_status(f"Error: {exc}")

    def _show_status(self, msg: str):
        ctk.CTkLabel(self, text=msg, text_color="red",
                     anchor="w").pack(anchor="w", padx=12)
