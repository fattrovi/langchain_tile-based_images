from flask import Flask, request, render_template, jsonify
import os,sys
import subprocess

app = Flask(__name__)

# 上傳檔案的路徑
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('insert.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '沒有檔案被選擇！'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有檔案被選擇！'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({'message': '檔案上傳成功', 'file_path': file_path}), 200

@app.route('/generate-presentation', methods=['POST'])
def generate_presentation():
    data = request.json
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '檔案未找到'}), 400

    # 假設你的 Python 程式為 generate_presentation.py，並且接受檔案作為參數
    try:
        result = subprocess.run([sys.executable, 'generate_presentation.py', file_path], capture_output=True, text=True)
        print("check")
        if result.returncode == 0:
            return jsonify({'message': '簡報生成成功'+ result.stdout}), 200
        else:
            return jsonify({'error': '生成失敗2' + result.stderr, 'output': result.stderr}), 500
    except Exception as e:
        return jsonify({'error': '伺服器內部錯誤', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
