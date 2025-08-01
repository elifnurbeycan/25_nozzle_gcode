

import trimesh
import numpy as np

# Ayarlar
layer_height = 0.2
extruder_count = 4  # Şimdilik 4 başlık için
birlesik_model_dosyasi = "birlesmis_model.stl"
gcode_dosyasi = "gcode_ilk_katman_detayli.gcode"

# STL modelini yükle
mesh = trimesh.load_mesh(birlesik_model_dosyasi)

# Modeli Z=0 seviyesine oturt
z_shift = -mesh.bounds[0][2]
mesh.apply_translation((0, 0, z_shift))

# İlk katman kesiti (Z=0.2)
z = layer_height
plane_origin = [0, 0, z]
plane_normal = [0, 0, 1]

section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)
if section is None:
    print("Bu katmanda kesit bulunamadı.")
    exit()

slice_2D = section.to_planar()
entities = slice_2D.entities
vertices = slice_2D.vertices

# G-code oluştur
gcode = []
gcode.append("; G-code: İlk Katman Detaylı\n")
gcode.append("M82 ; mutlak ekstrüzyon\n")
gcode.append("G90 ; mutlak konumlama\n")
gcode.append("G21 ; birimler mm\n")
gcode.append("G28 ; tüm eksenleri home'la\n")
gcode.append("G92 E0 ; ekstruder sıfırlama\n")
gcode.append("M104 S200 ; nozzle ısısı\n")
gcode.append("M140 S60 ; tabla ısısı\n")
gcode.append("M109 S200 ; nozzle ısısını bekle\n")
gcode.append("M190 S60 ; tabla ısısını bekle\n")
gcode.append("G1 Z{:.2f} F300\n".format(z))

E = 0.0
F = 1200  # feedrate
ekstruder = 0
genislik = mesh.extents[0]
genislik_birim = genislik / extruder_count

for i, entity in enumerate(entities):
    points = entity.discrete(vertices)
    if len(points) < 2:
        continue

    # Başlangıç noktası
    start = points[0]
    gcode.append(f"T{ekstruder} ; Extruder {ekstruder}\n")
    gcode.append(f"G0 X{start[0]:.3f} Y{start[1]:.3f} F{F}\n")
    for point in points[1:]:
        distance = np.linalg.norm(point - start)
        E += distance * 0.05  # ekstrüzyon katsayısı basitçe
        gcode.append(f"G1 X{point[0]:.3f} Y{point[1]:.3f} E{E:.5f} F{F}\n")
        start = point

    ekstruder = (ekstruder + 1) % extruder_count

gcode.append("M104 S0 ; nozzle kapat\n")
gcode.append("M140 S0 ; tabla kapat\n")
gcode.append("M84 ; motorları kapat\n")
gcode.append(";Bitti\n")

# G-code'u dosyaya yaz
with open(gcode_dosyasi, "w") as f:
    f.writelines(gcode)
print(f" G-code '{gcode_dosyasi}' dosyasına yazıldı.")
