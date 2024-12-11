import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

def create_ppt_from_images(image_folder, output_ppt):

    prs = Presentation()

    image_files = sorted(os.listdir(image_folder))

    # Loop through all files in the sorted list
    for image_file in image_files:
        # Check if the file is an image (you can add more extensions if needed)
        if image_file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(image_folder, image_file)

            # Add a slide with blank layout
            slide = prs.slides.add_slide(prs.slide_layouts[6])

            # Add the image to the slide
            img = slide.shapes.add_picture(image_path, Inches(0), Inches(0), height=Inches(5))

    # Save the PowerPoint presentation
    prs.save(output_ppt)
    print(f"PPT saved as {output_ppt}")





def capture_frames(video_path, output_dir, interval):
    
    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' does not exist.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file '{video_path}'.")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames
    duration = total_frames / fps  # Duration of the video in seconds

    print(f"Video Details: FPS={fps}, Total Frames={total_frames}, Duration={duration:.2f}s")

    # Calculate the frame interval based on the given time interval
    frame_interval = fps * interval

    frame_count = 0
    saved_frame_count = 0
    previous_file = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Save frames at the specified interval
        if frame_count % frame_interval == 0:
            frame_time = frame_count / fps
            output_file = os.path.join(output_dir, f"frame_{saved_frame_count:04d}_{frame_time:.2f}s.jpg")
            
            next_file = os.path.join(output_dir, f"frame_{saved_frame_count + 1:04d}_{frame_time + interval:.2f}s.jpg")
            # print(previous_file)
            # print
            if previous_file and saved_frame_count >= 1:
                print("entered if")
                frame1_path = previous_file

                frame1 = cv2.imread(frame1_path)
                frame2 = frame

                if frame1 is None or frame2 is None:
                    print("Error: One of the frames could not be loaded.")
                else:
                    print("Entered else")
                    mse_val, ssim_val, hist_corr = compare_frames(frame1, frame2)

                    # # Optionally show frames side by side
                    # fig, axes = plt.subplots(1, 2)
                    # axes[0].imshow(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
                    # axes[0].set_title("Frame 1")
                    # axes[1].imshow(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
                    # axes[1].set_title("Frame 2")
                    # plt.show()
                    # print(hist_corr)
                    if hist_corr <= 0.998 or ssim_val <= 0.97:
                    # Save the current frame
                        cv2.imwrite(output_file, frame)
                        print(f"Saved: {output_file}")
                        saved_frame_count += 1
                        previous_file = output_file
                    
                    # Update previous file for the next iteration
            if saved_frame_count < 1:
                cv2.imwrite(output_file, frame)
                saved_frame_count += 1
                previous_file = output_file

            
            

        frame_count += 1

    # Release the video capture object
    cap.release()
    print("Frame capture complete.")

def mse(imageA, imageB):
    """Calculate the Mean Squared Error (MSE) between two images."""
    # The 'Mean Squared Error' between the two images is the sum of the squared differences between the pixel intensities.
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err


def compare_histograms(imageA, imageB):
    """Compare histograms of two images."""
    histA = cv2.calcHist([imageA], [0], None, [256], [0, 256])
    histB = cv2.calcHist([imageB], [0], None, [256], [0, 256])
    # Normalize the histograms
    histA = cv2.normalize(histA, histA).flatten()
    histB = cv2.normalize(histB, histB).flatten()
    # Compute correlation between histograms
    return cv2.compareHist(histA, histB, cv2.HISTCMP_CORREL)

def compare_frames(frameA, frameB):
    """Compare two frames using different similarity metrics."""
    # Resize frames to the same size if they differ
    if frameA.shape != frameB.shape:
        frameB = cv2.resize(frameB, (frameA.shape[1], frameA.shape[0]))

    # Convert to grayscale for MSE and SSIM comparisons
    grayA = cv2.cvtColor(frameA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(frameB, cv2.COLOR_BGR2GRAY)

    # Compute the MSE between the two images
    mse_value = mse(grayA, grayB)
    print(f"Mean Squared Error (MSE): {mse_value}")

    # Compute the SSIM between the two images
    ssim_value, _ = ssim(grayA, grayB, full=True)
    print(f"Structural Similarity Index (SSIM): {ssim_value}")

    # Compute histogram comparison (correlation)
    histogram_correlation = compare_histograms(frameA, frameB)
    print(f"Histogram Correlation: {histogram_correlation}")

    return mse_value, ssim_value, histogram_correlation




if __name__ == "__main__":
    video_path = r"D:\Masters\Fall 2024\data_center_scale_computing\Project\dcsc_final_project\videoplayback.mp4"  # Replace with your video file path
    output_dir = r"D:\Masters\Fall 2024\data_center_scale_computing\Project\dcsc_final_project\frames_1"  # Directory to save frames
    interval = 4  # Capture frames every 5 seconds

    capture_frames(video_path, output_dir, interval)

    image_folder = output_dir
    output_ppt = r"D:\Masters\Fall 2024\data_center_scale_computing\Project\dcsc_final_project\images_presentation.pptx"

    create_ppt_from_images(image_folder, output_ppt)









