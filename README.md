# SareeVision AI — Color-Invariant Saree Design Recognition

An AI-powered computer vision system that identifies saree designs based on **patterns, motifs, borders, textures, and weaving structures**, while minimizing or eliminating the effect of fabric dye color.

Built with **PyTorch**, **FastAPI**, and a modern **React (Vite)** frontend.

---

## 🚀 Key Features

1. **Color-Invariant Computer Vision**:
   - Strips dye pigments using CIE LAB Luminance ($L^*$) decoupling with CLAHE.
   - Extracts motif geometry and borders via Sobel Gradient operators ($\nabla I = [\frac{\partial I}{\partial x}, \frac{\partial I}{\partial y}]$).
   - Extracts micro-weaving textures using Laplacian high-pass spatial filtering.
   - Synthesizes a 3-channel color-invariant composite representation.

2. **Dual-Head Deep Learning Model (PyTorch)**:
   - **Backbone**: MobileNetV3-Large transfer learning pre-trained feature extractor.
   - **Embedding Head**: 512-dimensional $L_2$-normalized feature vector for cosine similarity retrieval.
   - **Classification Head**: Softmax probability distribution over authentic Indian saree motifs:
     - *Temple Border*
     - *Peacock Motif*
     - *Floral Jaal*
     - *Paisley (Kalka)*
     - *Geometric Weave*
     - *Checks & Stripes*
     - *Butta Dots*
     - *Traditional Zari*

3. **Interactive Saree Color-Shifter**:
   - Real-time dynamic re-dyeing of saree fabric (Crimson Red, Royal Blue, Emerald Green, Mustard Yellow, Royal Purple, Peacock Teal, Tangerine Orange, Deep Magenta, or continuous 0°–360° hue rotation).
   - Side-by-side visual proof showing that changing fabric color preserves pattern recognition with high confidence.

4. **Nearest-Neighbor Design Similarity Search**:
   - Searches reference motifs across the 512-dimensional latent manifold using Cosine Similarity ($\text{Sim}(u, v) = u \cdot v$).
   - Returns top matching saree designs independent of color discrepancies.

5. **Cross-Chromatic Stress Testing**:
   - Benchmark module subjecting each saree motif to 12 synthetic color rotations ($0^\circ$ to $330^\circ$).
   - Achieves up to 100% stability on key motifs (Temple Border, Geometric Weave, Checks & Stripes, Paisley).

---

## 🛠️ Project Structure

```text
Color-Invariant Saree Design Recognition/
│
├── api/                             # FastAPI Web Service
│   ├── main.py                      # App entrypoint, CORS, static SPA mounting
│   ├── routes.py                    # Endpoints (/predict, /recolor, /presets, /health)
│   └── schemas.py                   # Pydantic input/output validation schemas
│
├── dataset/                         # Saree Dataset & Presets
│   ├── generate_presets.py          # Procedural saree design pattern generator
│   └── preset_sarees/               # 48 authentic saree designs across multiple colors
│
├── preprocessing/                   # Computer Vision Pipeline
│   ├── image_processor.py           # Image validation, resizing, bilateral denoising
│   └── color_invariance.py          # CIE LAB, Sobel gradients, dynamic recoloring
│
├── models/                          # PyTorch Neural Network
│   ├── architecture.py              # SareeDesignNet dual-head architecture
│   └── saree_model.pth              # Saved model weights checkpoint
│
├── training/                        # Training Pipeline
│   ├── train.py                     # Epoch loop, AdamW optimizer, CosineAnnealingLR
│   ├── dataset_loader.py            # SareeDataset and stratified DataLoaders
│   └── augmentation.py              # Color jitter, random grayscale & spatial transforms
│
├── evaluation/                      # Diagnostics & Benchmarking
│   ├── metrics.py                   # Accuracy, Precision, Recall, F1, 12-hue stress test
│   └── confusion_matrix.png         # Heatmap of model classification
│
├── inference/                       # Production Engine
│   ├── predictor.py                 # SareePredictor inference coordinator
│   └── similarity.py                # Cosine similarity nearest-neighbor search
│
├── frontend/                        # React Frontend (Vite)
│   ├── src/
│   │   ├── App.jsx                  # Main interactive dashboard with color shifter
│   │   ├── index.css                # Glassmorphism, jewel tones & animations
│   │   └── main.jsx                 # React root
│   ├── index.html                   # HTML template with Google Fonts (Outfit & Inter)
│   └── vite.config.js               # Dev server and API proxy configuration
│
├── tests/                           # Automated Test Suite
│   ├── test_preprocessing.py        # Transforms, validation & color shifter tests
│   ├── test_model.py                # SareeDesignNet forward pass & embedding tests
│   └── test_api.py                  # API endpoints integration tests
│
├── requirements.txt                 # Frozen Python dependencies
├── config.py                        # Centralized configurations & classes
└── README.md                        # Documentation
```

---

## 🚦 How to Run

### 1. Start the FastAPI Server (Backend + Built Frontend)
```powershell
.venv\Scripts\python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### 2. Start the React Frontend in Development Mode (Optional)
```powershell
npm --prefix frontend run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser with hot module reload.

### 3. Run Automated Tests
```powershell
$env:PYTHONPATH="."; .venv\Scripts\python -m pytest tests/
```

### 4. Run Model Training
```powershell
.venv\Scripts\python training/train.py
```

### 5. Run Evaluation & Color Invariance Stress Test
```powershell
.venv\Scripts\python evaluation/metrics.py
```
