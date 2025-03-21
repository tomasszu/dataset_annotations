from ultralytics import YOLO
import pandas as pd

model = YOLO(f'yolov8x.pt')

# Define output directory
output_dir = "annotated_output"

# Run inference with tracking enabled
results = model.track(
    source='reduced_vid_3.mp4',
    save=True, 
    save_txt=False,  # We handle saving manually
    conf=0.3,
    classes=[14],  # COCO class ID for birds
    project=output_dir,
    name="pidgeon_annotations3",
    tracker="bytetrack.yaml"  # Use ByteTrack for tracking
)


csv_data = []
# Iterate over the results to extract frame data and tracking information
frame_id = 0  # Initialize frame ID

# Iterate through the results
for result in results:
    for box in result.boxes.data:
        x1, y1, x2, y2, conf, cls, track_id = box.tolist()
        
        # Save frame_id, track_id, bounding box, confidence, and class_id to CSV
        csv_data.append([
            result.path,  # video filename
            frame_id,  # frame number
            conf,  # confidence
            x1, y1, x2, y2,  # bounding box coordinates
            int(cls),  # class ID
            int(track_id)  # track ID
        ])
    
    # Increment frame_id for each frame processed
    frame_id += 1

# Convert to DataFrame
df = pd.DataFrame(csv_data, columns=["filename", "frame_id", "track_id", "x1", "y1", "x2", "y2", "confidence", "class_id"])

# Save as CSV
csv_path = f"{output_dir}/pidgeon_annotations3.csv"
df.to_csv(csv_path, index=False)

print(f"Annotations saved to {csv_path}")