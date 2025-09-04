from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

file_bp = Blueprint("file_bp", __name__)

UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the upload folder exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"message": "File uploaded successfully", "file_path": os.path.join(UPLOAD_FOLDER, filename)}), 200
    return jsonify({"error": "File type not allowed"}), 400


