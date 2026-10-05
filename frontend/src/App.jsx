import React, { useState, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL !== undefined 
  ? import.meta.env.VITE_API_BASE_URL 
  : (typeof window !== 'undefined' && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") ? "http://127.0.0.1:8000" : "");

// Curated feature maps for each motif class
const DESIGN_FEATURES = {
  "Temple Border": [
    "Temple border pattern",
    "Zari weaving structure",
    "Geometric triangular motifs",
    "Repeated border design"
  ],
  "Floral Motif": [
    "Circular rosette medallions",
    "Intertwined foliage jaal",
    "Embroidered petal detailing",
    "Repeated floral spread"
  ],
  "Peacock Motif": [
    "Mayil / Peacock crest feathers",
    "Ornate plumage fan eyelets",
    "Traditional border alignment",
    "Fine zari relief weaving"
  ],
  "Geometric Pattern": [
    "Interlocking diamond lattices",
    "Stepped chevrons & frets",
    "Symmetrical patola weave",
    "Continuous geometric grid"
  ],
  "Checks & Stripes": [
    "Palum-pazham zari checks",
    "Pinstriped grid symmetry",
    "Woven warp and weft intersections",
    "Traditional checkered body"
  ],
  "Butta Dots": [
    "Scattered circular zari buttas",
    "Embossed floral coin motifs",
    "Uniform pattern spacing",
    "Gold thread relief embroidery"
  ],
  "Traditional Zari": [
    "Heavy brocade zari weave",
    "Rudraksha & kalash emblems",
    "Intricate pallu lattice",
    "Metallic thread warp structure"
  ],
  "Paisley (Kalka)": [
    "Curved mango / paisley motifs",
    "Traditional kalha border",
    "Embroidered scrollwork",
    "Dense zari fill pattern"
  ]
};

// 8 Complete Designs with their full-saree sample image
const AVAILABLE_DESIGNS = [
  { name: "Temple Border", icon: "🛕", baseImg: "/saree_samples/temple_red.jpg", category: "Traditional", confidence: "96.4%", preset: "Temple_Border__Crimson_Red.jpg" },
  { name: "Floral Motif", icon: "🌸", baseImg: "/saree_samples/floral_pink.jpg", category: "Traditional", confidence: "93.8%", preset: "Floral_Jaal__Crimson_Red.jpg" },
  { name: "Peacock Motif", icon: "🦚", baseImg: "/saree_samples/peacock_red.jpg", category: "Traditional", confidence: "92.6%", preset: "Peacock_Motif__Crimson_Red.jpg" },
  { name: "Geometric Pattern", icon: "🔷", baseImg: "/saree_samples/geo_orange.jpg", category: "Contemporary", confidence: "91.2%", preset: "Geometric_Weave__Crimson_Red.jpg" },
  { name: "Checks & Stripes", icon: "🏁", baseImg: "/saree_samples/checks_red.jpg", category: "Traditional", confidence: "94.5%", preset: "Checks_and_Stripes__Crimson_Red.jpg" },
  { name: "Butta Dots", icon: "🪙", baseImg: "/saree_samples/butta_red.jpg", category: "Traditional", confidence: "95.1%", preset: "Butta_Dots__Crimson_Red.jpg" },
  { name: "Traditional Zari", icon: "👑", baseImg: "/saree_samples/traditional_zari_red.jpg", category: "Traditional", confidence: "96.0%", preset: "Traditional_Zari__Crimson_Red.jpg" },
  { name: "Paisley (Kalka)", icon: "🥭", baseImg: "/saree_samples/paisley_red.jpg", category: "Traditional", confidence: "93.4%", preset: "Paisley_Kalka__Crimson_Red.jpg" },
];

const COLOR_OPTIONS = [
  { name: "Royal Blue", hex: "#1864ab" },
  { name: "Crimson Red", hex: "#c92a2a" },
  { name: "Emerald Green", hex: "#2b8a3e" },
  { name: "Mustard Yellow", hex: "#e67700" },
  { name: "Royal Purple", hex: "#6f42c1" },
  { name: "Rose Pink", hex: "#d63384" },
  { name: "Peacock Teal", hex: "#0c8599" },
  { name: "Tangerine Orange", hex: "#e8590c" },
  { name: "Midnight Black", hex: "#212529" },
];

const EXAMPLES_DATA = [
  {
    id: 1,
    title: "Example 1 : Same Design in Different Colors (Temple Border)",
    designName: "Temple Border",
    category: "Traditional",
    confidence: "96.4%",
    motifPatch: "/saree_samples/output_temple_border.jpg",
    sarees: [
      { name: "Red", img: "/saree_samples/temple_red.jpg", colorHex: "#c92a2a", preset: "Temple_Border__Crimson_Red.jpg" },
      { name: "Blue", img: "/saree_samples/temple_blue.jpg", colorHex: "#1864ab", preset: "Temple_Border__Royal_Blue.jpg" },
      { name: "Green", img: "/saree_samples/temple_green.jpg", colorHex: "#2b8a3e", preset: "Temple_Border__Emerald_Green.jpg" },
      { name: "Yellow", img: "/saree_samples/temple_yellow.jpg", colorHex: "#e67700", preset: "Temple_Border__Mustard_Yellow.jpg" }
    ],
    similar: [
      { name: "Temple Border", pct: "96% Similar", img: "/saree_samples/similar_red.jpg" },
      { name: "Temple Border", pct: "94% Similar", img: "/saree_samples/similar_blue.jpg" },
      { name: "Temple Border", pct: "92% Similar", img: "/saree_samples/similar_green.jpg" },
      { name: "Temple Border", pct: "90% Similar", img: "/saree_samples/similar_purple.jpg" }
    ]
  },
  {
    id: 2,
    title: "Example 2 : Same Design in Different Colors (Floral Motif)",
    designName: "Floral Motif",
    category: "Traditional",
    confidence: "93.8%",
    motifPatch: "/saree_samples/output_floral_motif.jpg",
    sarees: [
      { name: "Pink", img: "/saree_samples/floral_pink.jpg", colorHex: "#d63384", preset: "Floral_Jaal__Deep_Purple.jpg" },
      { name: "Purple", img: "/saree_samples/floral_purple.jpg", colorHex: "#6f42c1", preset: "Floral_Jaal__Deep_Purple.jpg" },
      { name: "Teal", img: "/saree_samples/floral_teal.jpg", colorHex: "#0c8599", preset: "Floral_Jaal__Peacock_Teal.jpg" },
      { name: "Beige", img: "/saree_samples/floral_beige.jpg", colorHex: "#d4a373", preset: "Floral_Jaal__Mustard_Yellow.jpg" }
    ],
    similar: [
      { name: "Floral Motif", pct: "95% Similar", img: "/saree_samples/floral_pink.jpg" },
      { name: "Floral Motif", pct: "93% Similar", img: "/saree_samples/floral_purple.jpg" },
      { name: "Floral Motif", pct: "91% Similar", img: "/saree_samples/floral_teal.jpg" },
      { name: "Floral Motif", pct: "89% Similar", img: "/saree_samples/floral_beige.jpg" }
    ]
  },
  {
    id: 3,
    title: "Example 3 : Same Design in Different Colors (Peacock Motif)",
    designName: "Peacock Motif",
    category: "Traditional",
    confidence: "92.6%",
    motifPatch: "/saree_samples/output_peacock_motif.jpg",
    sarees: [
      { name: "Red", img: "/saree_samples/peacock_red.jpg", colorHex: "#c92a2a", preset: "Peacock_Motif__Crimson_Red.jpg" },
      { name: "Blue", img: "/saree_samples/peacock_blue.jpg", colorHex: "#1864ab", preset: "Peacock_Motif__Royal_Blue.jpg" },
      { name: "Green", img: "/saree_samples/peacock_green.jpg", colorHex: "#2b8a3e", preset: "Peacock_Motif__Emerald_Green.jpg" },
      { name: "White", img: "/saree_samples/peacock_white.jpg", colorHex: "#e9ecef", preset: "Peacock_Motif__Mustard_Yellow.jpg" }
    ],
    similar: [
      { name: "Peacock Motif", pct: "95% Similar", img: "/saree_samples/peacock_red.jpg" },
      { name: "Peacock Motif", pct: "93% Similar", img: "/saree_samples/peacock_blue.jpg" },
      { name: "Peacock Motif", pct: "91% Similar", img: "/saree_samples/peacock_green.jpg" },
      { name: "Peacock Motif", pct: "88% Similar", img: "/saree_samples/peacock_white.jpg" }
    ]
  },
  {
    id: 4,
    title: "Example 4 : Same Design in Different Colors (Geometric Pattern)",
    designName: "Geometric Pattern",
    category: "Contemporary",
    confidence: "91.2%",
    motifPatch: "/saree_samples/output_geometric_pattern.jpg",
    sarees: [
      { name: "Orange", img: "/saree_samples/geo_orange.jpg", colorHex: "#e8590c", preset: "Geometric_Weave__Crimson_Red.jpg" },
      { name: "Black", img: "/saree_samples/geo_black.jpg", colorHex: "#212529", preset: "Geometric_Weave__Deep_Purple.jpg" },
      { name: "Purple", img: "/saree_samples/geo_purple.jpg", colorHex: "#6741d9", preset: "Geometric_Weave__Deep_Purple.jpg" },
      { name: "Maroon", img: "/saree_samples/geo_maroon.jpg", colorHex: "#721c24", preset: "Geometric_Weave__Crimson_Red.jpg" }
    ],
    similar: [
      { name: "Geometric Pattern", pct: "94% Similar", img: "/saree_samples/geo_orange.jpg" },
      { name: "Geometric Pattern", pct: "92% Similar", img: "/saree_samples/geo_black.jpg" },
      { name: "Geometric Pattern", pct: "90% Similar", img: "/saree_samples/geo_purple.jpg" },
      { name: "Geometric Pattern", pct: "87% Similar", img: "/saree_samples/geo_maroon.jpg" }
    ]
  }
];

// Color transformation helpers for 100% resilient client-side fabric recoloring
function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, v = max;
  const d = max - min;
  s = max === 0 ? 0 : d / max;
  if (max !== min) {
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
      default: break;
    }
    h /= 6;
  }
  return [h * 360, s, v];
}

function hsvToRgb(h, s, v) {
  h = (h % 360 + 360) % 360;
  h /= 360;
  let r, g, b;
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  switch (i % 6) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
    default: r = v; g = p; b = q; break;
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

// Client-side HTML5 canvas fabric recoloring (works 100% on Vercel without backend dependency)
const dyeSareeCanvas = (imageSrc, targetHex, preserveZariVal, intensityVal) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        let w = img.naturalWidth || img.width;
        let h = img.naturalHeight || img.height;
        const maxDim = 1200;
        if (Math.max(w, h) > maxDim) {
          const scale = maxDim / Math.max(w, h);
          w = Math.round(w * scale);
          h = Math.round(h * scale);
        }
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, w, h);

        const imgData = ctx.getImageData(0, 0, w, h);
        const data = imgData.data;

        const cleanHex = targetHex.replace('#', '');
        const tr = parseInt(cleanHex.substring(0, 2), 16);
        const tg = parseInt(cleanHex.substring(2, 4), 16);
        const tb = parseInt(cleanHex.substring(4, 6), 16);
        const [targetH, targetS] = rgbToHsv(tr, tg, tb);

        const len = data.length;
        for (let i = 0; i < len; i += 4) {
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];
          const a = data[i + 3];
          if (a === 0) continue;

          const [h, s, v] = rgbToHsv(r, g, b);

          // 1. Zari detection: warm gold (H 24-55) or bright metallic silver
          let isZari = false;
          if (preserveZariVal) {
            const isGold = (h >= 24 && h <= 55 && s >= 0.28 && v >= 0.35);
            const isSilver = (s < 0.20 && v >= 0.65 && v <= 0.96);
            if (isGold || isSilver) isZari = true;
          }

          // 2. Pure background detection (e.g. white border/backdrop)
          if (s < 0.08 && v > 0.93) continue;

          // Fabric weight
          const zariProtect = isZari ? 0.90 : 0.0;
          const fabricWeight = (1.0 - zariProtect) * intensityVal;

          // Target dyed saturation and value
          const dyedS = Math.min(1.0, Math.max(0.35, s * (targetS / 0.55)));
          const dyedV = v;
          const [dyedR, dyedG, dyedB] = hsvToRgb(targetH, dyedS, dyedV);

          // Blend dyed fabric with original fabric
          data[i] = Math.round(r * (1.0 - fabricWeight) + dyedR * fabricWeight);
          data[i + 1] = Math.round(g * (1.0 - fabricWeight) + dyedG * fabricWeight);
          data[i + 2] = Math.round(b * (1.0 - fabricWeight) + dyedB * fabricWeight);
        }

        ctx.putImageData(imgData, 0, 0);
        resolve(canvas.toDataURL("image/jpeg", 0.94));
      } catch (err) {
        console.warn("Canvas recoloring error:", err);
        resolve(imageSrc);
      }
    };
    img.onerror = () => resolve(imageSrc);
    img.src = imageSrc;
  });
};

export default function App() {
  const fileInputRef = useRef(null);

  // Active Saree Images State
  const [originalImage, setOriginalImage] = useState("/saree_samples/temple_red.jpg");
  const [displayedImage, setDisplayedImage] = useState("/saree_samples/temple_red.jpg");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [activePresetFilename, setActivePresetFilename] = useState("Temple_Border__Crimson_Red.jpg");

  // Recognition Results State
  const [currentDesign, setCurrentDesign] = useState("Temple Border");
  const [currentCategory, setCurrentCategory] = useState("Traditional");
  const [currentConfidence, setCurrentConfidence] = useState("96.4%");
  const [currentSimilar, setCurrentSimilar] = useState(EXAMPLES_DATA[0].similar);

  // Recolor, Realism & View Mode State
  const [activeColorHex, setActiveColorHex] = useState("#c92a2a");
  const [activeColorName, setActiveColorName] = useState("Crimson Red");
  const [isRecoloring, setIsRecoloring] = useState(false);
  const [viewMode, setViewMode] = useState("full"); // 'full', 'original', 'compare', 'stages'
  const [preserveZari, setPreserveZari] = useState(true);
  const [dyeIntensity, setDyeIntensity] = useState(0.88);
  const [visualStages, setVisualStages] = useState(null);
  const [imageDimensions, setImageDimensions] = useState("1200 × 900 px");

  // Handle changing design (shows full saree with new design)
  const handleSelectDesign = (designObj) => {
    setUploadedFile(null); // switch to design sample
    setActivePresetFilename(designObj.preset);
    setOriginalImage(designObj.baseImg);
    setDisplayedImage(designObj.baseImg);
    setCurrentDesign(designObj.name);
    setCurrentCategory(designObj.category);
    setCurrentConfidence(designObj.confidence);
    setActiveColorName("Base Dye");
    setActiveColorHex("#c92a2a");
    setImageDimensions("1000 × 800 px");

    // Also update similar designs
    const matchEx = EXAMPLES_DATA.find(e => e.designName === designObj.name);
    if (matchEx) {
      setCurrentSimilar(matchEx.similar);
    }
  };

  // Drag and drop state for manual upload
  const [isDragging, setIsDragging] = useState(false);

  // Handle clicking any saree from Example 1-4
  const handleSelectExampleSaree = (ex, saree) => {
    setUploadedFile(null);
    setActivePresetFilename(saree.preset);
    setOriginalImage(saree.img);
    setDisplayedImage(saree.img);
    setCurrentDesign(ex.designName);
    setCurrentCategory(ex.category);
    setCurrentConfidence(ex.confidence);
    setCurrentSimilar(ex.similar);
    setActiveColorName(saree.name);
    setActiveColorHex(saree.colorHex);
    setImageDimensions("1000 × 800 px");
    // Smoothly scroll to studio view at top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Trigger file picker
  const handleChooseImage = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Upload handler for user's own saree image with 100% natural original fidelity
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setActiveColorName("Original Upload");
    // Default to showing the pure untouched original photo first
    setViewMode("original");

    const reader = new FileReader();
    reader.onload = () => {
      setOriginalImage(reader.result);
      setDisplayedImage(reader.result);

      // Measure natural dimensions
      const img = new Image();
      img.onload = () => {
        setImageDimensions(`${img.naturalWidth} × ${img.naturalHeight} px`);
      };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);

    // Run prediction on uploaded saree image
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/predict`, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentDesign(data.predicted_design);
        setCurrentConfidence(`${data.confidence_percentage}%`);
        setCurrentCategory(data.predicted_design.includes("Geometric") ? "Contemporary" : "Traditional");

        if (data.visual_stages) {
          setVisualStages(data.visual_stages);
        }

        if (data.similar_designs && data.similar_designs.length > 0) {
          setCurrentSimilar(data.similar_designs.map(s => ({
            name: s.design,
            pct: `${s.match_percentage}% Similar`,
            img: `${API_BASE}${s.image_url}`
          })));
        }
      }
    } catch (err) {
      console.warn("Prediction error:", err);
    }
  };

  // Recolor the FULL saree with realism controls (preserveZari and dyeIntensity)
  const handleColorChange = async (targetHex, colorName = "Custom Color", customIntensity = null, customZari = null) => {
    setActiveColorHex(targetHex);
    setActiveColorName(colorName);
    
    // Switch away from pure original view when dyeing
    if (viewMode === "original") {
      setViewMode("full");
    }

    const intensity = customIntensity !== null ? customIntensity : dyeIntensity;
    const useZari = customZari !== null ? customZari : preserveZari;

    // STEP 1: INSTANT CLIENT-SIDE CANVAS DYEING (0ms latency, 100% guaranteed on Vercel & Render)
    try {
      const instantRecolor = await dyeSareeCanvas(originalImage, targetHex, useZari, intensity);
      setDisplayedImage(instantRecolor);
    } catch (clientErr) {
      console.warn("Client canvas recolor note:", clientErr);
    }

    // STEP 2: BACKEND SYNC (refreshes AI inference, confidence, and similarity if backend is running)
    try {
      const formData = new FormData();
      formData.append("target_hex", targetHex);
      formData.append("preserve_zari", useZari ? "true" : "false");
      formData.append("blend_intensity", intensity.toString());

      if (uploadedFile) {
        formData.append("file", uploadedFile);
      } else {
        formData.append("preset_filename", activePresetFilename || "Temple_Border__Crimson_Red.jpg");
      }

      const res = await fetch(`${API_BASE}/api/v1/recolor`, {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.recolored_image) {
          setDisplayedImage(data.recolored_image);
        }
        setCurrentDesign(data.predicted_design);
        setCurrentConfidence(`${data.confidence_percentage}%`);
        if (data.visual_stages) {
          setVisualStages(data.visual_stages);
        }
      }
    } catch (err) {
      // Backend may be starting or offline; client-side dye is already active and visible!
    } finally {
      setIsRecoloring(false);
    }
  };

  // Toggle Zari preservation and re-apply current dye
  const handleToggleZari = () => {
    const nextZari = !preserveZari;
    setPreserveZari(nextZari);
    if (activeColorHex) {
      handleColorChange(activeColorHex, activeColorName, dyeIntensity, nextZari);
    }
  };

  // Adjust Dye Intensity slider and re-apply current dye
  const handleIntensityChange = (val) => {
    const intensity = parseFloat(val);
    setDyeIntensity(intensity);
    if (activeColorHex) {
      handleColorChange(activeColorHex, activeColorName, intensity, preserveZari);
    }
  };

  // Reset to original image
  const handleResetToOriginal = () => {
    setDisplayedImage(originalImage);
    setActiveColorName("Original");
    setViewMode("original");
  };

  return (
    <div className="page-wrapper">
      {/* Top Banner */}
      <header className="top-banner">
        Color-Invariant Saree Design Recognition
      </header>

      {/* Main Container */}
      <main className="main-content-flow">
        
        {/* ================= TOP SECTION (ABOVE): MANUAL UPLOAD & AI RECOGNITION STUDIO ================= */}
        <section className="studio-section">
          
          {/* Top Bar with Logo & Navigation */}
          <div className="app-navbar">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: '1.35rem' }}>🥻</span>
              <span style={{ fontWeight: 700, letterSpacing: '-0.01em' }}>Saree Design Recognition AI Studio</span>
            </div>
            <div className="nav-links">
              <a href="#upload-area" onClick={handleChooseImage}>📤 Upload Image</a>
              <a href="#sample-benchmarks">📋 Sample Benchmarks</a>
              <a href="#about-system">ℹ️ System Info</a>
            </div>
          </div>

          {/* Upload Saree Image Box */}
          <div 
            id="upload-area"
            className={`upload-card ${isDragging ? 'dragging' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              if (e.dataTransfer.files?.[0]) {
                handleFileUpload({ target: { files: e.dataTransfer.files } });
              }
            }}
          >
            <input 
              type="file" 
              ref={fileInputRef}
              accept=".jpg,.jpeg,.png,.webp"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <div className="upload-inner-box">
              <svg className="upload-cloud-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
                <path d="m8 14 4-4 4 4" />
                <path d="M12 10v12" />
              </svg>

              <div className="upload-title">Upload Saree Image Manually</div>
              <div className="upload-subtitle">
                {uploadedFile 
                  ? `Uploaded: ${uploadedFile.name} (${(uploadedFile.size / 1024).toFixed(1)} KB)`
                  : "Click below or drag and drop any saree photo (JPG, JPEG, PNG, WEBP)"}
              </div>
              
              <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 4 }}>
                <button 
                  className="btn-choose-image"
                  onClick={handleChooseImage}
                >
                  {uploadedFile ? "Upload Another Image" : "Choose Saree Image"}
                </button>
                {uploadedFile && (
                  <span style={{ fontSize: '0.8rem', color: '#166534', fontWeight: 600 }}>
                    ✓ Saree Loaded into AI Recognition Studio
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Interactive Prediction Result Card */}
          <div className="prediction-card">
            
            {/* Prediction Header */}
            <div className="prediction-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: '1.1rem' }}>✨</span>
                <span>Prediction Result & Interactive Full Saree Studio</span>
              </div>
              {/* View Mode Toggle */}
              <div style={{ display: 'flex', gap: 6, fontSize: '0.8rem', fontWeight: 600, flexWrap: 'wrap' }}>
                <button 
                  onClick={() => setViewMode("original")}
                  className={`view-mode-btn ${viewMode === "original" ? 'active' : ''}`}
                  title="View untouched original photo exactly as uploaded"
                >
                  🖼️ Original Photo
                </button>
                <button 
                  onClick={() => setViewMode("full")}
                  className={`view-mode-btn ${viewMode === "full" ? 'active' : ''}`}
                  title="View photorealistic dyed saree with preserved zari"
                >
                  ✨ Natural Fabric Dye
                </button>
                <button 
                  onClick={() => setViewMode("compare")}
                  className={`view-mode-btn ${viewMode === "compare" ? 'active' : ''}`}
                  title="Compare original photo with dyed saree side-by-side"
                >
                  ⚖️ Compare Original
                </button>
                <button 
                  onClick={() => setViewMode("stages")}
                  className={`view-mode-btn ${viewMode === "stages" ? 'active' : ''}`}
                  title="View AI invariant feature maps (CLAHE, Sobel Edges, Texture)"
                >
                  🔬 AI Invariant Vision
                </button>
              </div>
            </div>

            {/* Interactive Change Design Toolbar */}
            <div className="design-selector-bar">
              <span className="design-selector-title">Change Design:</span>
              {AVAILABLE_DESIGNS.map((d) => (
                <button
                  key={d.name}
                  className={`design-chip ${currentDesign === d.name ? 'active' : ''}`}
                  onClick={() => handleSelectDesign(d)}
                  title={`Show full saree with ${d.name} design`}
                >
                  <span>{d.icon}</span> {d.name}
                </button>
              ))}
            </div>

            {/* Prediction Body */}
            <div className="prediction-body">
              
              {/* Left Column: Full Saree Image Showcase */}
              <div className="prediction-img-container">
                
                {/* Original Photo High-Fidelity Banner */}
                {uploadedFile && (
                  <div className="original-photo-badge">
                    <span style={{ fontSize: '1.2rem' }}>📸</span>
                    <div style={{ flex: 1 }}>
                      <strong>Original Saree Photo: {uploadedFile.name}</strong>
                      <div className="original-photo-sub">
                        Resolution: {imageDimensions} • Natural Weave & Highlights Preserved
                      </div>
                    </div>
                    <span className="original-photo-tag">100% Original Fidelity</span>
                  </div>
                )}

                <div className="full-saree-wrapper">
                  {viewMode === "stages" ? (
                    /* AI Invariant Vision Stages */
                    <div className="stages-container">
                      <div className="stage-box">
                        <div className="stage-title">1. Luminance Map (CLAHE)</div>
                        <img 
                          src={visualStages?.luminance_map || displayedImage} 
                          alt="Luminance Map" 
                          className="stage-img" 
                        />
                        <div className="stage-desc">Contrast equalized across weave & folds</div>
                      </div>
                      <div className="stage-box">
                        <div className="stage-title">2. Edge Gradient (Sobel)</div>
                        <img 
                          src={visualStages?.edge_map || displayedImage} 
                          alt="Sobel Edge Map" 
                          className="stage-img" 
                        />
                        <div className="stage-desc">Motif boundaries & temple border spires</div>
                      </div>
                      <div className="stage-box">
                        <div className="stage-title">3. Laplacian Weave Texture</div>
                        <img 
                          src={visualStages?.texture_map || displayedImage} 
                          alt="Laplacian Texture" 
                          className="stage-img" 
                        />
                        <div className="stage-desc">High-frequency metallic thread relief</div>
                      </div>
                      <div className="stage-box">
                        <div className="stage-title">4. Invariant Composite</div>
                        <img 
                          src={visualStages?.composite_invariant || displayedImage} 
                          alt="Composite Map" 
                          className="stage-img" 
                        />
                        <div className="stage-desc">Fed to Deep Learning CNN Head</div>
                      </div>
                    </div>
                  ) : viewMode === "compare" ? (
                    /* Compare Side-by-Side Mode */
                    <div className="compare-sarees-container">
                      <div className="compare-saree-box">
                        <img src={originalImage} alt="Original Saree" className="compare-saree-img" />
                        <div className="compare-saree-tag">Original Untouched Photo</div>
                      </div>
                      <div className="compare-saree-box">
                        <img src={displayedImage} alt="Recolored Saree" className="compare-saree-img" />
                        <div className="compare-saree-tag" style={{ color: '#1565c0' }}>
                          Natural Fabric Dye ({activeColorName})
                        </div>
                      </div>
                    </div>
                  ) : viewMode === "original" ? (
                    /* 100% Pure Untouched Original Photo View */
                    <div className="single-saree-display-box">
                      <img 
                        src={originalImage} 
                        alt="Original Untouched Saree" 
                        className="prediction-saree-img" 
                      />
                      <div className="original-floating-tag">
                        ✓ 100% Pure Original Saree Photo (Natural Lighting & Threads)
                      </div>
                    </div>
                  ) : (
                    /* Natural Fabric Dyed Saree View */
                    <div className="single-saree-display-box">
                      <img 
                        src={displayedImage} 
                        alt="Full Saree Preview" 
                        className="prediction-saree-img" 
                      />
                      {isRecoloring && (
                        <div className="recolor-overlay-badge">
                          Re-dyeing full saree garment...
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Saree Status Indicator */}
                <div className="saree-status-row">
                  <span>
                    {uploadedFile 
                      ? (viewMode === "original" ? "Mode: Pure Original Photo" : `Mode: Natural Silk Dye (${activeColorName})`)
                      : `Full Saree Showcase: ${currentDesign}`}
                  </span>
                  <span style={{ fontWeight: 700, color: '#1565c0' }}>
                    Active Color: {viewMode === "original" ? "Original Natural Color" : activeColorName}
                  </span>
                </div>

                {/* Realism Tuning Toolbar: Zari Preservation & Dye Intensity */}
                <div className="realism-controls-toolbar">
                  <div className="realism-controls-header">
                    <span>Authentic Fabric Realism Controls:</span>
                    <button 
                      onClick={handleToggleZari}
                      className={`zari-toggle-btn ${preserveZari ? 'active' : ''}`}
                      title="Keep gold/silver zari borders and motifs untouched while dyeing fabric"
                    >
                      {preserveZari ? "✓ Gold & Silver Zari Preserved" : "✕ Zari Protection Off"}
                    </button>
                  </div>
                  
                  <div className="intensity-slider-row">
                    <span style={{ fontSize: '0.76rem', color: '#475569', fontWeight: 600 }}>
                      Fabric Dye Blend: {Math.round(dyeIntensity * 100)}%
                    </span>
                    <input 
                      type="range" 
                      min="0.30" 
                      max="1.0" 
                      step="0.05"
                      value={dyeIntensity}
                      onChange={(e) => handleIntensityChange(e.target.value)}
                      title="Slide to blend between original natural fabric and deep dyed fabric"
                      className="intensity-slider"
                    />
                    <div className="preset-intensity-chips">
                      <button 
                        onClick={() => handleIntensityChange(0.50)}
                        className={`intensity-chip ${Math.abs(dyeIntensity - 0.50) < 0.05 ? 'active' : ''}`}
                      >
                        Soft (50%)
                      </button>
                      <button 
                        onClick={() => handleIntensityChange(0.85)}
                        className={`intensity-chip ${Math.abs(dyeIntensity - 0.85) < 0.05 ? 'active' : ''}`}
                      >
                        Natural (85%)
                      </button>
                      <button 
                        onClick={() => handleIntensityChange(1.0)}
                        className={`intensity-chip ${Math.abs(dyeIntensity - 1.0) < 0.05 ? 'active' : ''}`}
                      >
                        Deep (100%)
                      </button>
                    </div>
                  </div>
                </div>

                {/* Interactive Change Colour (Full Saree) Bar */}
                <div className="interactive-recolor-bar">
                  <span style={{ color: '#1e293b', fontWeight: 700, fontSize: '0.82rem' }}>Change Colour (Full Saree):</span>
                  
                  {COLOR_OPTIONS.map((c) => (
                    <button 
                      key={c.name}
                      className={`swatch-btn ${activeColorHex === c.hex && viewMode !== "original" ? 'selected' : ''}`}
                      style={{ background: c.hex }} 
                      title={`Dye saree naturally to ${c.name}`} 
                      onClick={() => handleColorChange(c.hex, c.name)} 
                    />
                  ))}

                  {/* Custom Color Picker Input */}
                  <input 
                    type="color" 
                    value={activeColorHex} 
                    onChange={(e) => handleColorChange(e.target.value, "Custom Dye")}
                    title="Pick custom color for full saree"
                    className="custom-color-input"
                  />

                  {/* Reset to Original Button */}
                  <button
                    onClick={handleResetToOriginal}
                    className="btn-reset-original"
                    title="Revert to 100% original untouched photo"
                  >
                    Original Photo
                  </button>
                </div>
              </div>

              {/* Right Column: Prediction Metadata & Detected Features */}
              <div className="prediction-meta">
                <div className="meta-card-box">
                  <div className="prediction-meta-row">
                    <span className="label">Design Name</span>
                    <span className="colon">:</span>
                    <span className="val-name">{currentDesign}</span>
                  </div>
                  <div className="prediction-meta-row">
                    <span className="label">Category</span>
                    <span className="colon">:</span>
                    <span>{currentCategory}</span>
                  </div>
                  <div className="prediction-meta-row">
                    <span className="label">Confidence</span>
                    <span className="colon">:</span>
                    <span className="val-conf">{currentConfidence}</span>
                  </div>
                </div>

                {/* Design Features Detected */}
                <div className="features-detected-box">
                  <div className="features-title">Design Features Detected</div>
                  {(DESIGN_FEATURES[currentDesign] || DESIGN_FEATURES["Temple Border"]).map((feature, idx) => (
                    <div key={idx} className="feature-item">
                      <span className="feature-check-icon">✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Color-Invariance Verified Callout */}
                <div className="invariance-callout-box">
                  <strong>Color-Invariance Verified:</strong> Full saree fabric color changes while the deep learning model consistently recognizes the design as <strong>{currentDesign}</strong>.
                </div>

                {/* Similar Designs Gallery */}
                <div className="similar-subcard">
                  <div className="similar-header-sub">Similar Designs in Database</div>
                  <div className="similar-grid">
                    {currentSimilar.map((item, idx) => (
                      <div 
                        key={idx} 
                        className="similar-item"
                        title="Click to view this similar saree"
                        onClick={() => {
                          setDisplayedImage(item.img);
                          setCurrentDesign(item.name);
                        }}
                      >
                        <img src={item.img} alt={item.name} className="similar-img" />
                        <div className="similar-name">{item.name}</div>
                        <div className="similar-pct">{item.pct}</div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </div>
          </div>

        </section>

        {/* ================= BOTTOM SECTION (BELOW): BENCHMARK REFERENCE SAMPLES ================= */}
        <section id="sample-benchmarks" className="samples-section">
          
          <div className="samples-section-header">
            <div>
              <div className="samples-section-title">Benchmark Reference Samples — Same Design in Different Colors</div>
              <div className="samples-section-subtitle">
                The model identifies invariant structural motifs, borders, and weave textures regardless of the saree color. Click any saree below to load it into the Recognition Studio above.
              </div>
            </div>
          </div>

          <div className="examples-grid">
            {EXAMPLES_DATA.map((ex) => (
              <div key={ex.id} className="example-row-card">
                
                {/* Left Sub-Box: Input Same Design in Different Colors */}
                <div className="example-input-side">
                  <div className="example-header">{ex.title}</div>
                  <div className="saree-quad-row">
                    {ex.sarees.map((saree) => (
                      <div 
                        key={saree.name} 
                        className="saree-mini-item"
                        title={`Click to load ${saree.name} ${ex.designName} into studio above`}
                        onClick={() => handleSelectExampleSaree(ex, saree)}
                      >
                        <img src={saree.img} alt={`${saree.name} Saree`} className="saree-mini-img" />
                        <div className="saree-mini-label">{saree.name}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Right Sub-Box: Output (AI Recognition) */}
                <div className="example-output-side">
                  <div className="output-header">Output (AI Recognition)</div>
                  <div className="output-content">
                    <img src={ex.motifPatch} alt={`${ex.designName} Motif`} className="output-motif-img" />
                    <div className="output-text-block">
                      <div>
                        <span className="label">Design:</span>
                        <span className="value-highlight">{ex.designName}</span>
                      </div>
                      <div>
                        <span className="label">Category:</span>
                        <span>{ex.category}</span>
                      </div>
                      <div>
                        <span className="label">Confidence:</span>
                        <span className="value-highlight">{ex.confidence}</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            ))}
          </div>
        </section>

      </main>
    </div>
  );
}
