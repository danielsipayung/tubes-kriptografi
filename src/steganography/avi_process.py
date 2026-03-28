import cv2
import os

def extract_frames(base,video_path, frames_folder):
    frame_folder_path = os.path.join(base,"avi_frames", frames_folder)
    
    if not os.path.exists(frame_folder_path):
        os.makedirs(frame_folder_path)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        read_was_successful, frame = cap.read()
        
        if not read_was_successful:
            break
            
        frame_filename = os.path.join(frame_folder_path, f"frame_{frame_count:04d}.bmp")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    cap.release()
    print(f"Frames extracted to /{frame_folder_path}")
    print(f"fps: {fps}")
    print(f"frame count: {frame_count}")
    
    return fps

def rebuild_video(frames_folder, output_video_path, fps):
    frame_folder_path = os.path.join("avi_frames", frames_folder)
    
    if not os.path.exists(frame_folder_path):
        print(f"Error: Folder '{frame_folder_path}' does not exist.")
        return

    images = [img for img in os.listdir(frame_folder_path) if img.endswith(".bmp")]
    images.sort()

    if not images:
        print(f"No frames found in {frame_folder_path}.")
        return

    first_frame_path = os.path.join(frame_folder_path, images[0])
    first_frame = cv2.imread(first_frame_path)
    height, width, layers = first_frame.shape
    frame_size = (width, height)

    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    output_video = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)

    for image in images:
        img_path = os.path.join(frame_folder_path, image)
        frame = cv2.imread(img_path)
        output_video.write(frame)

    output_video.release()
    print(f"Output video saved to {output_video_path}")

# test avi handling
# fps = 23.732 # fps test.avi
# fps = 30 # fps random.avi

# while True:
#     print("1. Extract frames from AVI")
#     print("2. Rebuild AVI from frames")
#     option = input("Choose an option: ")

#     if option == '1':
#         video_path = os.path.join("avi_video", input("Enter avi video file name: "))
#         folder_name = input("Enter the folder name where frames are kept (inside /avi_frames): ")
        
#         if os.path.exists(video_path):
#             fps = extract_frames(video_path, folder_name)
#         else:
#             print(f"Error: Could not find {video_path}")
#     elif option == '2':
#         folder_name = input("Enter the frame folder name inside /avi_frames to rebuild from: ")
#         output_path = os.path.join("output", input("Enter output video name (saves in /output): "))
#         rebuild_video(folder_name, output_path, fps)
#     else:
#         print("Invalid option.")