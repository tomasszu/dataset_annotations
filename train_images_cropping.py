import os
import cv2
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# === Paths ===
video_path = "vid_4.MOV"
csv_path = "annotated_output/pidgeon_annotations4.csv"  # Update if filename is different
output_root = "pidgeon_images"
output_folder = "pidgeon_vid_4"
output_path = os.path.join(output_root, output_folder)

# === Create output directory structure ===
os.makedirs(output_path, exist_ok=True)

# === Load annotations ===
df = pd.read_csv(csv_path)
df["frame_id"] = df["frame_id"].astype(int)
df["track_id"] = df["track_id"].astype(int)

# === Open video ===
cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# === Group annotations by frame ===
grouped = df.groupby("frame_id")

# === Track instances per pigeon ===
instance_counts = defaultdict(int)

# === Process frames with annotations ===
for frame_id in tqdm(sorted(grouped.groups.keys()), desc="Processing frames"):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
    success, frame = cap.read()
    if not success:
        print(f"Failed to read frame {frame_id}")
        continue

    frame_annotations = grouped.get_group(frame_id)

    for _, row in frame_annotations.iterrows():
        track_id = int(row["track_id"])
        x1, y1, x2, y2 = map(int, [row["x1"], row["y1"], row["x2"], row["y2"]])
        crop = frame[y1:y2, x1:x2]

        # Create subfolder for track_id
        pigeon_folder = os.path.join(output_path, str(track_id))
        os.makedirs(pigeon_folder, exist_ok=True)

        # Save image named by frame_id
        output_file = os.path.join(pigeon_folder, f"{frame_id}.png")
        cv2.imwrite(output_file, crop)

        instance_counts[track_id] += 1

cap.release()

# === Output instance counts per pigeon ID ===
print("\nInstance count per pidgeon ID:")
for track_id, count in sorted(instance_counts.items()):
    print(f"ID {track_id}: {count} instance(s)")
