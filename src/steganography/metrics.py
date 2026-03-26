import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import os
import sys

def calculate_frame_metrics(cover_frame, stego_frame):
    mse = np.mean((cover_frame.astype(float) - stego_frame.astype(float)) ** 2)
    
    if mse == 0:
        psnr = float('inf') 
    else:
        psnr = 10 * math.log10((255.0 ** 2) / mse)
        
    return mse, psnr

def plot_histograms(cover_frame, stego_frame):
    colors = ('b', 'g', 'r')
    
    plt.figure(figsize=(14, 6))
    plt.style.use('dark_background') 
    
    plt.subplot(1, 2, 1)
    plt.title('RGB Histogram - Cover Video', fontsize=14)
    plt.xlabel('Pixel Intensity (0-255)')
    plt.ylabel('Frequency')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([cover_frame], [i], None, [256], [0, 256])
        plt.plot(hist, color=col, alpha=0.8, linewidth=2)
        plt.xlim([0, 256])
    plt.grid(True, alpha=0.2)
        
    plt.subplot(1, 2, 2)
    plt.title('RGB Histogram - Stego Video', fontsize=14)
    plt.xlabel('Pixel Intensity (0-255)')
    plt.ylabel('Frequency')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([stego_frame], [i], None, [256], [0, 256])
        plt.plot(hist, color=col, linestyle='--', alpha=0.8, linewidth=2)
        plt.xlim([0, 256])
    plt.grid(True, alpha=0.2)
        
    plt.tight_layout()
    plt.show()

def analyze_videos(cover_path, stego_path):
    cap_cov = cv2.VideoCapture(cover_path)
    cap_steg = cv2.VideoCapture(stego_path)
    
    if not cap_cov.isOpened() or not cap_steg.isOpened():
        raise ValueError(f"Failed to open videos. Check if both {cover_path} and {stego_path} exist.")

    mse_list = []
    psnr_list = []
    
    ret_c, first_cover = cap_cov.read()
    ret_s, first_stego = cap_steg.read()
    
    if not ret_c or not ret_s:
        raise ValueError("Video is empty or cannot be read.")
        
    mse, psnr = calculate_frame_metrics(first_cover, first_stego)
    mse_list.append(mse)
    psnr_list.append(psnr)
    
    while True:
        ret_c, frame_c = cap_cov.read()
        ret_s, frame_s = cap_steg.read()
        
        if not ret_c or not ret_s:
            break
            
        mse, psnr = calculate_frame_metrics(frame_c, frame_s)
        mse_list.append(mse)
        psnr_list.append(psnr)

    cap_cov.release()
    cap_steg.release()

    avg_mse = sum(mse_list) / len(mse_list)
    finite_psnr = [p for p in psnr_list if p != float('inf')]
    avg_psnr = sum(finite_psnr) / len(finite_psnr) if finite_psnr else float('inf')

    return avg_mse, avg_psnr, first_cover, first_stego

if __name__ == "__main__":
    print("\n=== LSB METRICS ANALYZER ===")
    cover_vid = input("Enter the ORIGINAL cover video (e.g., vid.avi): ").strip()
    stego_vid = input("Enter the STEGO output video (e.g., stego_output.avi): ").strip()
    
    if not os.path.exists(cover_vid) or not os.path.exists(stego_vid):
        print("\n [!] ERROR: One or both files do not exist. Please check your spelling.")
        sys.exit(1)
        
    print(" [*] Analyzing videos. This might take a moment...")
    
    mse, psnr, cover_frame, stego_frame = analyze_videos(cover_vid, stego_vid)
    
    print(f"\n [✓] Analysis Complete!")
    print(f"     MSE : {mse:.4f}")
    print(f"     PSNR: {psnr:.2f} dB")
    
    print("\n [*] Opening Histogram charts...")
    plot_histograms(cover_frame, stego_frame)