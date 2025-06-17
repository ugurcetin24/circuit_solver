# ui/param_panel.py
import customtkinter as ctk

DEFAULTS = {
    # --- kök-bulma / dif-integ / interpolasyon ---
    "R1_min"   : 10.0,
    "R1_max"   : 10_000.0,
    "V_target" : 5.0,

    # --- ODE (RC) ---
    "ODE_R"    : 1_000.0,    # Ω
    "ODE_C"    : 1e-6,       # F
}

class ParamPanel(ctk.CTkScrollableFrame):
    """
    Scrollable panel with <key,value> entry widgets.
    on_change(values_dict) callback fires when user presses <Enter> or Apply.
    """

    def __init__(self, master, on_change):
        super().__init__(master, width=220, orientation="vertical")
        self._on_change = on_change
        self.entries = {}

        ctk.CTkLabel(self, text="Parameters",
                     font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 8))

        for key, default in DEFAULTS.items():
            row = ctk.CTkFrame(self)
            row.pack(fill="x", pady=2, padx=4)

            ctk.CTkLabel(row, text=key, width=100, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(row, width=80)
            ent.insert(0, str(default))
            ent.pack(side="right")
            ent.bind("<Return>", lambda *_: self._fire())
            self.entries[key] = ent

        ctk.CTkButton(self, text="Apply", command=self._fire)\
            .pack(pady=(6, 4), fill="x", padx=4)

    # --------------------------------------------------------------------- #
    def _values(self):
        vals = {}
        for k, ent in self.entries.items():
            try:
                vals[k] = float(ent.get())
            except ValueError:
                vals[k] = DEFAULTS[k]
        return vals

    def _fire(self):
        """Send current dict to dashboard."""
        self._on_change(self._values())
