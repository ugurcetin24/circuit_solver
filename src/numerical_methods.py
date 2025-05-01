import numpy as np

class Circuit:
    def __init__(self):
        self.components = []
        self.nodes = set()

    def add_resistor(self, name, node1, node2, value):
        self.components.append({
            "type": "resistor",
            "name": name,
            "node1": node1,
            "node2": node2,
            "value": value
        })
        self.nodes.update([node1, node2])

    def add_voltage_source(self, name, node1, node2, value):
        self.components.append({
            "type": "voltage_source",
            "name": name,
            "node1": node1,
            "node2": node2,
            "value": value
        })
        self.nodes.update([node1, node2])

    def add_current_source(self, name, node1, node2, value):
        self.components.append({
            "type": "current_source",
            "name": name,
            "node1": node1,
            "node2": node2,
            "value": value
        })
        self.nodes.update([node1, node2])

    def show_components(self):
        for comp in self.components:
            print(comp)

    def solve_simple_series(self):
        total_resistance = 0
        voltage = 0
        for comp in self.components:
            if comp["type"] == "resistor":
                total_resistance += comp["value"]
            elif comp["type"] == "voltage_source":
                voltage = comp["value"]

        if total_resistance == 0:
            raise ValueError("Total resistance is zero, cannot solve.")

        current = voltage / total_resistance
        return {
            "Node 1 Voltage (V)": voltage,
            "Node 0 Voltage (V)": 0,
            "Circuit Current (A)": current
        }

    def solve_nodal(self):
        nodes = set()
        voltage_sources = []
        for comp in self.components:
            nodes.update([comp["node1"], comp["node2"]])
            if comp["type"] == "voltage_source":
                voltage_sources.append(comp)

        nodes.discard(0)
        node_list = sorted(list(nodes))
        node_index = {node: i for i, node in enumerate(node_list)}
        n = len(node_list)
        m = len(voltage_sources)

        A = np.zeros((n + m, n + m))
        b = np.zeros(n + m)

        v_idx = 0
        for comp in self.components:
            n1 = comp["node1"]
            n2 = comp["node2"]
            value = comp["value"]

            if comp["type"] == "resistor":
                g = 1 / value
                if n1 != 0:
                    i = node_index[n1]
                    A[i][i] += g
                if n2 != 0:
                    j = node_index[n2]
                    A[j][j] += g
                if n1 != 0 and n2 != 0:
                    i = node_index[n1]
                    j = node_index[n2]
                    A[i][j] -= g
                    A[j][i] -= g

            elif comp["type"] == "current_source":
                if n1 != 0:
                    i = node_index[n1]
                    b[i] -= value
                if n2 != 0:
                    j = node_index[n2]
                    b[j] += value

        for vs in voltage_sources:
            n1 = vs["node1"]
            n2 = vs["node2"]
            v_value = vs["value"]
            row = n + v_idx

            if n1 != 0:
                i = node_index[n1]
                A[row][i] = 1
                A[i][row] = 1
            if n2 != 0:
                j = node_index[n2]
                A[row][j] = -1
                A[j][row] = -1

            b[row] = v_value
            v_idx += 1

        try:
            x = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            raise ValueError("System matrix is singular — cannot solve.")

        result = {}
        for i, node in enumerate(node_list):
            result[f"Node {node} Voltage (V)"] = x[i]

        return result

def run_lu_decomposition():
    return "LU decomposition not yet implemented.\n"

def solve_roots():
    return "Root finding not yet implemented.\n"

def interpolate_values():
    return "Interpolation not yet implemented.\n"

def differentiate_data():
    return "Differentiation not yet implemented.\n"

def integrate_data():
    return "Integration not yet implemented.\n"

def solve_odes():
    return "ODE solving not yet implemented.\n"

def optimize_function():
    return "Optimization not yet implemented.\n"
