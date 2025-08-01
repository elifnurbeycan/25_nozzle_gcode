import trimesh
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NOZZLE_COUNT = 4
NOZZLE_SPACING = 20.0

def stl_birlestir():
    parcalar = []

    for i in range(NOZZLE_COUNT):
        dosya_adi = os.path.join(OUTPUT_DIR, f"parca_{i+1}.stl")
        if not os.path.exists(dosya_adi):
            print(f"Hata: {dosya_adi} bulunamadı.")
            continue

        mesh = trimesh.load_mesh(dosya_adi)
        if mesh.is_empty:
            print(f"Uyarı: {dosya_adi} boş, atlanıyor.")
            continue

        mesh.apply_translation([i * NOZZLE_SPACING, 0, 0])
        parcalar.append(mesh)

    if not parcalar:
        print("Hiçbir geçerli parça bulunamadı.")
        return

    birlesmis = trimesh.util.concatenate(parcalar)
    birlesmis.export(os.path.join(OUTPUT_DIR, "birlesmis_model.stl"))
    print("Parçalar başarıyla birleştirildi.")

if __name__ == "__main__":
    stl_birlestir()
