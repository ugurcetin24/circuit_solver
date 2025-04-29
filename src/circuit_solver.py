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

    def show_components(self):
        for comp in self.components:
            print(comp)

    def solve_simple_series(self):
        """
        Solve a simple series circuit where all resistors and one voltage source exist.
        Assumptions:
            - All elements connected between node1=1 and node2=0
            - One voltage source exists
        Returns:
            dict: node voltages
        """
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

        # Calculate voltage at node 1
        voltage_node1 = voltage

        # Node 0 is always ground (0V)
        return {
            "Node 1 Voltage (V)": voltage_node1,
            "Node 0 Voltage (V)": 0,
            "Circuit Current (A)": current
        }
