# stl_bol.py

import trimesh
import numpy as np
import os

def stl_bol(nozzle_count=4, input_path="input/Chip1.stl", output_dir="output"):
    mesh = trimesh.load_mesh(input_path)

    min_x, max_x = mesh.bounds[0][0], mesh.bounds[1][0]
    step = (max_x - min_x) / nozzle_count

    os.makedirs(output_dir, exist_ok=True)

    for i in range(nozzle_count):
        x_start = min_x + i * step
        x_end = x_start + step

        mask = np.logical_and(
            mesh.triangles_center[:, 0] >= x_start,
            mesh.triangles_center[:, 0] < x_end
        )

        sliced = mesh.submesh([mask], append=True)
        sliced.export(os.path.join(output_dir, f"parca_{i+1}.stl"))

    print(f"{nozzle_count} parçaya bölündü ve '{output_dir}' klasörüne kaydedildi.")

# Doğrudan çalıştırmak için
if __name__ == "__main__":
    stl_bol()
