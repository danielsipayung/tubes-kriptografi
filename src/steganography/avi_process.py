import cv2
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AviProcess:

    def extract_frames(self, video_path, frames_folder):
        frame_folder_path = os.path.join(BASE_DIR, "avi_frames", frames_folder)
        abs_video_path = os.path.abspath(video_path)

        if os.path.exists(frame_folder_path):
            shutil.rmtree(frame_folder_path)
        os.makedirs(frame_folder_path)

        cap = cv2.VideoCapture(abs_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            fname = os.path.join(frame_folder_path, f"frame_{frame_count:04d}.bmp")
            cv2.imwrite(fname, frame)
            frame_count += 1

        cap.release()
        print(f"extracted {frame_count} frames, fps={fps}")
        return fps

    def rebuild_video(self, frames_folder, output_video_path, fps):
        frame_folder_path = os.path.join(BASE_DIR, "avi_frames", frames_folder)

        if not os.path.exists(frame_folder_path):
            print(f"folder not found: {frame_folder_path}")
            return

        images = sorted([img for img in os.listdir(frame_folder_path) if img.endswith(".bmp")])

        if not images:
            print("no frames found")
            return

        first_frame = cv2.imread(os.path.join(frame_folder_path, images[0]))
        height, width, _ = first_frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        for image in images:
            frame = cv2.imread(os.path.join(frame_folder_path, image))
            out.write(frame)

        out.release()
        print(f"video saved to {output_video_path}")


avi_processor = AviProcess()

def extract_frames(video_path, frames_folder):
    return avi_processor.extract_frames(video_path, frames_folder)

def rebuild_video(frames_folder, output_video_path, fps):
    return avi_processor.rebuild_video(frames_folder, output_video_path, fps)
