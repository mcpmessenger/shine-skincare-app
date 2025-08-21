# TODO

- [ ] Draft Developer Implementation Guide v1.0
- [ ] Define mobile capture and calibration pipeline (no-hardware + optional polarized add-on)
- [ ] Implement specular highlight suppression + diffuse albedo estimation prototype (OpenCV/Python)
- [ ] Implement pseudo-spectral feature extraction (melanin/hemoglobin proxies; rPPG option for videos)
- [ ] Implement texture-based segmentation prototype (Gabor/LBP + SLIC; baseline U-Net)
- [ ] Upgrade face detector to landmarks-capable model (MediaPipe/RetinaFace) and region masks (T-zone, cheeks, forehead)
- [ ] Prepare SCIN+UTKFace training splits and metadata harmonization
- [ ] Build multi-task model (conditions + severity) with calibration (Platt/Isotonic)
- [ ] Define evaluation protocol and dashboard (AUC, F1, balanced accuracy, ECE calibration)
- [ ] Integrate inference pipeline into Flask backend and Next.js UI with explainability overlays
- [ ] Write acceptance criteria and sprint plan (0–2, 3–6, 7–12 weeks)


