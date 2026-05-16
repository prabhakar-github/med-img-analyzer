# DICOM-AI: Multi-Modal Diagnostic Classification System

A comprehensive AI-driven tool designed to process DICOM (Digital Imaging and Communications in Medicine) images, extract clinical metadata, and perform diagnostic classification by fusing visual patterns with demographic data (Age, Gender, Region).

## 🚀 Project Overview

This system leverages a multi-modal fusion approach to recognize complex medical patterns. By combining pixel-level image analysis with structured patient information, the tool provides high-accuracy diagnostic insights while maintaining strict compliance with healthcare data regulations.

## 📅 Project Roadmap

### Phase 1: Requirements & Compliance 
* **Objectives & Scope:** Define target modalities (X-ray, MRI, CT) and therapeutic areas (Oncology, Neurology).
* **Regulatory Framework:** Establish **HIPAA** and **GDPR** compliance protocols.
* **De-identification:** Design Protected Health Information (PHI) anonymization pipelines.
* **Stakeholder Alignment:** Coordinate between Radiologists, Data Scientists, and Legal teams.

### Phase 2: System Architecture 
* **Data Ingestion:** Secure gateway for PACS or cloud storage integration.
* **De-identification Pipeline:** Automatic stripping of PHI from metadata tags.
* **Hybrid Storage:** PostgreSQL for structured metadata; AWS S3/MinIO for heavy image files.
* **Inference Engine:** Scalable microservices using FastAPI and Triton Inference Server.

### Phase 3: Data Engineering 
* **DICOM Parsing:** Metadata extraction (Age, Sex, Body Part, Study Description) via `pydicom`.
* **Normalization:** Standardizing regional data and hospital-specific codes.
* **Quality Control:** Automated checks for corrupted files or low-resolution imagery.

### Phase 4: AI Model Development 
* **Image Classification:** Deep Learning (ResNet, EfficientNet, ViT) pre-trained on medical datasets.
* **Tabular Track:** MLP/XGBoost for Age, Gender, and Regional patterns.
* **Multi-Modal Fusion:** Implementation of a Late Fusion Layer to combine visual and demographic embeddings.

### Phase 5: Integration & Dashboard 
* **Clinical UI:** Built with React or Streamlit for visualization.
* **Analytics:** Heatmaps showing diagnostic trends across demographic slices.
* **Explainable AI (XAI):** Integration of **Grad-CAM** to provide visual justification for AI decisions.

### Phase 6: Validation & Evaluation 
* **Bias Testing:** Evaluation of ROC-AUC across different ethnicities, genders, and age groups.
* **Clinical Ground Truth:** Comparison against human radiologist panels.
* **Security Audit:** Penetration testing and data leak audits.

### Phase 7: Deployment & Monitoring 
* **Orchestration:** Containerization with Docker and Kubernetes.
* **Hybrid Cloud:** Deployment on AWS HealthImaging or on-premises hospital servers.
* **Drift Monitoring:** Continuous tracking of data and model performance.

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **DICOM Processing** | `pydicom`, `Orthanc`, `MONAI` |
| **Data Pipelines** | Apache Airflow, Prefect |
| **AI/ML Frameworks** | PyTorch, TensorFlow |
| **Database** | PostgreSQL, AWS S3 / MinIO |
| **Backend & APIs** | FastAPI, Python |

## ⚠️ Key Risk Factors
1.  **Imbalanced Data:** High risk of "demographic shortcutting." Mitigated by oversampling and class-weighting.
2.  **Tag Inconsistency:** Scanner-specific metadata variations. Mitigated by robust normalization layers.

---
*Developed for clinical research and diagnostic assistance.*
