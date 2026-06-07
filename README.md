<h1 align="center"> Text-to-Sign Translation API</h1>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenNMT](https://img.shields.io/badge/OpenNMT-NLP-E34F26?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**A cloud-ready REST API for translating spoken language text into Sign Language glosses and 3D keypoints.**

</div>

---

##  Overview

The **Text-to-Sign API** acts as the backend service that powers the translation layer of the **Sign AI** platform. It receives natural language text from the client, translates it into Sign Language Gloss structure using OpenNMT, and returns the corresponding pre-calculated 3D animation keypoints for the client to render the avatar.

###  Key Features

-  **FastAPI Powered:** High-performance REST endpoints for instant translation.
-  **Gloss Translation:** Uses trained OpenNMT models to convert complex sentences into simplified Sign Language grammatical structures (Glosses).
-  **Keypoint Mapping:** Maps the generated glosses to a dictionary of 3D animation keypoints (`gloss_keypoints.json` & `fingerspelling_keypoints.json`).
-  **Dockerized:** Fully containerized with a lightweight Dockerfile for easy deployment on Azure VMSS or AWS.

---

##  Getting Started

### Option 1: Run with Docker (Recommended)

```bash
git clone https://github.com/amr-ahmed-exe/text-to-sign_API.git
cd text-to-sign_API

# Build and run the container
docker build -t text-to-sign-api .
docker run -p 8000:8000 text-to-sign-api
```

### Option 2: Run Locally

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

##  Endpoints

### `POST /translate`
Accepts a JSON payload containing English/Arabic text and returns the corresponding Sign Language gloss and animation keypoints.

**Request:**
```json
{
  "text": "Hello, how are you?"
}
```

**Response:**
```json
{
  "gloss": ["HELLO", "HOW", "YOU"],
  "animation_data": [...]
}
```

---

##  License

Copyright © 2026 **Amr Ahmed**. All Rights Reserved.

---

<div align="center">

Made with ❤️ as a graduation project · Suez Canal University 2026

If you find this useful, please consider giving it a star!

</div>
