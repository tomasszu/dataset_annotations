import os
import zipfile
import pandas as pd

# Define paths
input_csv_path = 'annotated_output/pidgeon_annotations3.csv'  # Your CSV file
output_dir = 'archive/gt'  # The directory where gt.txt will be stored
output_zip_path = 'archive.zip'  # The name of the zip file

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the input CSV
df = pd.read_csv(input_csv_path)

# Create and write to gt.txt in the required format
gt_txt_path = os.path.join(output_dir, 'gt.txt')
with open(gt_txt_path, 'w') as f:
    # Write the header comment (not data)
    f.write("# gt.txt\n")
    f.write("# frame_id, track_id, x, y, w, h, \"not ignored\", class_id, visibility, <skipped>\n")

    # Iterate over each row in the dataframe and convert to the required format
    for _, row in df.iterrows():
        # Extract relevant values from the dataframe
        frame_id = int(row['frame_id'])  # Assuming frame_id is an integer
        track_id = int(row['track_id'])  # Assuming track_id is an integer
        x1 = row['x1']
        y1 = row['y1']
        x2 = row['x2']
        y2 = row['y2']
        confidence = row['confidence']
        class_id = int(row['class_id'])  # Assuming class_id is an integer
        # Calculate width and height from bounding box coordinates
        w = x2 - x1
        h = y2 - y1
        not_ignored = 1  # Since the annotation is not ignored
        visibility = confidence  # Assuming visibility is based on confidence
        
        # Write the data to the file in the required format
        line = f"{frame_id},{track_id},{x1},{y1},{w},{h},{not_ignored},{class_id},{visibility}\n"
        f.write(line)

# Create a ZIP archive containing the gt folder
with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add the gt directory and its contents to the ZIP
    for root, dirs, files in os.walk('archive'):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, 'archive'))

print(f"ZIP file '{output_zip_path}' created successfully!")
