# -*- coding: utf-8 -*-

# Gerekli kütüphaneleri içe aktarıyoruz
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import trimesh
import numpy as np

# -- Global Ayarlar --
# Bu ayarlar, tüm scriptler tarafından kullanılacak şekilde merkezi olarak tanımlanmıştır.
NOZZLE_COUNT = 4
NOZZLE_SPACING = 20.0  # mm
LAYER_HEIGHT = 0.2     # mm
PRINT_SPEED = 1500     # mm/min
EXTRUSION_MULTIPLIER = 0.05 # Basit bir ekstrüzyon çarpanı

# Gerekli klasörleri oluştur
os.makedirs("gcode", exist_ok=True)
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

# -- Arayüz Fonksiyonları --

def stl_sec():
    """
    Kullanıcıya bir STL dosyası seçtiren fonksiyon.
    Seçilen dosya yolunu global değişkene kaydeder.
    """
    dosya_yolu = filedialog.askopenfilename(filetypes=[("STL Dosyaları", "*.stl")])
    if dosya_yolu:
        secilen_stl.set(dosya_yolu)
        messagebox.showinfo("Dosya Seçildi", f"{dosya_yolu} seçildi.")

def stl_bol():
    """
    Seçilen STL dosyasını belirlenen sayıda parçaya böler.
    Bölme işlemi için gerekli dosyayı hazırlar ve scripti çalıştırır.
    """
    if not secilen_stl.get():
        messagebox.showerror("Hata", "Lütfen önce bir STL dosyası seçin.")
        return
    
    try:
        input_stl_path = os.path.abspath(secilen_stl.get())
        hedef_yol = os.path.abspath("input/Chip1.stl")
        
        # Dosya zaten hedef yolda ve aynıysa kopyalama yapma
        if input_stl_path != hedef_yol:
            shutil.copy(input_stl_path, hedef_yol)
        
        # stl_bol fonksiyonunu doğrudan çağır
        stl_bol_script(NOZZLE_COUNT, input_path=hedef_yol, output_dir="output")
        messagebox.showinfo("Başarılı", f"STL dosyası {NOZZLE_COUNT} parçaya ayrıldı ve 'output' klasörüne kaydedildi.")
        
    except Exception as e:
        messagebox.showerror("Hata", f"STL parçalama sırasında bir hata oluştu: {e}")

def stl_birlestir():
    """
    Bölünmüş STL parçalarını birleştirir ve tek bir dosya olarak kaydeder.
    """
    try:
        # stl_birlestir fonksiyonunu doğrudan çağır
        stl_birlestir_script(NOZZLE_COUNT, NOZZLE_SPACING, output_dir="output")
        messagebox.showinfo("Başarılı", "Parçalar başarıyla birleştirildi ve 'birlesmis_model.stl' olarak kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"STL birleştirme sırasında bir hata oluştu: {e}")


def gcode_uret():
    try:
        from gcode_from_stl import gcode_uret as detayli_uret
        detayli_uret()  # Varsayılan parametrelerle çağır
        messagebox.showinfo("Başarılı", "Detaylı G-code başarıyla üretildi ve 'output' klasörüne kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"G-code üretimi sırasında hata oluştu:\n{e}")


# -- Scriptler --

def stl_bol_script(nozzle_count, input_path="input/Chip1.stl", output_dir="output"):
    """
    STL dosyasını X ekseni boyunca belirlenen sayıda parçaya böler.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Giriş dosyası bulunamadı: {input_path}")
        
    mesh = trimesh.load_mesh(input_path)
    if mesh.is_empty:
        raise ValueError("Giriş STL dosyası boş.")

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
        output_file = os.path.join(output_dir, f"parca_{i+1}.stl")
        sliced.export(output_file)

    print(f"✅ {nozzle_count} parçaya bölündü ve '{output_dir}' klasörüne kaydedildi.")

def stl_birlestir_script(nozzle_count, nozzle_spacing, output_dir="output"):
    """
    Bölünmüş STL parçalarını birleştirir ve X ekseninde ofset uygular.
    """
    parcalar = []

    for i in range(nozzle_count):
        dosya_adi = os.path.join(output_dir, f"parca_{i+1}.stl")
        if not os.path.exists(dosya_adi):
            raise FileNotFoundError(f"Parça dosyası bulunamadı: {dosya_adi}")
        
        mesh = trimesh.load_mesh(dosya_adi)
        if mesh.is_empty:
            print(f"Uyarı: {dosya_adi} boş, atlanıyor.")
            continue
        
        mesh.apply_translation([i * nozzle_spacing, 0, 0])
        parcalar.append(mesh)

    if not parcalar:
        raise ValueError("Hiçbir geçerli parça bulunamadı. Lütfen önce parçalama işlemini yapın.")

    birlesmis = trimesh.util.concatenate(parcalar)
    output_path = os.path.join(output_dir, "birlesmis_model.stl")
    birlesmis.export(output_path)
    print("Parçalar başarıyla birleştirildi.")

def gcode_from_stl_script(input_path, layer_height, print_speed):
    """
    STL dosyasını dilimleyerek 4 başlıklı 3D yazıcı için G-code üretir.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Giriş STL dosyası bulunamadı: {input_path}")
        
    mesh = trimesh.load_mesh(input_path)
    if mesh.is_empty:
        raise ValueError("Birleştirilmiş STL dosyası boş.")

    bounds = mesh.bounds
    min_z = bounds[0][2]
    max_z = bounds[1][2]
    z = min_z

    output_file = os.path.join("gcode", "final_gcode.gcode")

    with open(output_file, "w") as f:
        # Başlangıç komutları
        f.write("; G-code başlatılıyor\n")
        f.write("G21 ; mm cinsinden çalışma\n")
        f.write("G90 ; mutlak konumlama\n")
        f.write("M82 ; mutlak ekstrüzyon\n")
        f.write("G28 ; home all\n")
        f.write("G92 E0\n")
        f.write("M104 S200\n")
        f.write("M140 S60\n")
        f.write("M109 S200\n")
        f.write("M190 S60\n")
        f.write(f"G1 Z{layer_height:.2f} F300\n")

        E_values = [0.0 for _ in range(NOZZLE_COUNT)]

        while z < max_z:
            slice = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if slice is None:
                z += layer_height
                continue

            paths = slice.to_2D()
            if not isinstance(paths, list):
                paths = [paths]

            extruder_index = 0

            for path in paths:
                if not hasattr(path, 'entities'):
                    continue

                for entity in path.entities:
                    points = entity.discrete(20)
                    if len(points) < 2:
                        continue

                    offset_x = extruder_index * NOZZLE_SPACING
                    start = points[0]
                    f.write(f"\n; Extruder {extruder_index}\n")
                    f.write(f"T{extruder_index}\n")
                    f.write(f"G0 X{start[0] + offset_x:.3f} Y{start[1]:.3f} F{print_speed}\n")

                    for point in points[1:]:
                        distance = np.linalg.norm(point - start)
                        E_values[extruder_index] += distance * EXTRUSION_MULTIPLIER
                        f.write(
                            f"G1 X{point[0] + offset_x:.3f} Y{point[1]:.3f} "
                            f"E{E_values[extruder_index]:.5f} F{print_speed}\n"
                        )
                        start = point

                    extruder_index = (extruder_index + 1) % NOZZLE_COUNT

            z += layer_height

        # Bitirme komutları
        f.write("\nM104 S0 ; nozzle kapat\n")
        f.write("M140 S0 ; tabla kapat\n")
        f.write("M84 ; motorları kapat\n")

# -- Arayüz --

pencere = tk.Tk()
pencere.title("4 Başlıklı G-Code Üretici")
pencere.geometry("400x250")

# Değişkenler
secilen_stl = tk.StringVar()
secilen_stl.set("Henüz dosya seçilmedi")

# Arayüz elemanları
baslik_etiketi = tk.Label(pencere, text="4 Başlıklı 3D Yazıcı G-code Hazırlama", font=("Arial", 12))
baslik_etiketi.pack(pady=10)

dosya_etiketi = tk.Label(pencere, textvariable=secilen_stl, wraplength=350)
dosya_etiketi.pack(pady=5)

stl_sec_butonu = tk.Button(pencere, text="1. STL Dosyası Seç", command=stl_sec)
stl_sec_butonu.pack(pady=5)

stl_bol_butonu = tk.Button(pencere, text="2. STL Parçala (4 Parça)", command=stl_bol)
stl_bol_butonu.pack(pady=5)

stl_birlestir_butonu = tk.Button(pencere, text="3. STL Parçalarını Birleştir", command=stl_birlestir)
stl_birlestir_butonu.pack(pady=5)

gcode_uret_butonu = tk.Button(pencere, text="4. G-code Üret", command=gcode_uret)
gcode_uret_butonu.pack(pady=5)

# Doğrudan çalıştırma için ana döngü
if __name__ == "__main__":
    pencere.mainloop()
