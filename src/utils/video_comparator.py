import cv2
import numpy as np
import matplotlib.pyplot as plt

def compare_frames(frame_original, frame_stego)->list[float,float]:

    if frame_original.shape != frame_stego.shape:
        raise ValueError("Ukuran frame beda")

    mse = np.mean((frame_original.astype(np.float64) - frame_stego.astype(np.float64)) ** 2)

    if mse == 0:
        return 0, float('inf')

    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    
    return mse, psnr

def compare_videos_returns(path_original:str, path_stego:str)-> list[dict,list[list[int],list,list]]  : # dict data mse, frames[nomor frame,frame awal,frame akhir]
    cap_orig = cv2.VideoCapture(path_original)
    cap_stego = cv2.VideoCapture(path_stego)

    frame_count = 0
    total_mse = 0
    total_psnr = 0

    out = {"mse" : [],"psnr" : [],"Mean MSE" : 0,"Mean PSNR" : 0}
    frame_out = [[],[],[]]

    while cap_orig.isOpened() and cap_stego.isOpened():
        ret_o, frame_o = cap_orig.read()
        ret_s, frame_s = cap_stego.read()

        if not ret_o or not ret_s:
            break

        mse, psnr = compare_frames(frame_o, frame_s)
        out["mse"].append(mse)
        out["psnr"].append(psnr)

        total_mse += mse
        total_psnr += psnr
        frame_count += 1

        if mse !=0 :
            frame_out[0].append(frame_count)
            frame_out[1].append(frame_o)
            frame_out[2].append(frame_s)
            pass


    if frame_count > 0:
        print("-" * 45)
        out["Mean MSE"] = total_mse / frame_count
        out["Mean PSNR"] = total_psnr / frame_count


    cap_orig.release()
    cap_stego.release()
    return out,frame_out


def show_histograms(frames:list[list[int],list,list])->None:
    colors = ('b', 'g', 'r')
    plt.figure(figsize=(12, 4 * len(frames[0])))
    frame_amounts = len(frames[0])

    for frame_number in range(frame_amounts):
        plt.subplot(frame_amounts, 2, (frame_number * 2) + 1)
        plt.title("Histogram Asli Frame "+str(frames[0][frame_number]+1))
        for i, col in enumerate(colors):
            hist = cv2.calcHist([frames[1][frame_number]], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.ylabel("value")
        plt.xlabel("pixels")
        plt.xlim([0, 256])
        plt.grid(axis='y', alpha=0.3)

        plt.subplot(frame_amounts, 2, (frame_number * 2) + 2)
        plt.title("Histogram Stego "+str(frames[0][frame_number]+1))
        for i, col in enumerate(colors):
            hist = cv2.calcHist([frames[2][frame_number]], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.ylabel("value")
        plt.xlabel("pixels")
        plt.xlim([0, 256])
        plt.grid(axis='y', alpha=0.3)
        pass
   
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    a = compare_videos_returns('input.avi', 'hasil.avi')

    print("rata rata mse : "+ str(a[0]["Mean MSE"]))
    print("rata rata PSNR : "+ str(a[0]["Mean PSNR"]))
    show_histograms(a[1])