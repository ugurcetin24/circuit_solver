# Numerical Methods Circuit Solver GUI

An interactive Tkinter/ttkbootstrap tool that analyses DC resistor circuits while showcasing core numerical‑methods algorithms.

---

## 🚀 Quick Start

```bash
# 1. Clone repo & enter
$ git clone <repo‑url>
$ cd circuit_solver_gui

# 2. Install deps (Python ≥ 3.9)
$ pip install -r requirements.txt

# 3. Run GUI
$ python -m numerical_gui.ui.main_gui
```

---

## 🔑 What You Can Do

| Button             | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Linear Solver**  | Parse netlist → build MNA → solve with `numpy.linalg.solve`. |
| **LU Decomp**      | Visualise L & U heat‑maps; verify A ≈ L·U.                   |
| **Error Analysis** | Compare exact vs. numerical node voltages.                   |
| **Interpolation**  | Fit sinusoids / polynomials to solution data.                |
| **Diff / Int**     | Numerical derivative & integral demos.                       |
| **Optimization**   | Least‑squares parameter fitting.                             |
| **ODE Solver**     | Solve simple ODE example with Runge‑Kutta.                   |
| **Performance**    | Time complexity vs. matrix size.                             |
| **Comparison**     | Direct vs. LU runtime bar‑chart.                             |
| **Visualization**  | Quick sine‑wave plot (backend test).                         |

---

## 📝 Netlist Format

```
R<id> n1 n2 value   # resistor in ohms
V<id> n+ n- value   # DC source in volts
```

Example:

```
R1 1 2 1000
R2 2 0 2000
V1 1 0 10
```

Paste the text into the "Netlist" box, then press a module button.

---

## Folder Layout (minimal)

```
numerical_gui/
  ui/main_gui.py      # Tkinter + ttkbootstrap window
  circuit/            # parse_netlist & build_mna helpers
  numerics/           # one file per module listed above
```

Enjoy analysing circuits & numerical methods in one place!
