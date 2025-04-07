import os
import csv
from pathlib import Path

# === Config ===
image_base_path = Path("pidgeon_datasets/pidgeon_images/pidgeon_vid_4")
output_dir = Path("pidgeon_datasets/train_datasets/pidgeon_train_4")
output_dir.mkdir(parents=True, exist_ok=True)

train_ids = {1,2,4,5,6,7,8,10,12,13,16}
val_ids   = {3,9,11,17,25}

# === Collect samples ===
train_samples = []
val_samples = []

for track_id_dir in image_base_path.iterdir():
    if not track_id_dir.is_dir():
        continue

    track_id = int(track_id_dir.name)
    image_files = sorted(track_id_dir.glob("*.png"))

    for img in image_files:
        relative_path = img.as_posix()  # string with '/' separators
        sample = (relative_path, track_id)

        if track_id in train_ids:
            train_samples.append(sample)
        elif track_id in val_ids:
            val_samples.append(sample)
        else:
            continue  # ignore unknown ids

# === Write CSVs ===
def write_csv(path, samples):
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["path", "id"])
        writer.writerows(samples)

write_csv(output_dir / "train.csv", train_samples)
write_csv(output_dir / "val.csv", val_samples)

print(f"train.csv: {len(train_samples)} samples")
print(f"val.csv: {len(val_samples)} samples")
