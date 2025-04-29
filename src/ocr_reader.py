import cv2
import pytesseract
import os
import matplotlib.pyplot as plt

# Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# OCR için özel ayarlar
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789Ω'

def read_text_from_image(image_path, save_output=True):
    """
    Reads an image, processes it and applies OCR to extract text.
    Returns OCR output as string.
    """
    # Görseli oku (renkli)
    img = cv2.imread(image_path)

    # 1️⃣ Griye çevir
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2️⃣ Canny edge detection
    edges = cv2.Canny(gray, 100, 200)

    # 3️⃣ Görselleri sırayla göster
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.title("Original")
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Grayscale")
    plt.imshow(gray, cmap='gray')
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Canny Edges")
    plt.imshow(edges, cmap='gray')
    plt.axis("off")

    plt.tight_layout()
    plt.show()

    # 4️⃣ OCR işlemi (gri görsel üzerinden)
    text = pytesseract.image_to_string(gray, config=custom_config)

    # 5️⃣ Sonuç yazdır
    print("Detected text:")
    print(text)

    # 6️⃣ Kaydet (opsiyonel)
    if save_output:
        os.makedirs("results", exist_ok=True)
        with open("results/ocr_output.txt", "w", encoding="utf-8") as f:
            f.write(text)

    return text
