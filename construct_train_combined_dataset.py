import os
import csv
from pathlib import Path

# === Config ===
image_base_path = Path("pidgeon_datasets/pidgeon_images")
output_dir = Path("pidgeon_datasets/train_datasets/pidgeon_train_combined_t124_v3")
output_dir.mkdir(parents=True, exist_ok=True)

train_vids = {"pidgeon_vid_1", "pidgeon_vid_2", "pidgeon_vid_4"}
val_vids   = {"pidgeon_vid_3"}

# === ID remapping ===
global_id_counter = 0
id_mapping = {}  # (video_name, original_id) -> new_id

train_samples = []
val_samples = []

for vid_dir in sorted(image_base_path.iterdir()):
    if not vid_dir.is_dir():
        continue

    vid_name = vid_dir.name
    target_list = train_samples if vid_name in train_vids else val_samples if vid_name in val_vids else None
    if target_list is None:
        continue

    for track_id_dir in sorted(vid_dir.iterdir()):
        if not track_id_dir.is_dir():
            continue

        original_id = int(track_id_dir.name)
        mapping_key = (vid_name, original_id)

        # Assign new unique global ID if not already mapped
        if mapping_key not in id_mapping:
            id_mapping[mapping_key] = global_id_counter
            global_id_counter += 1

        remapped_id = id_mapping[mapping_key]
        image_files = sorted(track_id_dir.glob("*.png"))

        for img_path in image_files:
            relative_path = img_path.as_posix()
            target_list.append((relative_path, remapped_id))

# === Write CSVs ===
def write_csv(csv_path, samples):
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "id"])
        writer.writerows(samples)

write_csv(output_dir / "train.csv", train_samples)
write_csv(output_dir / "val.csv", val_samples)

# === Summary ===
print(f"Train samples: {len(train_samples)}")
print(f"Val samples: {len(val_samples)}")
print(f"Total unique remapped IDs: {global_id_counter}")
