import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "wastewise_ai_secret_key"  # used for flash messages

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
DATA_FILE = "data.json"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Make sure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# Waste Category Knowledge Base
# ---------------------------------------------------------------------------
# Each category contains:
#   - keywords: words searched for in the uploaded filename
#   - recycling instructions
#   - environmental impact info
#   - disposal recommendation
#   - icon (Bootstrap Icons class name)
#   - color (used for theming the result card)
WASTE_DATA = {
    "Plastic": {
        "keywords": ["plastic", "bottle", "wrapper", "packet", "container", "bag", "straw", "cup", "pet", "polythene"],
        "recycling": "Rinse the plastic item, remove caps/labels if possible, and place it in the "
                      "designated plastic recycling bin. Avoid mixing with food waste.",
        "impact": "Plastic can take 400-1000 years to decompose. Recycling 1 tonne of plastic "
                  "saves approximately 5,774 kWh of energy and reduces ocean/landfill pollution.",
        "disposal": "Dispose of in a BLUE recycling bin (or your local plastic-waste collection point). "
                     "Do not burn plastic as it releases toxic fumes.",
        "icon": "bi-cup-straw",
        "color": "#1e88e5"
    },
    "Paper": {
        "keywords": ["newspaper", "paper", "notebook", "cardboard", "carton", "box", "magazine", "envelope", "tissue"],
        "recycling": "Flatten cardboard boxes, remove any plastic tape, and keep paper dry and clean "
                      "before placing it in the paper recycling bin.",
        "impact": "Recycling 1 tonne of paper saves about 17 trees, 26,500 litres of water, "
                  "and reduces landfill methane emissions significantly.",
        "disposal": "Dispose of in a designated PAPER/CARDBOARD recycling bin. Keep paper waste "
                     "dry and free from food contamination.",
        "icon": "bi-file-earmark-text",
        "color": "#6d4c41"
    },
    "Glass": {
        "keywords": ["glass", "jar", "bottle", "mirror", "window", "tumbler", "wine"],
        "recycling": "Rinse glass containers, remove lids, and separate by color if your local "
                      "facility requires it. Broken glass should be wrapped safely before disposal.",
        "impact": "Glass is 100% recyclable and can be recycled endlessly without losing quality. "
                  "Recycling glass reduces related air pollution by up to 20%.",
        "disposal": "Dispose of in a GREEN/glass-specific recycling bin. Handle broken glass with "
                     "care and wrap it in paper before discarding.",
        "icon": "bi-cup",
        "color": "#43a047"
    },
    "Metal": {
        "keywords": ["can", "metal", "aluminium", "aluminum", "steel", "tin", "foil", "scrap", "wire", "nail"],
        "recycling": "Rinse food residue from cans, flatten them if possible, and place them in "
                      "the metal recycling bin. Aluminum foil should be clean before recycling.",
        "impact": "Recycling aluminum saves up to 95% of the energy required to produce new "
                  "aluminum from raw materials, significantly cutting greenhouse gas emissions.",
        "disposal": "Dispose of in a designated METAL/CAN recycling bin or scrap-metal collection center.",
        "icon": "bi-recycle",
        "color": "#9e9e9e"
    },
    "E-Waste": {
        "keywords": ["charger", "laptop", "mobile", "phone", "battery", "cable", "electronic", "ewaste", "computer", "circuit"],
        "recycling": "Do NOT throw electronic items in regular trash. Take them to a certified "
                      "e-waste collection center where components can be safely dismantled and recycled.",
        "impact": "E-waste contains hazardous materials like lead, mercury, and cadmium. Proper "
                  "recycling recovers valuable metals (gold, copper, silver) and prevents soil/water contamination.",
        "disposal": "Drop off at a certified E-WASTE collection point or authorized electronics retailer "
                     "offering take-back programs.",
        "icon": "bi-cpu",
        "color": "#fb8c00"
    },
    "Organic Waste": {
        "keywords": ["food", "fruit", "vegetable", "peel", "organic", "leftovers", "leftover", "compost", "leaf", "garden"],
        "recycling": "Collect organic waste separately and use it for composting at home or "
                      "through a community composting program to create nutrient-rich soil.",
        "impact": "Composting organic waste reduces methane emissions from landfills and produces "
                  "natural fertilizer, improving soil health and reducing the need for chemical fertilizers.",
        "disposal": "Dispose of in a GREEN/organic waste bin or a home compost pit. Avoid mixing "
                     "with plastic or non-biodegradable items.",
        "icon": "bi-flower1",
        "color": "#7cb342"
    },
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def allowed_file(filename):
    """Check whether the uploaded file has an allowed image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_data():
    """Load dashboard statistics from the JSON data file.

    If the file does not exist or is corrupted, a fresh data
    structure is returned and saved.
    """
    default_data = {
        "total_uploads": 0,
        "category_counts": {category: 0 for category in WASTE_DATA.keys()},
        "history": []  # list of {filename, description, category, confidence, timestamp}
    }

    if not os.path.exists(DATA_FILE):
        save_data(default_data)
        return default_data

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Ensure all expected keys exist (handles older data files gracefully)
            if "total_uploads" not in data:
                data["total_uploads"] = 0
            if "category_counts" not in data:
                data["category_counts"] = {category: 0 for category in WASTE_DATA.keys()}
            else:
                # Make sure every known category has an entry
                for category in WASTE_DATA.keys():
                    data["category_counts"].setdefault(category, 0)
            if "history" not in data:
                data["history"] = []
            return data
    except (json.JSONDecodeError, IOError):
        # If the file is corrupted, reset it
        save_data(default_data)
        return default_data


def save_data(data):
    """Save dashboard statistics to the JSON data file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def find_matching_categories(text):
    """
    Scan a piece of text (lowercased) for waste-category keywords.

    Returns:
        set: names of all categories that have at least one keyword
             appearing in the given text. Empty set if no match.
    """
    text_lower = text.lower()
    matches = set()

    for category, info in WASTE_DATA.items():
        for keyword in info["keywords"]:
            if keyword in text_lower:
                matches.add(category)
                break  # one keyword hit is enough to flag this category

    return matches


def classify_waste(filename, description=""):
    """
    Simulate AI classification using rule-based keyword matching on
    BOTH the uploaded filename and an optional user-written description.

    Logic:
        1. Find which waste categories are suggested by the filename.
        2. Find which waste categories are suggested by the description.
        3. If a category is suggested by BOTH sources -> highest confidence
           (strong agreement between the two "signals").
        4. If a category is suggested by only ONE source -> medium confidence.
        5. If neither source matches anything -> "Unknown Waste" with low
           confidence.

    Args:
        filename (str): the uploaded image's filename.
        description (str): optional user-written description of the item.

    Returns:
        tuple: (category_name (str), confidence (float))
    """
    filename_matches = find_matching_categories(filename)
    description_matches = find_matching_categories(description) if description else set()

    # Categories agreed upon by BOTH the filename and the description.
    # If more than one category matches both sources (e.g., the word
    # "bottle" appears in both Plastic and Glass keyword lists), pick
    # the first one in WASTE_DATA's defined order for consistency.
    both_match = filename_matches & description_matches
    if both_match:
        category = next(c for c in WASTE_DATA if c in both_match)
        confidence = round(random.uniform(90.0, 99.0), 2)
        return category, confidence

    # Categories suggested by only one of the two sources
    single_match = filename_matches | description_matches
    if single_match:
        category = next(c for c in WASTE_DATA if c in single_match)
        confidence = round(random.uniform(60.0, 84.0), 2)
        return category, confidence

    # No keyword matched in either source -> Unknown Waste
    confidence = round(random.uniform(30.0, 55.0), 2)
    return "Unknown Waste", confidence


def validate_image(filepath):
    """
    Validate that the uploaded file is a real, openable image using Pillow.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    try:
        with Image.open(filepath) as img:
            img.verify()  # verify that it is, in fact, an image
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the homepage with project information and upload form."""
    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve an uploaded image file from the uploads folder."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle image upload, validate it, classify it using rule-based
    logic, update the dashboard statistics, and render the results page.
    """
    # Check if a file was actually included in the request
    if "image" not in request.files:
        flash("Please select an image to upload before submitting.")
        return redirect(url_for("index"))

    file = request.files["image"]

    # Check if a filename was provided
    if file.filename == "":
        flash("No image selected. Please choose a photo of the waste item first.")
        return redirect(url_for("index"))

    # Check if the file extension is allowed
    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload an image in PNG, JPG, JPEG, GIF, BMP, or WEBP format.")
        return redirect(url_for("index"))

    # Secure the filename to prevent directory traversal attacks
    original_filename = secure_filename(file.filename)

    # Read the optional user-written description of the waste item
    description = request.form.get("description", "").strip()

    # Add a timestamp prefix to avoid filename collisions
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_filename = f"{timestamp}_{original_filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], saved_filename)

    try:
        file.save(filepath)
    except Exception as e:
        flash(f"Something went wrong while saving your file. Please try again. (Details: {e})")
        return redirect(url_for("index"))

    # Validate that the uploaded file is actually a valid image
    if not validate_image(filepath):
        # Remove the invalid file
        if os.path.exists(filepath):
            os.remove(filepath)
        flash("That file doesn't look like a valid image. Please upload a real PNG, JPG, JPEG, GIF, BMP, or WEBP file.")
        return redirect(url_for("index"))

    # ---------------------------------------------------------------
    # Run the simulated AI classification using BOTH the filename
    # and the optional user description as keyword sources.
    # ---------------------------------------------------------------
    category, confidence = classify_waste(original_filename, description)

    # ---------------------------------------------------------------
    # Update dashboard statistics in data.json
    # ---------------------------------------------------------------
    data = load_data()
    data["total_uploads"] += 1

    if category not in data["category_counts"]:
        data["category_counts"][category] = 0
    data["category_counts"][category] += 1

    data["history"].append({
        "filename": saved_filename,
        "description": description,
        "category": category,
        "confidence": confidence,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_data(data)

    # Get detailed info for the detected category (if available)
    info = WASTE_DATA.get(category)

    return render_template(
        "result.html",
        image_path=saved_filename,
        description=description,
        category=category,
        confidence=confidence,
        info=info
    )


@app.route("/dashboard")
def dashboard():
    """Render the dashboard page showing overall usage statistics."""
    data = load_data()

    total_uploads = data["total_uploads"]
    category_counts = data["category_counts"]

    # Determine the most common waste category
    if total_uploads > 0 and any(category_counts.values()):
        most_common = max(category_counts, key=category_counts.get)
        most_common_count = category_counts[most_common]
    else:
        most_common = "N/A"
        most_common_count = 0

    # Recent uploads (latest 10, most recent first)
    recent_history = list(reversed(data["history"]))[:10]

    return render_template(
        "dashboard.html",
        total_uploads=total_uploads,
        category_counts=category_counts,
        most_common=most_common,
        most_common_count=most_common_count,
        recent_history=recent_history,
        waste_data=WASTE_DATA
    )


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors gracefully."""
    return render_template("index.html"), 404


@app.errorhandler(413)
def file_too_large(e):
    """Handle file-too-large errors gracefully."""
    flash("That image is too large. Please upload a file smaller than 5 MB.")
    return redirect(url_for("index"))


@app.errorhandler(500)
def internal_server_error(e):
    """Handle unexpected server errors gracefully."""
    flash("Something went wrong on our end. Please try again with a different image.")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# App Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Limit upload size to 5 MB to prevent abuse
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.run(debug=True)
