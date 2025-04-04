import tkinter as tk
from tkinter import Canvas
import cv2
import pandas as pd
from PIL import Image, ImageTk

class VideoAnnotationApp:
    def __init__(self, video_path, csv_path, resized_width=1440, resized_height=900):
        self.video_path = video_path
        self.csv_path = csv_path
        self.resized_width = resized_width
        self.resized_height = resized_height

        self.cap = cv2.VideoCapture(video_path)
        self.annotations = pd.read_csv(csv_path)

        self.frame_annotations = self._load_annotations()
        self.bboxes = []
        self.selected_box = None
        self.moving = False
        self.resizing = False
        self.start_x, self.start_y = 0, 0
        self.current_frame = 0

        self._setup_tkinter_ui()

    def _load_annotations(self):
        annotations = {}
        x_scale = self.resized_width / int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_scale = self.resized_height / int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        for index, row in self.annotations.iterrows():
            frame_id = row['frame_id']
            bbox = (int(row['x1'] * x_scale), int(row['y1'] * y_scale),
                    int((row['x2'] - row['x1']) * x_scale), int((row['y2'] - row['y1']) * y_scale))
            if frame_id not in annotations:
                annotations[frame_id] = []
            annotations[frame_id].append((bbox, row['track_id']))  # Store track_id with bbox
        
        return annotations

    def _setup_tkinter_ui(self):
        self.root = tk.Tk()
        self.root.title("Interactive Bounding Boxes")

        self.canvas = Canvas(self.root, width=self.resized_width, height=self.resized_height)
        self.canvas.pack()

        self.control_window = tk.Toplevel(self.root)
        self.control_window.title("Frame Controls")

        self.next_button = tk.Button(self.control_window, text="Next Frame", command=self.next_frame)
        self.next_button.pack(side="left", padx=10)

        self.previous_button = tk.Button(self.control_window, text="Previous Frame", command=self.previous_frame)
        self.previous_button.pack(side="left", padx=10)

        self.jump_label = tk.Label(self.control_window, text="Jump to Frame:")
        self.jump_label.pack(side="left", padx=5)

        self.jump_entry = tk.Entry(self.control_window)
        self.jump_entry.pack(side="left", padx=5)
        self.jump_button = tk.Button(self.control_window, text="Go", command=self.jump_to_frame)
        self.jump_button.pack(side="left", padx=10)

        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.update_frame()

    def is_inside_bbox(self, x, y, bbox):
        bx, by, bw, bh = bbox
        return bx <= x <= bx + bw and by <= y <= by + bh

    def is_on_edge(self, x, y, bbox):
        bx, by, bw, bh = bbox
        return (bx + bw - 10 <= x <= bx + bw and by + bh - 10 <= y <= by + bh)

    def on_click(self, event):
        x, y = event.x, event.y
        for i, (bbox, _) in enumerate(self.bboxes):
            if self.is_on_edge(x, y, bbox):
                self.selected_box = i
                self.resizing = True
                break
            elif self.is_inside_bbox(x, y, bbox):
                self.selected_box = i
                self.start_x, self.start_y = x - bbox[0], y - bbox[1]
                self.moving = True
                break

    def on_drag(self, event):
        x, y = event.x, event.y
        if self.moving and self.selected_box is not None:
            bx, by, bw, bh = self.bboxes[self.selected_box][0]
            self.bboxes[self.selected_box] = ((x - self.start_x, y - self.start_y, bw, bh), self.bboxes[self.selected_box][1])
            self.update_frame()
        elif self.resizing and self.selected_box is not None:
            bx, by, bw, bh = self.bboxes[self.selected_box][0]
            self.bboxes[self.selected_box] = ((bx, by, max(20, x - bx), max(20, y - by)), self.bboxes[self.selected_box][1])
            self.update_frame()

    def on_release(self, event):
        self.moving = False
        self.resizing = False
        self.selected_box = None

    def update_frame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_resized = cv2.resize(frame, (self.resized_width, self.resized_height))

        for bbox, track_id in self.bboxes:
            x, y, w, h = bbox
            cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.rectangle(frame_resized, (x + w - 10, y + h - 10), (x + w, y + h), (0, 0, 255), -1)
            cv2.putText(frame_resized, f"ID: {int(track_id)}", (x + w + 5, y + h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        frame_image = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
        frame_tk = ImageTk.PhotoImage(frame_image)

        self.canvas.create_image(0, 0, anchor="nw", image=frame_tk)
        self.canvas.image = frame_tk

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame >= int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)):
            self.current_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            return

        self.bboxes = self.frame_annotations.get(self.current_frame, [])
        self.update_frame()

    def previous_frame(self):
        self.current_frame -= 1
        if self.current_frame < 0:
            self.current_frame = 0

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            return

        self.bboxes = self.frame_annotations.get(self.current_frame, [])
        self.update_frame()

    def jump_to_frame(self):
        try:
            frame_number = int(self.jump_entry.get())
            if 0 <= frame_number < int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)):
                self.current_frame = frame_number
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                ret, frame = self.cap.read()
                if not ret:
                    return

                self.bboxes = self.frame_annotations.get(self.current_frame, [])
                self.update_frame()
        except ValueError:
            pass  # Ignore if input is not a valid integer

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoAnnotationApp("reduced_vid_3.mp4", "annotated_output/pidgeon_annotations3.csv")
    app.run()
