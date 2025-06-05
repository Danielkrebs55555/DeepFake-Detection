# 🧠 Deepfake Detection Through Hybrid MobileNet-LSTM Model

## 📌 About

This project uses a hybrid model combining **MobileNet** and **LSTM** to detect deepfakes, addressing the growing threat of AI-generated manipulated media. MobileNet extracts spatial features from images and video frames, while LSTM analyzes temporal patterns to identify inconsistencies.

---

## 🧪 Abstract

The proliferation of deepfakes poses a significant threat to digital content authenticity. This system leverages a hybrid architecture that integrates MobileNet—a lightweight CNN—for visual feature extraction, and LSTM for modeling temporal sequences. It supports both image and video inputs and delivers accurate real-time deepfake detection through a streamlined user interface.

---

## 🧰 Tech Stack

- **TensorFlow / PyTorch** – Model development
- **OpenCV** – Frame extraction & preprocessing
- **NumPy / Pandas** – Data manipulation
- **Streamlit** – Real-time web app interface
- **Matplotlib / Seaborn** – Performance visualization

---

## 🏗️ System Architecture

1. **Input**: Image or video
2. **Preprocessing**: Resize, normalize, frame extraction
3. **Feature Extraction**: MobileNet extracts spatial features
4. **Temporal Modeling**: LSTM captures motion-based anomalies
5. **Output**: Real or fake classification with detection score

---

## 📦 Module Description

- **Input Layer**: Accepts images/videos and extracts frames
- **Preprocessing Layer**: Standardizes inputs for analysis
- **MobileNet Layer**: Detects visual artifacts and inconsistencies
- **LSTM Layer**: Identifies abnormal temporal patterns
- **Output Layer**: Provides classification with explanation cues

![image](https://github.com/user-attachments/assets/29ab12ca-ba37-40b6-b757-d705a3323445)


---

## 🚀 Features

- Dual-mode detection: Works on both images and videos
- Real-time detection interface via Streamlit
- Visual feedback for interpretability
- Lightweight architecture optimized for speed and accuracy

---

## 🔮 Future Enhancements

- Optimize LSTM model for faster processing
- Expand dataset diversity for improved generalization
- Add support for live video stream input
- Deploy as a browser extension or mobile app

## 🎥 Demo
   
  ![Image](https://github.com/user-attachments/assets/fb860436-4f40-4ce3-8e51-5179f63f4047)

---

## 📝 References

A full list of academic references can be found in the documentation. Key works include research on CNN-LSTM models, deepfake detection benchmarks, and temporal feature analysis.

---

## License

This project is licensed under the MIT License.

---


