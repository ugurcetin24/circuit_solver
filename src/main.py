from circuit_solver import Circuit

# Devre bileşenleri: R1, R2 ve V1
components = {
    "R1": {"type": "resistor", "node1": 1, "node2": 2, "value": 100},
    "R2": {"type": "resistor", "node1": 2, "node2": 0, "value": 200},
    "V1": {"type": "voltage_source", "node1": 1, "node2": 0, "value": 10}
}

# Devreyi oluştur
circuit = Circuit()

# Bileşenleri ekle
for name, comp in components.items():
    if comp["type"] == "resistor":
        circuit.add_resistor(name, comp["node1"], comp["node2"], comp["value"])
    elif comp["type"] == "voltage_source":
        circuit.add_voltage_source(name, comp["node1"], comp["node2"], comp["value"])

# Nodal çözüm yap
try:
    result = circuit.solve_nodal()
    print("\n[Nodal Analysis Result]")
    for k, v in result.items():
        print(f"{k}: {v:.4f} V")
except Exception as e:
    print("[!] Error during circuit solving:", e)
