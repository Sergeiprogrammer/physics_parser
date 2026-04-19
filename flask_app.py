from pathlib import Path
import zipfile
import io
import uuid
import sys
import os

from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

from analyze import process_path


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(
    __name__,
    template_folder=resource_path("templates")
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

MB = 1024 * 1024
MAX_FILE_SIZE = 1024 * MB
MAX_ZIP_UNCOMPRESSED = 1024 * MB
MAX_ZIP_FILES = 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE + 10 * 1024

def info(path_to_file, filename=None):
    return process_path(path_to_file, filename)


def check_zip_without_extracting(zip_source):
    with zipfile.ZipFile(zip_source) as zf:
        members = zf.infolist()

        file_count = 0
        total_uncompressed = 0

        for item in members:
            if item.is_dir():
                continue

            file_count += 1
            total_uncompressed += item.file_size

            if file_count > MAX_ZIP_FILES:
                raise ValueError("Too many files inside zip")

            if total_uncompressed > MAX_ZIP_UNCOMPRESSED:
                raise ValueError("Zip is too large after extraction")

        return file_count, total_uncompressed


def analyze_uploaded_file(uploaded_file):
    if uploaded_file is None or uploaded_file.filename == "":
        return {
            "ok": False,
            "status": 400,
            "message": "No file selected.",
            "zip_message": None,
            "results": None,
        }

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        return {
            "ok": False,
            "status": 400,
            "message": "Invalid filename.",
            "zip_message": None,
            "results": None,
        }

    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(0)

    if size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // MB
        return {
            "ok": False,
            "status": 413,
            "message": f"File is too large (max {max_mb} MB).",
            "zip_message": None,
            "results": None,
        }

    file_bytes = uploaded_file.read()

    zip_message = ""
    if filename.lower().endswith(".zip"):
        try:
            file_count, total_uncompressed = check_zip_without_extracting(io.BytesIO(file_bytes))
            zip_message = (
                f"ZIP checked successfully.\n"
                f"Files inside: {file_count}\n"
                f"Total uncompressed size: {total_uncompressed} bytes"
            )
        except zipfile.BadZipFile:
            return {
                "ok": False,
                "status": 400,
                "message": "Invalid ZIP file.",
                "zip_message": None,
                "results": None,
            }
        except ValueError as e:
            return {
                "ok": False,
                "status": 400,
                "message": f"ZIP rejected: {e}",
                "zip_message": None,
                "results": None,
            }

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = UPLOAD_FOLDER / unique_name

    try:
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        try:
            results = info(str(save_path), filename)
        except Exception as e:
            results = [{"file": filename, "error": str(e)}]

        return {
            "ok": True,
            "status": 200,
            "message": None,
            "zip_message": zip_message,
            "results": results,
        }

    except Exception as e:
        return {
            "ok": False,
            "status": 500,
            "message": f"file cannot be analyzed: {e}",
            "zip_message": zip_message,
            "results": None,
        }

    finally:
        try:
            if save_path.exists():
                save_path.unlink()
        except Exception:
            pass


@app.errorhandler(413)
def too_large(_error):
    max_mb = MAX_FILE_SIZE // MB
    return render_template(
        "index.html",
        message=f"File is too large (max {max_mb} MB).",
        zip_message=None,
        results=None
    ), 413


@app.route("/", methods=["GET", "POST"])
def load_file():
    if request.method == "GET":
        return render_template(
            "index.html",
            message=None,
            zip_message=None,
            results=None
        )

    data = analyze_uploaded_file(request.files.get("file"))
    return render_template(
        "index.html",
        message=data["message"],
        zip_message=data["zip_message"],
        results=data["results"]
    ), data["status"]

@app.route("/api/analyze", methods=["GET", "POST"])
def load_file_api():
    data = analyze_uploaded_file(request.files.get("file"))
    return jsonify(data), data["status"]

@app.route("/help", methods=["GET"])
def help():
    return render_template("help.html")

if __name__ == "__main__":
    app.run(debug=True)