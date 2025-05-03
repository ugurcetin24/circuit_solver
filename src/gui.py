import tkinter as tk
from tkinter import scrolledtext, messagebox
from circuit_solver import Circuit
import numpy as np
import scipy.linalg
from scipy.optimize import minimize_scalar, minimize
from scipy.integrate import odeint, quad
import matplotlib.pyplot as plt
import time

class CircuitSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Numerical Methods Circuit Solver (Manual Input Mode)")
        self.root.state("zoomed")  # Fullscreen

        # Ana çerçeve: sol, merkez, sağ
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sol: Kullanım Talimatları
        left_hint = tk.Label(
            main_frame,
            text="How to use:\n- Enter circuit elements line by line\n- Click on any numerical method\n- See results below\n\nExample Steps:\n1. Paste or type circuit\n2. Press 'Solve Circuit'\n3. Try LU, ODE, etc.",
            justify="left", anchor="n"
        )
        left_hint.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Sağ: Format Bilgisi
        right_hint = tk.Label(
            main_frame,
            text="Input Format:\n- R1 100 1 2\n- V1 10 1 0\n- I1 1.5 2 0\n\nNotes:\n- Use node 0 as ground\n- Use integers for node numbers\n- Decimal values allowed for sources",
            justify="left", anchor="n"
        )
        right_hint.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Orta: Ana içeriği taşıyan frame
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
        A = np.array([[4, 3], [6, 3]])
        b = np.array([10, 12])
        try:
            lu, piv = scipy.linalg.lu_factor(A)
            x = scipy.linalg.lu_solve((lu, piv), b)
            self.result_text.insert(tk.END, f"Solution x: {x}\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"LU error: {str(e)}\n")

    def run_root_finding(self):
        self.result_text.insert(tk.END, "\n[Root Finding Result]\n")
        f = lambda x: x**3 - x - 2
        res = minimize_scalar(lambda x: abs(f(x)), bounds=(1, 2), method='bounded')
        self.result_text.insert(tk.END, f"Approximate root: {res.x:.4f}\n")

    def run_interpolation(self):
        self.result_text.insert(tk.END, "\n[Interpolation Result]\n")
        x = np.array([0, 1, 2, 3])
        y = np.array([1, 3, 2, 5])
        xp = np.linspace(0, 3, 100)
        yp = np.interp(xp, x, y)
        self.result_text.insert(tk.END, "Interpolated values computed.\n")
        plt.plot(x, y, 'o', label='Original Data')
        plt.plot(xp, yp, '-', label='Linear Interpolation')
        plt.legend()
        plt.title("Interpolation")
        plt.grid()
        plt.show()

    def run_differentiation(self):
        self.result_text.insert(tk.END, "\n[Differentiation Result]\n")
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        dy_dx = np.gradient(y, x)
        self.result_text.insert(tk.END, "Numerical derivative computed.\n")
        plt.plot(x, dy_dx, label='dy/dx')
        plt.title("Numerical Differentiation")
        plt.grid()
        plt.legend()
        plt.show()

    def run_integration(self):
        self.result_text.insert(tk.END, "\n[Integration Result]\n")
        f = lambda x: np.exp(-x**2)
        area, _ = quad(f, 0, 1)
        self.result_text.insert(tk.END, f"Integral of exp(-x^2) from 0 to 1: {area:.4f}\n")

    def run_ode_solver(self):
        self.result_text.insert(tk.END, "\n[ODE Solution Result]\n")
        def model(y, t):
            return -2 * y
        t = np.linspace(0, 5, 100)
        y0 = 1
        y = odeint(model, y0, t)
        self.result_text.insert(tk.END, "ODE solution computed.\n")
        plt.plot(t, y)
        plt.title("ODE Solution: dy/dt = -2y")
        plt.grid()
        plt.show()

    def run_optimization(self):
        self.result_text.insert(tk.END, "\n[Optimization Result]\n")
        f = lambda x: (x - 2)**2 + 1
        res = minimize_scalar(f, bounds=(0, 4), method='bounded')
        self.result_text.insert(tk.END, f"Minimum at x = {res.x:.4f}, f(x) = {res.fun:.4f}\n")

    def run_lu_vs_direct(self):
        self.result_text.insert(tk.END, "\n[LU vs Direct Solver Comparison]\n")
        A = np.array([[4, 3], [6, 3]])
        b1 = np.array([10, 12])
        b2 = np.array([20, 30])
        try:
            start_direct = time.perf_counter()
            x1_direct = np.linalg.solve(A, b1)
            x2_direct = np.linalg.solve(A, b2)
            time_direct = time.perf_counter() - start_direct

            start_lu = time.perf_counter()
            lu, piv = scipy.linalg.lu_factor(A)
            x1_lu = scipy.linalg.lu_solve((lu, piv), b1)
            x2_lu = scipy.linalg.lu_solve((lu, piv), b2)
            time_lu = time.perf_counter() - start_lu

            self.result_text.insert(tk.END, f"Direct Solve (b1): {x1_direct}\n")
            self.result_text.insert(tk.END, f"Direct Solve (b2): {x2_direct}\n")
            self.result_text.insert(tk.END, f"LU Solve (b1): {x1_lu}\n")
            self.result_text.insert(tk.END, f"LU Solve (b2): {x2_lu}\n")
            self.result_text.insert(tk.END, f"\nTime (Direct Total): {time_direct:.8f} seconds\n")
            self.result_text.insert(tk.END, f"Time (LU Total): {time_lu:.8f} seconds\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitSolverGUI(root)
    root.mainloop()