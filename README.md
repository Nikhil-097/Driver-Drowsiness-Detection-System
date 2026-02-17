# Drowsiness Detection System 🚗💤

## 📝 System Overview
The **Drowsiness Detection System** is a cutting-edge, real-time safety application engineered to prevent road accidents by monitoring driver fatigue using computer vision and interactive web technologies. At its core, the system detects exhaustion by analyzing eye movements and identifying instances of prolonged eye closure through the calculation of the **Eye Aspect Ratio (EAR)**.

---

## ⚙️ Core Detection Logic
The application captures live video via a webcam, processing the frames using **OpenCV** and **Dlib’s 68-point facial landmark detector**. 

* **Analysis:** By mapping specific coordinates around the eyes, the system calculates the EAR value in real-time. 
* **Alerting:** When this value drops below a predefined threshold for a sustained period, the system recognizes a state of drowsiness and immediately triggers both **visual and audio alerts** to warn the driver.

---

## 🖥️ Backend and Integration
Developed using **Flask**, the backend facilitates:
* **Live Streaming:** Seamless video delivery to the browser via MJPEG.
* **API Endpoints:** Custom endpoints provide instantaneous EAR data and alertness status.
* **Communication:** Ensures a fluid bridge between the computer vision logic and the frontend interface.

---

## 🎨 Frontend Visualization
The user dashboard utilizes **HTML, CSS, and JavaScript** to deliver an intuitive, responsive experience:
* **Three.js:** Powers dynamic particle animations reflecting the driver's alertness level.
* **GSAP:** Handles sleek, scroll-based transitions across the UI.
* **Chart.js:** Provides a live-updating EAR graph for continuous performance analysis.

This project showcases a cohesive safety-focused solution, highlighting the practical utility of **Artificial Intelligence** in creating responsive, real-time monitoring systems that significantly improve driver awareness and overall highway safety.
