import trimesh

mesh = trimesh.load_mesh("birlesmis_model.stl")
min_z = mesh.bounds[0][2]
max_z = mesh.bounds[1][2]
print(f"Model yüksekliği: {min_z} mm → {max_z} mm")
