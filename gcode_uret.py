# -*- coding: utf-8 -*-
import os

# ➕ Ayarlar
NOZZLE_COUNT = 4
NOZZLE_SPACING = 20  # mm
DRAW_LENGTH = 10     # mm (her başlık kendi X alanında 10 mm çizsin)
Y_POSITION = 0
Z_HEIGHT = 0.3       # mm
FEEDRATE = 1500      # mm/min

# 📁 G-code klasörü
os.makedirs("gcode", exist_ok=True)
output_file = os.path.join("gcode", "toplu_gcode.gcode")

# 📄 Dosyaya yazma
with open(output_file, "w", encoding="utf-8") as f:
    f.write("; Eş zamanlı 4 başlık G-code örneği\n")
    f.write("G90 ; Mutlak konumlandırma\n")
    f.write("G28 ; Home all axes\n")
    f.write("M83 ; Ekstrüderi relative mode'a al\n\n")

    # Z eksenine iniş
    f.write(f"G1 Z{Z_HEIGHT} F{FEEDRATE}\n")

    # Her başlık başlangıç konumuna gitsin
    for i in range(NOZZLE_COUNT):
        x_start = i * NOZZLE_SPACING
        f.write(f"G1 X{x_start} Y{Y_POSITION} F{FEEDRATE}\n")

    f.write("\n; Paralel çizgiler başlıyor\n")

    # Her başlık çizim yapsın
    for i in range(NOZZLE_COUNT):
        x_start = i * NOZZLE_SPACING
        x_end = x_start + DRAW_LENGTH
        extrusion = 1.0
        f.write(f"G1 X{x_end} Y{Y_POSITION} E{extrusion:.2f} F{FEEDRATE}\n")

    # Sonlandırma komutları
    f.write("\nM104 S0 ; Nozzle kapat\n")
    f.write("M140 S0 ; Tabla kapat\n")
    f.write("M84 ; Motorları kapat\n")
    f.write("; Bitti\n")

print(f"✅ G-code dosyası oluşturuldu: {output_file}")
