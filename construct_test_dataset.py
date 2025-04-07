import os
import csv
from pathlib import Path

# === Config ===
video_name = "pidgeon_vid_4"
image_base_path = Path("pidgeon_datasets/pidgeon_images") / video_name
output_base_path = Path("pidgeon_datasets/test_datasets") / f"pidgeon_test_4"
output_base_path.mkdir(parents=True, exist_ok=True)

# Define parts with frame ranges (inclusive)
parts = {
    "part1": (0, 180),
    "part2": (320, 480),
    "part3": (613, float("inf"))
}


# === Collect data per part ===
part_data = {name: [] for name in parts}

for track_id_dir in sorted(image_base_path.iterdir()):
    if not track_id_dir.is_dir():
        continue

    track_id = int(track_id_dir.name)

    for img_file in sorted(track_id_dir.glob("*.png")):
        try:
            frame_id = int(img_file.stem)
        except ValueError:
            continue  # Skip non-numeric filenames

        for part_name, (start, end) in parts.items():
            if start <= frame_id <= end:
                rel_path = img_file.as_posix()
                part_data[part_name].append((rel_path, track_id))
                break  # A frame can belong to only one part

# === Write to CSVs ===
for part_name, samples in part_data.items():
    output_file = output_base_path / f"{part_name}.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "id"])
        writer.writerows(samples)

print(f"✅ Done. Created {len(parts)} test parts in: {output_base_path}")

print("\n=== Part Statistics ===")
for part_name, samples in part_data.items():
    ids = [track_id for _, track_id in samples]
    unique_ids = set(ids)
    print(f"{part_name}:")
    print(f"  Total instances: {len(ids)}")
    print(f"  Unique IDs: {len(unique_ids)}")
