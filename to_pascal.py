import os
import pandas as pd
from lxml import etree

# Input CSV file path
csv_file = 'annotated_output/pidgeon_annotations3.csv'

# Output directory for Pascal VOC XML annotations
output_dir = 'output_pascal_voc'
os.makedirs(output_dir, exist_ok=True)

# Read CSV
df = pd.read_csv(csv_file)

# Map class_id to class name (adjust this mapping based on your dataset)
class_names = {
    14: 'bird',  # Example: Replace with your actual mapping
}

# Function to create XML for each frame
def create_pascal_voc_xml(frame_id, annotations):
    root = etree.Element("annotation")
    
    # Add basic info
    folder = etree.SubElement(root, "folder")
    folder.text = "images"
    filename = etree.SubElement(root, "filename")
    filename.text = f"frame_{frame_id}.jpg"
    
    # Loop through the annotations for the frame
    for ann in annotations:
        obj = etree.SubElement(root, "object")
        
        # Object details
        name = etree.SubElement(obj, "name")
        name.text = class_names.get(ann['class_id'], "unknown")
        
        bndbox = etree.SubElement(obj, "bndbox")
        etree.SubElement(bndbox, "xmin").text = str(int(ann['x1']))
        etree.SubElement(bndbox, "ymin").text = str(int(ann['y1']))
        etree.SubElement(bndbox, "xmax").text = str(int(ann['x2']))
        etree.SubElement(bndbox, "ymax").text = str(int(ann['y2']))

    # Convert XML tree to a string
    xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    # Write to file
    with open(os.path.join(output_dir, f"frame_{frame_id}.xml"), 'wb') as f:
        f.write(xml_str)

# Iterate through frames and create XML files
for frame_id, group in df.groupby('frame_id'):
    annotations = group[['x1', 'y1', 'x2', 'y2', 'class_id']].to_dict(orient='records')
    create_pascal_voc_xml(frame_id, annotations)

print("Conversion to Pascal VOC format completed.")
