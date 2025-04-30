def parse_ocr_text(text):
    """
    Parses raw OCR text into a structured component dictionary.
    Accepts loose formats like:
        R1 R2\n100 200\nV1\n10V\n
    Returns dict with keys as component names and values as dicts containing type, value, and node info.
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    components = {}
    resistors = []
    values = []

    # Step 1: Rough format normalization
    for i, line in enumerate(lines):
        if any(r.startswith("R") for r in line.split()):
            resistors = line.split()
        elif all(x.replace('.', '').isdigit() for x in line.split()):
            values = [float(v) for v in line.split()]
        elif line.upper().startswith("V"):
            if i+1 < len(lines) and "V" in lines[i+1].upper():
                voltage_value = float(lines[i+1].replace("V", "").strip())
                components[line.strip()] = {
                    "type": "voltage_source",
                    "value": voltage_value,
                    "node1": 1,
                    "node2": 0
                }
        elif line.upper().startswith("I"):
            if i+1 < len(lines):
                current_value = float(lines[i+1].replace("mA", "").replace("A", "").strip())
                components[line.strip()] = {
                    "type": "current_source",
                    "value": current_value,
                    "node1": 2,
                    "node2": 0
                }

    # Step 2: Assign resistors and values to nodes manually (best guess)
    for idx, name in enumerate(resistors):
        if idx < len(values):
            node1 = idx + 1
            node2 = 0 if idx + 1 == len(values) else node1 + 1
            components[name] = {
                "type": "resistor",
                "value": values[idx],
                "node1": node1,
                "node2": node2
            }

    return components
