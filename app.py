"""
Vecmocon Quotation Backend API
Production-ready Flask version for cloud deployment
"""

import os
import traceback
from flask import Flask, request, jsonify, send_file, Response

from generate_quotation import build_pdf, SAMPLE_DATA

app = Flask(__name__)

# ============================================================
# CORS (Optional but safe)
# ============================================================

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ============================================================
# BASIC ROUTES
# ============================================================

@app.route("/", methods=["GET"])
def index():
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


# ============================================================
# UI ROUTE (IMPORTANT FIX FOR RENDER)
# ============================================================

@app.route("/ui", methods=["GET"])
def serve_ui():
    file_path = os.path.join(os.path.dirname(__file__), "quotation_ui.html")
    return send_file(file_path)


# ============================================================
# STATIC FILES (Images / Icons)
# ============================================================

@app.route("/<path:filename>")
def serve_static_files(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(file_path):
        return send_file(file_path)

    return "", 404


# ============================================================
# API ROUTES
# ============================================================

@app.route("/api/sample", methods=["GET"])
def sample():
    return jsonify(SAMPLE_DATA)


@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate():

    if request.method == "OPTIONS":
        return Response(status=200)

    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        if "quotation" not in data or "products" not in data:
            return jsonify({"error": "Missing required fields: quotation, products"}), 400

        for p in data.get("products", []):
            p["unitPrice"] = float(p.get("unitPrice", 0))
            p["quantity"] = int(p.get("quantity", 1))

        output_path = os.path.join(os.path.dirname(__file__), "quotation_output.pdf")
        build_pdf(data, output_path)

        quotation_number = data["quotation"]["number"].replace("/", "_")

        return send_file(
            output_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Quotation_{quotation_number}.pdf"
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
