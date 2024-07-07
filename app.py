from flask import Flask, request, send_file
from PIL import Image
import io
import zipfile

app = Flask(__name__)

@app.route('/')
def upload_form():
    return '''
    <!doctype html>
    <title>Upload QR Codes</title>
    <h1>Upload QR Codes to Overlay on Template</h1>
    <form method="POST" action="/generate_cards" enctype="multipart/form-data">
        <input type="file" name="qr_codes" multiple><br><br>
        <input type="submit" value="Upload and Generate">
    </form>
    '''

@app.route('/generate_cards', methods=['POST'])
def generate_cards():
    if 'qr_codes' not in request.files:
        return "No file part"
    
    qr_files = request.files.getlist('qr_codes')
    template_path = './digichola.png'
    qr_position = (80, 707)
    qr_size = (850 - 80, 1457 - 707)  # Calculate width and height based on the specified positions
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for idx, qr_file in enumerate(qr_files):
            template_img = Image.open(template_path).convert("RGBA")
            qr_code_img = Image.open(qr_file).convert("RGBA")
            
            # Resize QR code to fit the specified area
            qr_code_img = qr_code_img.resize(qr_size, Image.LANCZOS)
            
            # Create a transparent layer the size of the template
            layer = Image.new('RGBA', template_img.size, (0, 0, 0, 0))
            layer.paste(qr_code_img, qr_position)
            
            # Composite the template and the QR code layer
            combined_img = Image.alpha_composite(template_img, layer)
            
            # Save the result to a BytesIO object
            img_buffer = io.BytesIO()
            combined_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Write the image to the ZIP file
            zip_file.writestr(f'generated_vcard_{idx + 1}.png', img_buffer.read())
    
    zip_buffer.seek(0)
    
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='generated_vcards.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
