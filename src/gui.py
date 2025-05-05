import tkinter as tk
from tkinter import scrolledtext, messagebox
from circuit_solver import Circuit
from numerical_methods import (
    run_lu_decomposition,
    solve_roots,
    interpolate_values,
    differentiate_data,
    integrate_data,
    solve_odes,
    optimize_function,
    compare_lu_vs_direct
)
import matplotlib.pyplot as plt

class CircuitSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Numerical Methods Circuit Solver (Manual Input Mode)")
        self.root.state("zoomed")

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_hint = tk.Label(
            main_frame,
            text="How to use:\n- Enter circuit elements line by line\n- Click on any numerical method\n- See results below\n\nExample Steps:\n1. Paste or type circuit\n2. Press 'Solve Circuit'\n3. Try LU, ODE, etc.",
            justify="left", anchor="n"
        )
        left_hint.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        right_hint = tk.Label(
            main_frame,
            text="Input Format:\n- R1 100 1 2\n- V1 10 1 0\n- I1 1.5 2 0\n\nNotes:\n- Use node 0 as ground\n- Use integers for node numbers\n- Decimal values allowed for sources",
            justify="left", anchor="n"
        )
        right_hint.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        center_frame = tk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)

        self.manual_text = scrolledtext.ScrolledText(center_frame, height=10)
        self.manual_text.insert(tk.END, """R1 100 1 2\nR2 200 2 3\nR3 300 2 4\nR4 400 3 5\nV1 10 1 0\nI1 1 5 0""")
        self.manual_text.pack(pady=10, fill=tk.X)

        self.result_text = scrolledtext.ScrolledText(center_frame, height=20)
        self.result_text.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(center_frame)
        button_frame.pack(pady=10)

        buttons = [
            ("Solve Circuit (Nodal)", self.solve_circuit),
            ("Run Error Analysis", self.run_error_analysis),
            ("LU Decomposition", self.run_lu_analysis),
            ("Root Finding", self.run_root_finding),
            ("Interpolation", self.run_interpolation),
            ("Differentiation", self.run_differentiation),
            ("Integration", self.run_integration),
            ("Solve ODE", self.run_ode_solver),
            ("Optimization", self.run_optimization),
            ("LU vs Direct Comparison", self.run_lu_vs_direct)
        ]

        for i, (label, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=label, command=command, width=25)
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)

    def parse_manual_input(self):
        text = self.manual_text.get("1.0", tk.END).strip().splitlines()
        components = {}
        for line in text:
            parts = line.split()
            if len(parts) != 4:
                continue
            name, value, node1, node2 = parts
            try:
                value = float(value)
                node1 = int(node1)
                node2 = int(node2)
            except:
                continue
            if name.upper().startswith("R"):
                components[name] = {"type": "resistor", "value": value, "node1": node1, "node2": node2}
            elif name.upper().startswith("V"):
                components[name] = {"type": "voltage_source", "value": value, "node1": node1, "node2": node2}
            elif name.upper().startswith("I"):
                components[name] = {"type": "current_source", "value": value, "node1": node1, "node2": node2}
        return components

    def solve_circuit(self):
        try:
            components = self.parse_manual_input()
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
            components = self.parse_manual_input()
            circuit = Circuit()
            for name, info in components.items():
                if info['type'] == 'resistor':
                    circuit.add_resistor(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'voltage_source':
                    circuit.add_voltage_source(name, info['node1'], info['node2'], info['value'])
                elif info['type'] == 'current_source':
                    circuit.add_current_source(name, info['node1'], info['node2'], info['value'])
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
        try:
            A, b, x = run_lu_decomposition()
            self.result_text.insert(tk.END, f"Solution x: {x}\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"LU error: {str(e)}\n")

    def run_root_finding(self):
        self.result_text.insert(tk.END, "\n[Root Finding Result]\n")
        root = solve_roots()
        self.result_text.insert(tk.END, f"Approximate root: {root:.4f}\n")

    def run_interpolation(self):
        self.result_text.insert(tk.END, "\n[Interpolation Result]\n")
        x, y, xp, yp = interpolate_values()
        self.result_text.insert(tk.END, "Interpolated values computed.\n")
        plt.plot(x, y, 'o', label='Original Data')
        plt.plot(xp, yp, '-', label='Linear Interpolation')
        plt.legend()
        plt.title("Interpolation")
        plt.grid()
        plt.show()

    def run_differentiation(self):
        self.result_text.insert(tk.END, "\n[Differentiation Result]\n")
        x, dy_dx = differentiate_data()
        self.result_text.insert(tk.END, "Numerical derivative computed.\n")
        plt.plot(x, dy_dx, label='dy/dx')
        plt.title("Numerical Differentiation")
        plt.grid()
        plt.legend()
        plt.show()

    def run_integration(self):
        self.result_text.insert(tk.END, "\n[Integration Result]\n")
        area = integrate_data()
        self.result_text.insert(tk.END, f"Integral of exp(-x^2) from 0 to 1: {area:.4f}\n")

    def run_ode_solver(self):
        self.result_text.insert(tk.END, "\n[ODE Solution Result]\n")
        t, y = solve_odes()
        self.result_text.insert(tk.END, "ODE solution computed.\n")
        plt.plot(t, y)
        plt.title("ODE Solution: dy/dt = -2y")
        plt.grid()
        plt.show()

    def run_optimization(self):
        self.result_text.insert(tk.END, "\n[Optimization Result]\n")
        x_min, f_min = optimize_function()
        self.result_text.insert(tk.END, f"Minimum at x = {x_min:.4f}, f(x) = {f_min:.4f}\n")

    def run_lu_vs_direct(self):
        self.result_text.insert(tk.END, "\n[LU vs Direct Solver Comparison]\n")
        results = compare_lu_vs_direct()
        self.result_text.insert(tk.END, f"Direct Solve (b1): {results['x1_direct']}\n")
        self.result_text.insert(tk.END, f"Direct Solve (b2): {results['x2_direct']}\n")
        self.result_text.insert(tk.END, f"LU Solve (b1): {results['x1_lu']}\n")
        self.result_text.insert(tk.END, f"LU Solve (b2): {results['x2_lu']}\n")
        self.result_text.insert(tk.END, f"\nTime (Direct Total): {results['time_direct']:.8f} seconds\n")
        self.result_text.insert(tk.END, f"Time (LU Total): {results['time_lu']:.8f} seconds\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitSolverGUI(root)
    root.mainloop()
