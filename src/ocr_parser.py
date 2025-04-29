def parse_ocr_text(text):
    """
    Parse OCR text and extract components and their values.
    Example input:
        R1 R2
        100 200
        V1
        10V
    Returns:
        dict of components
    """
    lines = text.strip().split('\n')
    components = {}
    resistors = []
    resistor_values = []
    voltage_name = ""
    voltage_value = None

    for line in lines:
        words = line.strip().split()
        for word in words:
            if word.startswith("R"):
                resistors.append(word)
            elif word.replace("Ω", "").isdigit():  # ex: 100 or 200
                resistor_values.append(int(word.replace("Ω", "")))
            elif word.startswith("V"):
                voltage_name = word
            elif "V" in word and word.replace("V", "").isdigit():
                voltage_value = int(word.replace("V", ""))

    # Map resistors
    for i in range(min(len(resistors), len(resistor_values))):
        components[resistors[i]] = {
            "type": "resistor",
            "value": resistor_values[i]
        }

    # Map voltage source
    if voltage_name and voltage_value is not None:
        components[voltage_name] = {
            "type": "voltage_source",
            "value": voltage_value
        }

    return components
