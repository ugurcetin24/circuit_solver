from ocr_reader import read_text_from_image
from ocr_parser import parse_ocr_text
from circuit_solver import Circuit

if __name__ == "__main__":
    # 1. OCR çıktısını al
    ocr_result = read_text_from_image("images/circuit1.png", save_output=False)

    # 2. OCR çıktısını analiz et
    components = parse_ocr_text(ocr_result)

    # 3. OCR sonuçlarını ekrana yazdır
    print("Parsed components:")
    for name, info in components.items():
        print(f"{name}: type={info['type']}, value={info['value']}")

    # 4. Kendi Circuit nesnemizi oluşturalım
    my_circuit = Circuit()

    # 5. Bileşenleri tek tek Circuit nesnesine ekleyelim
    for name, info in components.items():
        if info['type'] == 'resistor':
            my_circuit.add_resistor(name, 1, 0, info['value'])
        elif info['type'] == 'voltage_source':
            my_circuit.add_voltage_source(name, 1, 0, info['value'])

    # 6. Oluşturulan devreyi gösterelim
    print("\nCircuit elements:")
    my_circuit.show_components()

    # 7. Devreyi çözelim
    print("\nSolving the circuit...")
    solution = my_circuit.solve_simple_series()

    # 8. Çözüm sonuçlarını yazdıralım
    print("\nSolution:")
    for key, value in solution.items():
        print(f"{key}: {value:.4f}")
