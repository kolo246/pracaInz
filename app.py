from flask import Flask, flash, request, redirect, url_for, render_template, session, send_from_directory
from werkzeug.utils import secure_filename
from PIL import ImageFilter
from PIL import Image
from google.cloud import storage
import random
import string
import os
import datetime
import tempfile

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
#Max payload is 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/")
def upload_form():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/blur', methods=['GET'])
def upload_file():
    return render_template('index.html')


@app.route('/blur', methods=['POST'])
def post_blur():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        # Upload file to GCS bucket_upload_image
        upload_url, upload_blob = gcsUploadFile()
        # Blur image and assign bluredUrl with signed url
        bluredUrl = blur_image(upload_blob)
        return render_template('blur.html', fileurl=upload_url, bluredurl=bluredUrl)


def gcsUploadFile():
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    #Create a GCS client
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')

    #Get the bucket where the file will be uploaded to
    bucket = client.get_bucket('bucket_upload_image')

    #Create a new blob and upload the file
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    #Create signed URL
    url_upload_image = blob.generate_signed_url(
        version = "v4",
        #URL is valid for 15 minutes
        expiration = datetime.timedelta(minutes=30),
        #Allow GET requests using this URL
        method = "GET")
        
    return url_upload_image, blob

def blur_image(current_blob):
    file_name = current_blob.name
    extension = os.path.splitext(file_name)[1]
    #Create temporary file with extension 
    fd, temp_local_filename = tempfile.mkstemp(suffix=extension)

    #Download file from bucket
    current_blob.download_to_filename(temp_local_filename)
    
    #File is resized and blured
    image = Image.open(temp_local_filename)
    image_resized = image.resize(((480, 240)))
    blured_image = image_resized.filter(ImageFilter.GaussianBlur(15))
    image.close()
    blured_image.save(temp_local_filename)
    blured_image.close()

    #Upload blured file to a second bucket called 'bucket_blured_image'
    client = storage.Client.from_service_account_json(
        'ced0f9b8731e.json')
    blur_bucket = client.get_bucket('bucket_blured_image')
    blur_blob = blur_bucket.blob(file_name)
    blur_blob.upload_from_filename(temp_local_filename)

    #Delete the temporary file
    os.close(fd)
    os.remove(temp_local_filename)

    #Create signed URL 
    url_blured_image = blur_blob.generate_signed_url(
        version = "v4",
        expiration = datetime.timedelta(minutes=30),
        method = "GET")

    return url_blured_image

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
