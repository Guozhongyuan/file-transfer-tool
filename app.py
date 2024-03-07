from flask import Flask, render_template_string, send_from_directory, abort, request, redirect, url_for
import os

app = Flask(__name__)


html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Browser</title>
    <style>
        .button-row {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .button-row input[type="submit"] {
            width: 200px;
            font-size: 18px;
            padding: 10px;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <h1>Mode</h1>
    <div class="button-row">
        <form action="{{ url_for('choose_action') }}" method="post">
            <input type="submit" name="action" value="download">
            <input type="submit" name="action" value="upload">
        </form>
    </div>
</body>
</html>
"""
@app.route('/')
def index():
    try:
        return render_template_string(html_template)
    except Exception as e:
        abort(500, str(e))

@app.route('/choose_action', methods=['POST'])
def choose_action():
    action = request.form.get('action')
    if action == 'download':
        return redirect(url_for('download'))
    elif action == 'upload':
        return redirect(url_for('upload'))
    else:
        return "Invalid action", 400


download_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Browser</title>
</head>
<body>
    <h1>Download</h1>
    <p>PATH: {{ file_path }}</p>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/download')
def download():
    try:
        user_home_directory = os.path.expanduser('~')
        downloads_path = os.path.join(user_home_directory, 'Downloads')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        files = [f for f in os.listdir(downloads_path) if os.path.isfile(os.path.join(downloads_path, f))]
        return render_template_string(download_template, file_path=downloads_path ,files=files)
    except Exception as e:
        abort(500, str(e))


@app.route('/download/<filename>')
def download_file(filename):
    try:
        user_home_directory = os.path.expanduser('~')
        downloads_path = os.path.join(user_home_directory, 'Downloads')
        return send_from_directory(downloads_path, filename, as_attachment=True)
    except Exception as e:
        abort(404, "File not found: " + filename)



upload_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Upload File</title>
    <style>
        .upload-input {
            font-size: 18px;
            padding: 10px;
            margin-top: 10px;
            cursor: pointer;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .upload-button {
            font-size: 18px;
            padding: 10px 20px;
            margin-top: 10px;
            cursor: pointer;
        }
        .success-message {
            color: green;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Upload</h1>
    <p>Your IP: {{ client_ip }}</p>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required class="upload-input">
        <button type="submit" class="upload-button">Upload</button>
    </form>
    {% if success %}
        <div class="success-message">
            File "{{ uploaded_file }}" uploaded successfully!
        </div>
    {% endif %}
</body>
</html>
"""


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        client_ip = request.remote_addr
        if 'file' not in request.files:
            return "No file part in the request"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            user_home_directory = os.path.expanduser('~')
            client_ip = request.remote_addr
            downloads_path = os.path.join(user_home_directory, 'Downloads', client_ip)
            print(downloads_path)
            if not os.path.exists(downloads_path):
                os.makedirs(downloads_path)
            filename = file.filename
            file.save(os.path.join(downloads_path, filename))
            return render_template_string(upload_template, client_ip=client_ip, uploaded_file=filename, success=True)
    return render_template_string(upload_template, client_ip=request.remote_addr)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8502, debug=True)