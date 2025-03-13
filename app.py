from flask import Flask, render_template, request, send_file
import requests
import os

app = Flask(__name__)
YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    files = []
    public_key = ""
    
    if request.method == 'POST':
        public_key = request.form.get('public_key')
        if public_key:
            params = {"public_key": public_key}
            response = requests.get(YANDEX_DISK_API_URL, params=params)
            
            if response.status_code == 200:
                items = response.json().get('_embedded', {}).get('items', [])
                files = [
                    {
                        'name': item['name'],
                        'type': item['type'],
                        'path': item['public_url'] if 'public_url' in item else item['file']
                    }
                    for item in items if 'public_url' in item or 'file' in item
                ]
            else:
                return "Ошибка"
    
    return render_template('index.html', files=files, public_key=public_key)

@app.route('/download')
def download():
    file_url = request.args.get('url')
    file_name = request.args.get('name')
    
    if not file_url or not file_name:
        return "Неверные параметры", 400
    
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return send_file(file_path, as_attachment=True)
    else:
        return "Ошибка", 500

if __name__ == '__main__':
    app.run(debug=True)