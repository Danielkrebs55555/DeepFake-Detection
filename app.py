import streamlit as st
import tensorflow as tf
import cv2
import numpy as np
import tempfile
import os
from PIL import Image
import time
from pathlib import Path
from collections import deque

class DeepfakeDetector:
    def __init__(self, model_path):
        """Initialize the deepfake detector with a saved model."""
        self.model = tf.keras.models.load_model(model_path)
        self.img_height = 224
        self.img_width = 224
        # Window size for moving average
        self.window_size = 5
        # Confidence threshold for predictions
        self.confidence_threshold = 0.7

    def preprocess_image(self, image):
        """Preprocess image for model input with additional normalization."""
        if isinstance(image, str):
            img = tf.keras.preprocessing.image.load_img(
                image, 
                target_size=(self.img_height, self.img_width)
            )
            img_array = tf.keras.preprocessing.image.img_to_array(img)
        else:
            img_array = cv2.resize(image, (self.img_height, self.img_width))
            if len(img_array.shape) == 2:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)

        # Enhanced preprocessing
        img_array = img_array / 255.0
        # Add standardization
        img_array = (img_array - np.mean(img_array)) / np.std(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def predict(self, image):
        """Make prediction with confidence score."""
        processed_img = self.preprocess_image(image)
        prediction = self.model.predict(processed_img, verbose=0)[0][0]
        confidence = abs(prediction - 0.5) * 2  # Scale confidence between 0 and 1
        return prediction, confidence

def extract_frames(video_path, output_dir, frame_interval=2):
    """Extract frames with motion detection."""
    frames = []
    frame_paths = []

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    prev_frame = None
    motion_threshold = 30  # Adjust based on your needs

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate optimal frame interval based on video length
    optimal_interval = max(1, int(fps / 4))  # Extract 4 frames per second

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % optimal_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Motion detection
            if prev_frame is not None:
                frame_delta = cv2.absdiff(cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY),
                                        cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY))
                motion_score = np.mean(frame_delta)

                if motion_score > motion_threshold:
                    frames.append(frame_rgb)
                    frame_path = os.path.join(output_dir, f'frame_{frame_count}.jpg')
                    cv2.imwrite(frame_path, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
                    frame_paths.append(frame_path)
            else:
                # Always include first frame
                frames.append(frame_rgb)
                frame_path = os.path.join(output_dir, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_path, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
                frame_paths.append(frame_path)
            
            prev_frame = frame_rgb
            
        frame_count += 1
    
    cap.release()
    return frames, frame_paths, fps

def analyze_video_frames(detector, frames, progress_bar=None):
    """Analyze video frames with temporal smoothing."""
    results = []
    confidences = []
    prediction_window = deque(maxlen=detector.window_size)
    
    for i, frame in enumerate(frames):
        # Get prediction and confidence
        prediction, confidence = detector.predict(frame)
        
        # Apply temporal smoothing
        prediction_window.append(prediction)
        smoothed_prediction = np.mean(prediction_window)
        
        results.append(smoothed_prediction)
        confidences.append(confidence)
        
        if progress_bar:
            progress_bar.progress((i + 1) / len(frames))
    
    return results, confidences

def main():
    st.title("Enhanced Deepfake Detection System")
    
    model_path = r"D:\Final Year - Project\Phase 2\deepfake-det\deepfake-det\Models\best_mobilenet_lstm_model.keras"
    
    try:
        detector = DeepfakeDetector(model_path)
        st.success("Model loaded successfully!")
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return

    tab1, tab2 = st.tabs(["Image Detection", "Video Detection"])

    with tab1:
        st.header("Image Deepfake Detection")
        
        uploaded_image = st.file_uploader(
            "Upload an image", 
            type=['jpg', 'jpeg', 'png'],
            key="image_uploader"
        )

        if uploaded_image is not None:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(uploaded_image.getvalue())
                    img_path = tmp_file.name

                img = Image.open(uploaded_image)
                st.image(img, caption="Uploaded Image", use_column_width=True)

                if st.button("Detect Deepfake", key="image_detect"):
                    with st.spinner("Analyzing image..."):
                        prediction, confidence = detector.predict(img_path)

                        st.write("### Results")
                        prob_fake = prediction * 100
                        prob_real = (1 - prediction) * 100

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Probability of Fake", f"{prob_fake:.2f}%")
                        with col2:
                            st.metric("Probability of Real", f"{prob_real:.2f}%")
                        with col3:
                            st.metric("Confidence", f"{confidence*100:.2f}%")

                        verdict = "FAKE" if prediction > 0.5 else "REAL"
                        st.write(f"### Final Verdict: {verdict}")

                        if confidence < detector.confidence_threshold:
                            st.warning("⚠️ Low confidence prediction - result may not be reliable")

                os.unlink(img_path)

            except Exception as e:
                st.error(f"Error processing image: {str(e)}")

    with tab2:
        st.header("Video Deepfake Detection")
        
        uploaded_video = st.file_uploader(
            "Upload a video", 
            type=['mp4', 'avi', 'mov'],
            key="video_uploader"
        )

        if uploaded_video is not None:
            try:
                temp_dir = tempfile.mkdtemp()
                video_path = os.path.join(temp_dir, "video.mp4")
                with open(video_path, "wb") as f:
                    f.write(uploaded_video.read())

                st.video(video_path)

                if st.button("Detect Deepfake", key="video_detect"):
                    with st.spinner("Analyzing video..."):
                        frames, frame_paths, fps = extract_frames(video_path, temp_dir)
                        
                        if not frames:
                            st.error("No frames could be extracted from the video.")
                            return

                        progress_bar = st.progress(0)
                        results, confidences = analyze_video_frames(detector, frames, progress_bar)

                        # Calculate weighted average based on confidence scores
                        weighted_prediction = np.average(results, weights=confidences)
                        avg_confidence = np.mean(confidences)
                        
                        prob_fake = weighted_prediction * 100
                        prob_real = (1 - weighted_prediction) * 100

                        st.write("### Results")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Weighted Probability of Fake", f"{prob_fake:.2f}%")
                        with col2:
                            st.metric("Weighted Probability of Real", f"{prob_real:.2f}%")
                        with col3:
                            st.metric("Average Confidence", f"{avg_confidence*100:.2f}%")

                        # Plot predictions over time
                        st.write("### Frame Analysis Over Time")
                        plot_data = {
                            'Frame': list(range(len(results))),
                            'Fake Probability': [r * 100 for r in results],
                            'Confidence': [c * 100 for c in confidences]
                        }
                        
                        st.line_chart(plot_data)

                        # Show key frames
                        st.write("### Key Frames Analysis")
                        for i, (frame_path, pred, conf) in enumerate(zip(frame_paths, results, confidences)):
                            if i % 5 == 0 or conf > 0.9:  # Show every 5th frame or high confidence frames
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.image(frame_path, caption=f"Frame {i}")
                                with col2:
                                    st.write(f"Fake Probability: {pred*100:.2f}%")
                                    st.write(f"Confidence: {conf*100:.2f}%")

                        # Final verdict with confidence check
                        verdict = "FAKE" if weighted_prediction > 0.5 else "REAL"
                        st.write(f"### Final Verdict: {verdict}")
                        
                        if avg_confidence < detector.confidence_threshold:
                            st.warning("⚠️ Low average confidence - result may not be reliable")

                        # Cleanup
                        for path in frame_paths:
                            os.unlink(path)
                        os.unlink(video_path)
                        os.rmdir(temp_dir)

            except Exception as e:
                st.error(f"Error processing video: {str(e)}")

if __name__ == "__main__":
    main()