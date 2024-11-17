from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from multiprocessing import Pool
from werkzeug.utils import secure_filename
from services.ocr_utils import ocr_recognition, extract_delivery_info, parse_extracted_info
from services.output_handler import save_results_to_csv


app = Flask(__name__)
app.secret_key = '123456'  # 用于闪现消息的密钥



UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "ocr_results.csv")
SUPPORTED_FORMATS = (".jpg", ".png", ".jpeg")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)




# 清空 OUTPUT_FOLDER 文件夹内容
def clear_output_csv():
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)




# 设置允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image_multiprocessing(args):
    image_folder, image_file = args
    image_path = os.path.join(image_folder, image_file)
    print(f"正在处理: {image_file}")

    # OCR 识别
    ocr_text = ocr_recognition(image_path)
    if ocr_text:
        # 提取信息
        extracted_info = extract_delivery_info(ocr_text)
        if extracted_info:
            print(f"提取到的原始信息: {extracted_info}")
            # 解析提取的信息
            parsed_data = parse_extracted_info(extracted_info)

            return {"image_name": image_file, **parsed_data}
        else:
            print(f"大模型提取失败: {image_file}")
    else:
        print(f"OCR识别失败: {image_file}")
    return None


@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    if request.method == 'POST':
        if 'images' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('images')
        
        # 保存文件并处理
        image_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                image_files.append(filename)
            else:
                flash('无效的文件类型', 'error')

        if image_files:

            # 使用多进程处理图片
            with Pool(processes=4) as pool:
                results = pool.map(process_image_multiprocessing, [(UPLOAD_FOLDER, image_file) for image_file in image_files])

            # 过滤掉处理失败的图片
            results = [result for result in results if result is not None]
            # 保存结果到 CSV
            save_results_to_csv(results, OUTPUT_CSV)

    download_link = url_for('download_file', filename="ocr_results.csv") if os.path.exists(OUTPUT_CSV) else None
    return render_template('index.html', results=results, download_link=download_link)

@app.route('/download/<filename>')
def download_file(filename):
    # 调试打印实际路径
    print(f"尝试下载文件: {os.path.join(OUTPUT_FOLDER, filename)}")
    
    # 确保文件存在后下载
    if os.path.exists(os.path.join(OUTPUT_FOLDER, filename)):
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    else:
        flash("文件未找到！", "error")
        return redirect(url_for('home'))







if __name__ == '__main__':
    clear_output_csv()
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    
