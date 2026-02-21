from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import zipfile
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['GET', 'POST'])
def merge_pdfs():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        pdf_writer = PdfWriter()
        
        for file in files:
            if file and allowed_file(file.filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(file_path)
                
                try:
                    pdf_reader = PdfReader(file_path)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                except Exception as e:
                    return jsonify({'error': f'Error reading {file.filename}: {str(e)}'}), 400
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        output_buffer = BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'merged_{timestamp}.pdf'
        
        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=output_filename
        )
    
    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            
            try:
                pdf_reader = PdfReader(file_path)
                total_pages = len(pdf_reader.pages)
                
                split_mode = request.form.get('split_mode', 'all')
                
                if split_mode == 'all':
                    # Split into individual pages
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for page_num in range(total_pages):
                            pdf_writer = PdfWriter()
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            page_buffer = BytesIO()
                            pdf_writer.write(page_buffer)
                            page_buffer.seek(0)
                            
                            zip_file.writestr(f'page_{page_num + 1}.pdf', page_buffer.read())
                    
                    zip_buffer.seek(0)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    return send_file(
                        zip_buffer,
                        mimetype='application/zip',
                        as_attachment=True,
                        download_name=f'split_pages_{timestamp}.zip'
                    )
                
                elif split_mode == 'range':
                    # Split by page ranges
                    ranges = request.form.get('ranges', '').strip()
                    if not ranges:
                        return jsonify({'error': 'Please specify page ranges'}), 400
                    
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        range_list = ranges.split(',')
                        for idx, range_str in enumerate(range_list):
                            range_str = range_str.strip()
                            if '-' in range_str:
                                start, end = map(int, range_str.split('-'))
                                start = max(1, min(start, total_pages))
                                end = max(start, min(end, total_pages))
                                
                                pdf_writer = PdfWriter()
                                for page_num in range(start - 1, end):
                                    pdf_writer.add_page(pdf_reader.pages[page_num])
                                
                                page_buffer = BytesIO()
                                pdf_writer.write(page_buffer)
                                page_buffer.seek(0)
                                
                                zip_file.writestr(f'range_{start}_to_{end}.pdf', page_buffer.read())
                    
                    zip_buffer.seek(0)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    return send_file(
                        zip_buffer,
                        mimetype='application/zip',
                        as_attachment=True,
                        download_name=f'split_ranges_{timestamp}.zip'
                    )
                
            except Exception as e:
                return jsonify({'error': f'Error processing PDF: {str(e)}'}), 400
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('split.html')

@app.route('/rotate', methods=['GET', 'POST'])
def rotate_pdf():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            
            try:
                pdf_reader = PdfReader(file_path)
                pdf_writer = PdfWriter()
                
                rotation = int(request.form.get('rotation', 90))
                pages = request.form.get('pages', 'all')
                
                if pages == 'all':
                    for page in pdf_reader.pages:
                        rotated_page = page.rotate(rotation)
                        pdf_writer.add_page(rotated_page)
                else:
                    # Rotate specific pages
                    page_list = [int(p) - 1 for p in pages.split(',')]
                    for idx, page in enumerate(pdf_reader.pages):
                        if idx in page_list:
                            rotated_page = page.rotate(rotation)
                            pdf_writer.add_page(rotated_page)
                        else:
                            pdf_writer.add_page(page)
                
                output_buffer = BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                return send_file(
                    output_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'rotated_{timestamp}.pdf'
                )
                
            except Exception as e:
                return jsonify({'error': f'Error processing PDF: {str(e)}'}), 400
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('rotate.html')

@app.route('/extract', methods=['GET', 'POST'])
def extract_pages():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            
            try:
                pdf_reader = PdfReader(file_path)
                total_pages = len(pdf_reader.pages)
                
                pages = request.form.get('pages', '')
                if not pages:
                    return jsonify({'error': 'Please specify pages to extract'}), 400
                
                pdf_writer = PdfWriter()
                page_list = []
                
                # Parse page numbers (e.g., "1,3,5-7")
                for part in pages.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        page_list.extend(range(start - 1, min(end, total_pages)))
                    else:
                        page_list.append(int(part) - 1)
                
                # Remove duplicates and sort
                page_list = sorted(set(page_list))
                page_list = [p for p in page_list if 0 <= p < total_pages]
                
                if not page_list:
                    return jsonify({'error': 'No valid pages selected'}), 400
                
                for page_num in page_list:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output_buffer = BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                return send_file(
                    output_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'extracted_pages_{timestamp}.pdf'
                )
                
            except Exception as e:
                return jsonify({'error': f'Error processing PDF: {str(e)}'}), 400
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('extract.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            
            try:
                pdf_reader = PdfReader(file_path)
                pdf_writer = PdfWriter()
                
                # Copy pages with compression
                for page in pdf_reader.pages:
                    page.compress_content_streams()
                    pdf_writer.add_page(page)
                
                output_buffer = BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                return send_file(
                    output_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'compressed_{timestamp}.pdf'
                )
                
            except Exception as e:
                return jsonify({'error': f'Error processing PDF: {str(e)}'}), 400
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('compress.html')

@app.route('/info', methods=['GET', 'POST'])
def pdf_info():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            
            try:
                pdf_reader = PdfReader(file_path)
                info = {
                    'filename': file.filename,
                    'total_pages': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata or {},
                    'is_encrypted': pdf_reader.is_encrypted
                }
                
                return jsonify(info)
                
            except Exception as e:
                return jsonify({'error': f'Error reading PDF: {str(e)}'}), 400
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('info.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
