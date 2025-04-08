import os
import csv
import random
from pathlib import Path
from collections import defaultdict

# Set single dataset folder
dataset_name = "pidgeon_vid_4"
input_dir = Path(f"pidgeon_datasets/pidgeon_images/{dataset_name}")
output_dir = Path(f"pidgeon_datasets/train_datasets/{dataset_name}_split_ids")
output_dir.mkdir(parents=True, exist_ok=True)

# Gather all (path, id) pairs
data = []
for id_folder in input_dir.iterdir():
    if id_folder.is_dir():
        pid = int(id_folder.name)
        for img_file in id_folder.glob("*.png"):
            rel_path = img_file.relative_to(Path("pidgeon_datasets"))
            data.append((str(rel_path), pid))

# Group by ID
id_to_images = defaultdict(list)
for path, pid in data:
    id_to_images[pid].append(path)

# 70/30 split per ID
train_rows, val_rows = [], []
for pid, images in id_to_images.items():
    random.shuffle(images)
    split_idx = int(len(images) * 0.7)
    train_rows.extend([(img, pid) for img in images[:split_idx]])
    val_rows.extend([(img, pid) for img in images[split_idx:]])

# Write to CSV
def save_csv(rows, out_path):
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["path", "id"])
        writer.writerows(rows)

save_csv(train_rows, output_dir / "train.csv")
save_csv(val_rows, output_dir / "val.csv")

print(f"✅ {dataset_name}: Train={len(train_rows)}, Val={len(val_rows)}, Total IDs={len(id_to_images)}")
