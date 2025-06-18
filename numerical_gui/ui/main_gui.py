import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import matplotlib.pyplot as plt
import os
import sys # sys.path manipülasyonu için
import traceback # Hata ayıklama için detaylı hata mesajları

# Bu dosya numerical_gui/ui/ altında olduğundan,
# bir üstteki numerical_gui paketine ve onun altındaki circuit ve numerics'e erişmek için
# doğru import yolları kullanılmalı.
# Eğer bu dosya doğrudan python numerical_gui/ui/main_gui.py olarak çalıştırılıyorsa,
# __main__ bloğundaki sys.path ayarı önemlidir.
try:
    from numerical_gui.circuit.circuit_solver import Circuit
    from numerical_gui.numerics.lu_decomp import run_lu_decomposition
    from numerical_gui.numerics.root_finding import run as rf_run
    # Diğer numerik modülleri kullandıkça buraya ekleyebilirsiniz:
    # import importlib # run_generic_module için
    # from numerical_gui.numerics.linear_solver import run as ls_run
    # from numerical_gui.numerics.error_analysis import run as ea_run
    # from numerical_gui.numerics.interpolation import run as int_run
    # from numerical_gui.numerics.diff_int import run as di_run
    # from numerical_gui.numerics.ode_solver import run as ode_run
    # from numerical_gui.numerics.optimization import run as opt_run
    # from numerical_gui.numerics.performance import run as perf_run
    # from numerical_gui.numerics.visualization import run as viz_run
    # from numerical_gui.numerics.comparison import run as comp_run
except ImportError:
    # Eğer yukarıdaki importlar çalışmazsa (örn: dosya farklı bir yerden çalıştırılıyorsa),
    # bu, sys.path'in doğru ayarlanmadığı anlamına gelebilir.
    # __main__ bloğundaki sys.path ayarı bu durumu çözmeye çalışır.
    print("Warning: numerical_gui paketinden importlar başarısız oldu. "
          "Eğer bu dosyayı doğrudan çalıştırıyorsanız, sys.path ayarının doğru olduğundan emin olun.")
    pass 


class CircuitSolverGUI_Tkinter:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Circuit Solver (Tkinter GUI)")
        self.root.geometry("1000x700") 

        self.user_params = {} 

        main_container = tk.Frame(self.root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor="nw") # anchor eklendi

        right_frame = tk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Sol tarafa yaslandıktan sonra sağ taraf genişlesin

        # --- Sol Çerçeve: Netlist Girişi ve Parametreler ---
        netlist_frame = tk.LabelFrame(left_frame, text="Netlist Input (NAME VALUE NODE1 NODE2)", padx=5, pady=5)
        netlist_frame.pack(pady=(0,10), fill=tk.X)
        
        self.netlist_text_box = scrolledtext.ScrolledText(netlist_frame, height=10, width=45, font=("Courier New", 10), wrap=tk.WORD)
        self.netlist_text_box.insert(tk.END, "R1 100 1 2\nR2 200 2 0\nV1 10 1 0")
        self.netlist_text_box.pack(fill=tk.X, expand=True)

        file_io_frame = tk.Frame(netlist_frame)
        file_io_frame.pack(fill=tk.X, pady=(5,0))
        tk.Button(file_io_frame, text="Load Netlist", command=self.load_netlist_from_file, width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(file_io_frame, text="Save Netlist", command=self.save_netlist_to_file, width=15).pack(side=tk.LEFT, padx=2)

        self.param_input_frame = tk.LabelFrame(left_frame, text="Method Parameters", padx=5, pady=5)
        self.param_input_frame.pack(pady=10, fill=tk.X)
        self._setup_parameter_entries()
        
        # --- Sağ Çerçeve: Butonlar ve Sonuçlar ---
        actions_frame = tk.LabelFrame(right_frame, text="Actions", padx=5, pady=5)
        actions_frame.pack(pady=(0,10), fill=tk.X) # Sağ çerçevenin en üstüne
        self._setup_action_buttons(actions_frame)

        results_frame = tk.LabelFrame(right_frame, text="Output / Results", padx=5, pady=5)
        results_frame.pack(pady=10, fill=tk.BOTH, expand=True) # Kalan alanı dolduracak
        self.results_text_box = scrolledtext.ScrolledText(results_frame, height=15, font=("Courier New", 10), wrap=tk.WORD)
        self.results_text_box.pack(fill=tk.BOTH, expand=True)
        
        # apply_parameters'ı widget'lar oluşturulduktan sonra çağır
        self.apply_parameters() # Başlangıç parametrelerini yükle

    def _setup_parameter_entries(self):
        self.param_entries = {}
        param_config = { # (isim, varsayılan, satır, sütun, tip)
            "R1_min":      ("10.0",    0, 1, float),
            "R1_max":      ("10000.0", 0, 3, float),
            "V_target":    ("5.0",     1, 1, float),
            "Target_Node": ("2",       1, 3, int),
        }

        for name, (default_val, r, c, p_type) in param_config.items():
            tk.Label(self.param_input_frame, text=f"{name}:").grid(row=r, column=c-1, padx=2, pady=3, sticky="w")
            entry = tk.Entry(self.param_input_frame, width=12)
            entry.insert(0, default_val)
            entry.grid(row=r, column=c, padx=2, pady=3, sticky="ew")
            self.param_entries[name] = (entry, p_type)
        
        tk.Button(self.param_input_frame, text="Apply Parameters", command=self.apply_parameters, width=15) \
            .grid(row=max(v[1] for v in param_config.values()) + 1, column=0, columnspan=4, pady=(10,5), sticky="e")

    def _setup_action_buttons(self, parent_frame):
        buttons_config = [
            ("Solve Circuit (Nodal)", self.solve_circuit_nodal),
            ("LU Decomposition", self.run_lu_decomposition_gui),
            ("Root Finding (R1 for V_target)", self.run_root_finding_gui),
        ]
        for i, (label, cmd) in enumerate(buttons_config):
            tk.Button(parent_frame, text=label, command=cmd, width=28, height=1) \
                .grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")

    def apply_parameters(self):
        temp_params = {}
        try:
            for name, (entry_widget, param_type) in self.param_entries.items():
                value_str = entry_widget.get()
                if not value_str.strip() and name in ["R1_min", "R1_max", "V_target", "Target_Node"]: # Örnek zorunlu alanlar
                    raise ValueError(f"Parameter '{name}' cannot be empty.")
                elif not value_str.strip(): # Diğerleri boşsa varsayılanı kullanabilir veya atlayabilir
                    continue # Veya varsayılanı DEFAULTS'tan al
                temp_params[name] = param_type(value_str) 
            
            self.user_params.update(temp_params) # Sadece geçerli olanları güncelle
            self._log_to_results(f"[INFO] Parameters Updated: {self.user_params}")
            return True
        except ValueError as e:
            messagebox.showerror("Invalid Parameter", f"Error in parameter input: {e}")
            self._log_to_results(f"[ERROR] Invalid parameter input: {e}", is_error=True)
            return False

    def _log_to_results(self, message: str, clear_first: bool = False, is_error: bool = False):
        if clear_first:
            self.results_text_box.delete("1.0", tk.END)
        prefix = "[ERROR] " if is_error else ""
        self.results_text_box.insert(tk.END, prefix + message + "\n")
        self.results_text_box.see(tk.END)

    def _convert_netlist_format(self, netlist_tk_format: str) -> str:
        if not netlist_tk_format.strip(): return ""
        converted_lines = []
        for line_num, line_content in enumerate(netlist_tk_format.strip().splitlines()):
            parts = line_content.strip().split()
            if not parts: continue
            if len(parts) == 4:
                name, val_str, n1_str, n2_str = parts
                converted_lines.append(f"{name} {n1_str} {n2_str} {val_str}")
            else:
                self._log_to_results(f"[WARNING] Line {line_num+1} ('{line_content}') has incorrect format, skipping conversion.", is_error=True)
                converted_lines.append(line_content) 
        return "\n".join(converted_lines)

    def _get_netlist_for_numerics(self) -> str:
        netlist_from_gui = self.netlist_text_box.get("1.0", tk.END).strip()
        if not netlist_from_gui:
            messagebox.showwarning("Input Error", "Netlist is empty.")
            self._log_to_results("[ERROR] Netlist is empty.", is_error=True)
            return ""
        return self._convert_netlist_format(netlist_from_gui)

    def load_netlist_from_file(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Netlist Files", "*.net"), ("All Files", "*.*")]
        )
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: # encoding eklendi
                content = f.read()
            self.netlist_text_box.delete("1.0", tk.END)
            self.netlist_text_box.insert("1.0", content)
            self._log_to_results(f"[INFO] Netlist loaded from: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to load netlist file: {e}")
            self._log_to_results(f"[ERROR] Failed to load netlist: {e}", is_error=True)

    def save_netlist_to_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Netlist Files", "*.net"), ("All Files", "*.*")]
        )
        if not filepath: return
        try:
            content = self.netlist_text_box.get("1.0", tk.END)
            with open(filepath, 'w', encoding='utf-8') as f: # encoding eklendi
                f.write(content.strip()) # Sondaki boşlukları temizle
            self._log_to_results(f"[INFO] Netlist saved to: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to save netlist file: {e}")
            self._log_to_results(f"[ERROR] Failed to save netlist: {e}", is_error=True)

    def solve_circuit_nodal(self):
        self._log_to_results("\n--- Nodal Analysis ---", clear_first=True)
        try:
            temp_circuit = Circuit()
            raw_netlist_gui_format = self.netlist_text_box.get("1.0", tk.END).strip()
            if not raw_netlist_gui_format:
                self._log_to_results("Netlist is empty for nodal analysis.", is_error=True)
                return

            for line_num, line_content in enumerate(raw_netlist_gui_format.strip().splitlines()):
                parts = line_content.strip().split()
                if not parts: continue
                if len(parts) != 4:
                    raise ValueError(f"Line {line_num + 1} ('{line_content}') invalid format. Expected: NAME VALUE NODE1 NODE2")
                name, val_str, n1_str, n2_str = parts
                
                if name.upper().startswith("R"):
                    temp_circuit.add_resistor(name, n1_str, n2_str, val_str)
                elif name.upper().startswith("V"):
                    temp_circuit.add_voltage_source(name, n1_str, n2_str, val_str)
                elif name.upper().startswith("I"):
                    temp_circuit.add_current_source(name, n1_str, n2_str, val_str)
                else:
                    raise ValueError(f"Line {line_num + 1}: Unknown component '{name}'")

            if not temp_circuit.components:
                self._log_to_results("No valid components found in netlist for nodal analysis.", is_error=True)
                return

            solution = temp_circuit.solve_nodal()
            if "Info" in solution: # Circuit.solve_nodal'dan özel mesaj
                self._log_to_results(f"[INFO] {solution['Info']}")
                return

            for node_name, voltage in sorted(solution.items(), key=lambda item: (item[0].startswith("Node 0"), int(item[0].split()[1]) if item[0].split()[1].isdigit() else float('inf')) ):
                self._log_to_results(f"{node_name}: {voltage:.4f} V")

        except ValueError as ve:
            self._log_to_results(f"Nodal Analysis Error: {ve}", is_error=True)
            messagebox.showerror("Nodal Analysis Error", str(ve))
        except Exception as e:
            self._log_to_results(f"Unexpected Nodal Analysis Error: {e}\n{traceback.format_exc()}", is_error=True)
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

    def run_lu_decomposition_gui(self):
        self._log_to_results("\n--- LU Decomposition ---", clear_first=True)
        netlist_for_numerics = self._get_netlist_for_numerics()
        if not netlist_for_numerics: return

        try:
            A, b, x_solution = run_lu_decomposition(netlist_for_numerics)
            self._log_to_results(f"Matrix A (shape: {A.shape}):\n{A}")
            self._log_to_results(f"\nVector b (shape: {b.shape}):\n{b}")
            self._log_to_results(f"\nSolution x (shape: {x_solution.shape}):\n{x_solution}")
        except ValueError as ve:
            self._log_to_results(f"LU Decomposition Error: {ve}", is_error=True)
            messagebox.showerror("LU Decomposition Error", str(ve))
        except Exception as e:
            self._log_to_results(f"Unexpected LU Error: {e}\n{traceback.format_exc()}", is_error=True)
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

    def run_root_finding_gui(self):
        self._log_to_results("\n--- Root Finding (Bisection for R1) ---", clear_first=True)
        if not self.apply_parameters(): return
        
        netlist_for_numerics = self._get_netlist_for_numerics()
        if not netlist_for_numerics: return

        fig = plt.figure(figsize=(8,6))
        try:
            result_message = rf_run(netlist_for_numerics, fig, self.user_params)
            self._log_to_results(result_message)
            if fig.get_axes(): plt.show()
            else: plt.close(fig)
        except Exception as e:
            self._log_to_results(f"Root Finding Error: {e}\n{traceback.format_exc()}", is_error=True)
            messagebox.showerror("Root Finding Error", str(e))
            if fig: plt.close(fig)

if __name__ == "__main__":
    try:
        current_file_path = os.path.abspath(__file__)
        ui_dir = os.path.dirname(current_file_path)
        numerical_gui_dir = os.path.dirname(ui_dir)
        project_root_dir = os.path.dirname(numerical_gui_dir)
        if project_root_dir not in sys.path:
            sys.path.insert(0, project_root_dir)
    except NameError:
        print("Warning: Could not determine project root for sys.path modification.")

    root = tk.Tk()
    app = CircuitSolverGUI_Tkinter(root)
    root.mainloop()