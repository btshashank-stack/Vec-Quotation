"""
Vecmocon Quotation Backend API
Professional quotation generation service with Flask

Usage:
    python app.py
    Then open http://localhost:5000/ui in your browser
"""

import os
import io
import json
import traceback
from flask import Flask, request, jsonify, send_file, Response, send_from_directory

# ══════════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
def add_cors(response):
    """Enable CORS for local file access"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ══════════════════════════════════════════════════════════════════════════════
# FLASK APP SETUP
# ══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.after_request(add_cors)

from generate_quotation import build_pdf, SAMPLE_DATA

import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "Vecmocon Quotation API is running",
        "version": "2.0",
        "endpoints": {
            "/": "Health check",
            "/ui": "Quotation UI",
            "/api/generate": "Generate PDF (POST)",
            "/api/sample": "Get sample data (GET)"
        }
    })


@app.route("/ui", methods=["GET"])
def serve_ui():
    """Serve the quotation UI"""
    return send_from_directory(BASE_DIR, "quotation_ui.html")


@app.route("/favicon.ico", methods=["GET"])
def serve_favicon_ico():
    """Serve the favicon.ico"""
    favicon_path = os.path.join(BASE_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return send_file(favicon_path, mimetype="image/x-icon")
    return "", 404


@app.route("/favicon.svg", methods=["GET"])
def serve_favicon_svg():
    """Serve the favicon.svg"""
    favicon_path = os.path.join(BASE_DIR, "favicon.svg")
    if os.path.exists(favicon_path):
        return send_file(favicon_path, mimetype="image/svg+xml")
    return "", 404


@app.route("/favicon-96x96.png", methods=["GET"])
def serve_favicon_96():
    """Serve the 96x96 favicon"""
    favicon_path = os.path.join(BASE_DIR, "favicon-96x96.png")
    if os.path.exists(favicon_path):
        return send_file(favicon_path, mimetype="image/png")
    return "", 404


@app.route("/apple-touch-icon.png", methods=["GET"])
def serve_apple_icon():
    """Serve the Apple touch icon"""
    icon_path = os.path.join(BASE_DIR, "apple-touch-icon.png")
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype="image/png")
    return "", 404


@app.route("/web-app-manifest-192x192.png", methods=["GET"])
def serve_manifest_192():
    """Serve the 192x192 manifest icon"""
    icon_path = os.path.join(BASE_DIR, "web-app-manifest-192x192.png")
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype="image/png")
    return "", 404


@app.route("/web-app-manifest-512x512.png", methods=["GET"])
def serve_manifest_512():
    """Serve the 512x512 manifest icon"""
    icon_path = os.path.join(BASE_DIR, "web-app-manifest-512x512.png")
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype="image/png")
    return "", 404


@app.route("/site.webmanifest", methods=["GET"])
def serve_webmanifest():
    """Serve the web app manifest"""
    manifest_path = os.path.join(BASE_DIR, "site.webmanifest")
    if os.path.exists(manifest_path):
        return send_file(manifest_path, mimetype="application/manifest+json")
    return "", 404


@app.route("/vecmocon_logo.png", methods=["GET"])
def serve_vecmocon_logo():
    """Serve the Vecmocon logo - tries multiple file names"""
    # Try different possible filenames
    possible_files = [
        "vecmocon_logo.png",
        "vecmocon_logo.jpg",
        "vecmocon_logo.jpeg",
        "vecmocon_logo",  # No extension
        "Horizontal_Original_Black_2x__2_.png",  # Original uploaded name
    ]
    
    for filename in possible_files:
        logo_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(logo_path):
            # Determine mimetype based on file extension
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                mimetype = "image/jpeg"
            else:
                mimetype = "image/png"
            return send_file(logo_path, mimetype=mimetype)
    
    return "", 404


@app.route("/logo.png", methods=["GET"])
def serve_logo():
    """Serve the Vecmocon logo (backward compatibility)"""
    return serve_vecmocon_logo()


@app.route("/api/sample", methods=["GET"])
def sample():
    """Returns sample data structure for UI pre-fill"""
    return jsonify(SAMPLE_DATA)


@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate():
    """
    Generate quotation PDF from JSON data
    
    Request Body:
        JSON object containing quotation details
        
    Returns:
        PDF file download
    """
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response(status=200)
    
    try:
        # Parse JSON data
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON body received"}), 400
        
        # Validate required fields
        if "quotation" not in data or "products" not in data:
            return jsonify({"error": "Missing required fields: quotation, products"}), 400
        
        # Auto-calculate product totals
        for p in data.get("products", []):
            p["unitPrice"] = float(p.get("unitPrice", 0))
            p["quantity"] = int(p.get("quantity", 1))
        
        # Generate PDF
        out_path = os.path.join(BASE_DIR, "quotation_output.pdf")
        build_pdf(data, out_path)
        
        # Send file as download
        quotation_number = data['quotation']['number'].replace('/', '_')
        return send_file(
            out_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Quotation_{quotation_number}.pdf"
        )
    
    except KeyError as e:
        error_msg = f"Missing required field: {str(e)}"
        return jsonify({"error": error_msg}), 400
    
    except ValueError as e:
        error_msg = f"Invalid data format: {str(e)}"
        return jsonify({"error": error_msg}), 400
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:5000/ui")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
