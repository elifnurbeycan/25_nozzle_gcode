# gcode_from_stl.py

import trimesh
import numpy as np
import os

def gcode_uret(birlesik_model="output/birlesmis_model.stl", gcode_cikti="output/gcode_tum_model.gcode"):
    layer_height = 0.2
    extruder_count = 4

    if not os.path.exists(birlesik_model):
        print("❌ Birleştirilmiş STL dosyası bulunamadı.")
        return

    mesh = trimesh.load_mesh(birlesik_model)

    # Z ekseni 0'dan başlasın
    z_shift = -mesh.bounds[0][2]
    mesh.apply_translation((0, 0, z_shift))

    min_z = mesh.bounds[0][2]
    max_z = mesh.bounds[1][2]
    z_layers = np.arange(min_z + layer_height, max_z, layer_height)

    gcode = []
    gcode.append("; G-code: Çok Katmanlı\n")
    gcode.append("M82\nG90\nG21\nG28\nG92 E0\n")
    gcode.append("M104 S200\nM140 S60\nM109 S200\nM190 S60\n")

    E = 0.0
    F = 1200
    ekstruder = 0
    genislik = mesh.extents[0]
    genislik_birim = genislik / extruder_count

    for z in z_layers:
        gcode.append(f"\n; === Z = {z:.2f} mm ===\n")
        gcode.append(f"G1 Z{z:.2f} F300\n")

        plane_origin = [0, 0, z]
        plane_normal = [0, 0, 1]
        section = mesh.section(plane_origin=plane_origin, plane_normal=plane_normal)

        if section is None:
            continue

        slice_2D, _ = section.to_planar()
        entities = slice_2D.entities
        vertices = slice_2D.vertices

        for entity in entities:
            points = entity.discrete(vertices)
            if len(points) < 2:
                continue

            start = points[0]
            gcode.append(f"T{ekstruder} ; Extruder {ekstruder}\n")
            gcode.append(f"G0 X{start[0]:.3f} Y{start[1]:.3f} F{F}\n")
            for point in points[1:]:
                distance = np.linalg.norm(point - start)
                E += distance * 0.05  # bu katsayıyı nozüle göre ayarlayabilirsin
                gcode.append(f"G1 X{point[0]:.3f} Y{point[1]:.3f} E{E:.5f} F{F}\n")
                start = point

            ekstruder = (ekstruder + 1) % extruder_count

    gcode.append("\nM104 S0\nM140 S0\nM84\n; Bitti\n")

    with open(gcode_cikti, "w", encoding="utf-8") as f:
        f.writelines(gcode)

    print(f"✅ Tüm katmanlar için G-code '{gcode_cikti}' olarak kaydedildi.")
