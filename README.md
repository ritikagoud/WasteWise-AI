# ♻️ WasteWise AI

**WasteWise AI** is a simple, beginner-friendly web application that helps users
identify waste categories from an uploaded image (and an optional written
description) and learn how to recycle or dispose of that item correctly. It is
built as a college AI project in support of **UN Sustainable Development Goal 12:
Responsible Consumption and Production**.

---

## 🎯 Project Objective

The objective of WasteWise AI is to demonstrate, in a simple and explainable
way, how a rule-based "AI" system can guide everyday users toward better waste
segregation habits. Instead of relying on heavy machine learning models, the
project focuses on:

- A clear, working full-stack web application (Flask + HTML/CSS/JS + Bootstrap)
- A transparent, rule-based classification engine that is easy to explain in
  a viva or demo
- Practical, real-world recycling guidance for six common waste categories

---

## 🌍 SDG Alignment — SDG 12: Responsible Consumption and Production

Improper waste disposal contributes directly to pollution, resource depletion,
and the loss of recyclable materials to landfills. **SDG 12** calls for reducing
waste generation through prevention, reduction, recycling, and reuse.

WasteWise AI supports this goal by:

- Helping users quickly identify what category a waste item belongs to
- Teaching correct recycling and disposal practices for each category
- Highlighting the environmental impact of recycling vs. improper disposal
- Encouraging the habit of segregating waste at the source — the single most
  effective step in making recycling systems work

---

## ✨ Features

1. **Professional Landing Page** — Explains the SDG 12 problem, the app's
   solution, and includes a dedicated **SDG 12 information card** describing
   why waste segregation matters.
2. **Image Upload with Live Preview** — Users select an image and instantly
   see a preview before submitting.
3. **"Describe the Waste Item" Input** — An optional text field where users
   describe the item in their own words (e.g., "an empty plastic water
   bottle").
4. **Dual-Source Rule-Based Classification** — The app scans **both** the
   uploaded filename and the user's description for keywords to classify the
   item into:
   - Plastic
   - Paper
   - Glass
   - Metal
   - E-Waste
   - Organic Waste
   - *(Unknown Waste if neither source matches)*
5. **Smart Confidence Scoring**:
   - **High confidence (90–99%)** — both the filename and description point
     to the same category
   - **Medium confidence (60–84%)** — only one of the two sources matches
   - **Low confidence (30–55%)** — neither source matches → "Unknown Waste"
6. **Detailed Results Page** — Shows the detected category, the user's
   description (if given), an animated confidence bar, recycling
   instructions, environmental impact facts, and disposal recommendations.
7. **Dashboard** — Displays total uploads, the most common category, a
   visual category breakdown, and a table of recent uploads. All data is
   stored persistently in `data.json`.
8. **Loading Spinner** — The "Classify Waste" button shows a spinner while
   the image is being processed, giving clear feedback to the user.
9. **Modern Responsive UI** — Built with Bootstrap 5 and Bootstrap Icons in a
   clean green sustainability theme, fully responsive on mobile and desktop.
10. **Friendly Error Handling** — Validates file type and verifies that
    uploaded files are genuine images using Pillow; shows clear, helpful
    messages for invalid uploads, oversized files, and unexpected errors.

> **AI Approach:** WasteWise AI uses a lightweight rule-based classification engine that analyzes information provided by the user and categorizes waste into appropriate recycling groups. The current prototype focuses on demonstrating the workflow of an AI-assisted waste management system. Future versions can integrate machine learning and computer vision models for automatic image recognition and improved classification accuracy.

---

## 🛠️ Technology Stack

| Layer            | Technology                          |
|------------------|--------------------------------------|
| Backend          | Python 3, Flask                      |
| Image Validation | Pillow (PIL)                         |
| Frontend         | HTML5, CSS3, JavaScript              |
| UI Framework     | Bootstrap 5 + Bootstrap Icons        |
| Data Storage     | JSON file (`data.json`)              |

No paid APIs, no TensorFlow/PyTorch, and no external database required.

---

## 📁 Project Structure

```
WasteWise-AI/
│
├── app.py                 # Main Flask application (routes, logic, classification)
├── data.json              # Stores dashboard statistics & upload history
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── static/
│   └── style.css          # Custom CSS (green sustainability theme)
│
├── templates/
│   ├── index.html         # Homepage (landing page + upload form + SDG card)
│   ├── result.html         # Classification results page
│   └── dashboard.html      # Dashboard / statistics page
│
└── uploads/                # Stores user-uploaded images
```

---

## ⚙️ Installation Steps

### 1. Prerequisites
- Python 3.8 or higher installed on your system
- `pip` package manager

### 2. Get the Project
Download/extract the `WasteWise-AI` folder, or clone it if using Git.

### 3. (Recommended) Create a Virtual Environment
```bash
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser
Navigate to:
```
http://127.0.0.1:5000/
```

---

## 🧪 How to Demo the Classification

Classification uses keyword matching on **both** the image filename and the
optional description. For the most convincing demo, combine a hinted filename
with a matching description — this produces the highest confidence score.

| Category       | Filename Keywords                                   | Description Example                       |
|-----------------|------------------------------------------------------|----------------------------------------------|
| Plastic         | bottle, plastic, wrapper, packet, container           | "an empty plastic bottle"                     |
| Paper           | newspaper, paper, notebook, cardboard, carton         | "a used cardboard box"                        |
| Glass           | glass, jar, bottle                                    | "a glass jam jar"                             |
| Metal           | can, metal, aluminium, steel, tin                     | "an aluminium soda can"                       |
| E-Waste         | charger, laptop, mobile, phone, battery, cable        | "an old phone charger"                        |
| Organic Waste   | food, fruit, vegetable, peel, organic, leftovers      | "banana peel and food leftovers"              |

If neither the filename nor the description contains a recognizable keyword,
the app returns **"Unknown Waste"** with a low confidence score and general
guidance.

---

## 🚨 Error Handling Notes

- Rejects empty form submissions (no file selected) with a friendly message.
- Rejects files with disallowed extensions (only image formats allowed).
- Uses Pillow to verify the uploaded file is a genuine, openable image.
- Limits uploads to 5 MB to prevent abuse.
- Displays clear, actionable flash messages for all error cases.
- Gracefully handles a missing or corrupted `data.json` by recreating it.

---

## 🚀 Future Scope

- Integrate a real lightweight image classification model (e.g., a small CNN
  trained on a public waste dataset) once project scope allows for it.
- Add a map feature to help users locate nearby recycling centers.
- Allow users to download their dashboard statistics as a PDF or CSV report.
- Add multi-language support for recycling instructions.
- Introduce a points/rewards system to encourage consistent recycling habits.

---

## 📜 License

This project was developed as part of the Artificial Intelligence course project. The application demonstrates how AI-inspired waste classification systems can support sustainable waste management and promote the goals of SDG 12: Responsible Consumption and Production.
