# If you prefer to create a new video instead of images, you can reduce the frame rate and save it as a new file:

ffmpeg -i original_vid/IMG_9068.MOV -r 8 -c:v libx264 -crf 23 -preset fast reduced_vid_3.mp4


# You can use ffmpeg to extract frames at 2 FPS from your .mov video efficiently. Run the following command in your terminal:


ffmpeg -i input.mov -vf "fps=2" output_%04d.jpg
