# MedScribe 🩺🤖

**MedScribe** is a smart AI-powered system designed to read handwritten prescriptions and identify Bangladeshi medicines based on their descriptions. It leverages computer vision and natural language processing (NLP) to assist pharmacists, patients, and healthcare providers with better understanding and digitizing medical prescriptions.

---

## 🔍 Overview

In Bangladesh, prescriptions are often handwritten and difficult to read, and medicine names/descriptions vary between local brands. MedScribe aims to:

- Digitally recognize handwritten prescriptions using OCR.
- Extract and identify medicine names, doses, and instructions.
- Match medicine descriptions with Bangladeshi medicine databases.
- Provide structured, readable output for better healthcare delivery.

---

## ✨ Features

- 📝 **Handwritten Text Recognition (HTR)**: Detects and transcribes handwritten prescriptions.
- 💊 **Medicine Matching**: Maps detected medicine names to Bangladeshi pharmaceutical data.
- 🔎 **Smart Search**: Search by medicine name, use case, or partial input.
- 🌐 **Bangla Language Support**: Supports English and Bangla texts.
- 📱 **API Ready**: Easy integration into mobile or web-based healthcare apps.

---

## 🧠 Tech Stack

- **Python** (Core programming language)
- **Gemini-2.5-flash**/  (Image processing & OCR)
- **Transformers / LLMs** (NLP for context understanding)
- **Pandas** / **SQLite / PostgreSQL** (Medicine data handling)
- **FastAPI**  (Optional API layer)
---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/medscribe.git
cd medscribe
