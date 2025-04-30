import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from ocr_reader import read_text_from_image
from ocr_parser import parse_ocr_text
from circuit_solver import Circuit
from numerical_methods import run_lu_decomposition, solve_roots, interpolate_values, differentiate_data, integrate_data, solve_odes, optimize_function

class CircuitSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Numerical Methods Circuit Solver")
        self.root.geometry("800x800")

        # Text area to show OCR output
        self.ocr_text = scrolledtext.ScrolledText(root, height=10)
        self.ocr_text.pack(pady=10)

        # Text area to show results
        self.result_text = scrolledtext.ScrolledText(root, height=20)
        self.result_text.pack(pady=10)

        # Button grid layout
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        buttons = [
            ("Upload Circuit Image", self.load_image),
            ("Solve Circuit (Nodal)", self.solve_circuit),
            ("Run Error Analysis", self.run_error_analysis),
            ("LU Decomposition", self.run_lu_analysis),
            ("Root Finding", self.run_root_finding),
            ("Interpolation", self.run_interpolation),
            ("Differentiation", self.run_differentiation),
            ("Integration", self.run_integration),
            ("Solve ODE", self.run_ode_solver),
            ("Optimization", self.run_optimization)
        ]

        for i, (label, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=label, command=command, width=25)
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)

        self.ocr_result = ""

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.ocr_result = read_text_from_image(file_path, save_output=False)
            self.ocr_text.delete("1.0", tk.END)
            self.ocr_text.insert(tk.END, self.ocr_result)

    def solve_circuit(self):
        try:
            components = parse_ocr_text(self.ocr_result)
            circuit = Circuit()

            for name, info in components.items():
                if info['type'] == 'resistor':
                    circuit.add_resistor(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'voltage_source':
                    circuit.add_voltage_source(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'current_source':
                    circuit.add_current_source(name, info['node1'], info['node2'], info['value'])

            result = circuit.solve_nodal()

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "[Nodal Analysis Result]\n")
            for key, value in result.items():
                self.result_text.insert(tk.END, f"{key}: {value:.4f} V\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_error_analysis(self):
        try:
            components = parse_ocr_text(self.ocr_result)
            circuit = Circuit()

            for name, info in components.items():
                if info['type'] == 'resistor':
                    circuit.add_resistor(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'voltage_source':
                    circuit.add_voltage_source(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'current_source':
                    circuit.add_current_source(name, info['node1'], info['node2'], info['value'])

            if not all(
                (comp['type'] == 'resistor' and comp['node1'] == 1 and comp['node2'] == 0) or
                (comp['type'] == 'voltage_source' and comp['node1'] == 1 and comp['node2'] == 0)
                for comp in circuit.components
            ):
                self.result_text.insert(tk.END, "\n[ERROR ANALYSIS] Not a simple series circuit.\n")
                return

            nodal_result = circuit.solve_nodal()
            simple_result = circuit.solve_simple_series()

            v1_nodal = nodal_result.get("Node 1 Voltage (V)")
            v1_simple = simple_result.get("Node 1 Voltage (V)")

            relative_error = abs(v1_nodal - v1_simple) / abs(v1_nodal)
            percent_error = relative_error * 100

            self.result_text.insert(tk.END, f"\n[ERROR ANALYSIS]\n")
            self.result_text.insert(tk.END, f"Node 1 (Nodal): {v1_nodal:.4f} V\n")
            self.result_text.insert(tk.END, f"Node 1 (Series): {v1_simple:.4f} V\n")
            self.result_text.insert(tk.END, f"Percent Error: {percent_error:.2f}%\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_lu_analysis(self):
        self.result_text.insert(tk.END, "\n[LU Decomposition Result]\n")
        self.result_text.insert(tk.END, run_lu_decomposition())

    def run_root_finding(self):
        self.result_text.insert(tk.END, "\n[Root Finding Result]\n")
        self.result_text.insert(tk.END, solve_roots())

    def run_interpolation(self):
        self.result_text.insert(tk.END, "\n[Interpolation Result]\n")
        self.result_text.insert(tk.END, interpolate_values())

    def run_differentiation(self):
        self.result_text.insert(tk.END, "\n[Differentiation Result]\n")
        self.result_text.insert(tk.END, differentiate_data())

    def run_integration(self):
        self.result_text.insert(tk.END, "\n[Integration Result]\n")
        self.result_text.insert(tk.END, integrate_data())

    def run_ode_solver(self):
        self.result_text.insert(tk.END, "\n[ODE Solution Result]\n")
        self.result_text.insert(tk.END, solve_odes())

    def run_optimization(self):
        self.result_text.insert(tk.END, "\n[Optimization Result]\n")
        self.result_text.insert(tk.END, optimize_function())

if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitSolverGUI(root)
    root.mainloop()
