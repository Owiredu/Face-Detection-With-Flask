from flask import Flask, render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
from flask.helpers import flash
import os
import cv2
import time
#from mtcnn.mtcnn import MTCNN


# create all the constants
UPLOAD_DIR = 'static/assets/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMG_FILE_EXT = '.jpg'
SRC_IMG_NAME_PREFIX = 'src_img'
RESULT_IMG_NAME_PREFIX = 'result_img'
DEFAULT_IMG_NAME = 'default_img' + IMG_FILE_EXT
CASCADE_CLASSIFIER_NAME = 'haarcascade_frontalface_alt.xml'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR


@app.route('/')
def index():
    """
    Opens the homepage
    """
    return render_template('index.html')


@app.route('/<img_path>')
def result(img_path):
    """
    Opens the results page
    """
    # split string into src_img_name and result_img_name
    img_path_l = img_path.split(':')
    return render_template('index.html', img_path=img_path_l)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Uploads an image file
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(url_for('index'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(url_for('index'))
        if file and allowed_file(file.filename):
            # remove existing src and result images
            remove_existing_src_or_result_img('src')
            remove_existing_src_or_result_img('result')
            # get secure filename
            filename = secure_filename(file.filename)
            # create unique src image name
            soure_img_name = SRC_IMG_NAME_PREFIX + "_" + get_timestamp() + IMG_FILE_EXT
            # save the source image
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], soure_img_name))
            # detect faces
            output = detect_faces_haar()
            # return the result page
            return redirect(url_for('result', img_path=soure_img_name + ":" + output))
    # return the index page if the form is not submitted rightly
    return redirect(url_for('index'))


def detect_faces_haar():
    """
    Detects faces in images and returns the image with the detected face dimensions 
    using haarcascades
    """
    # read src image
    src_img_name = url_for('static', filename=os.path.join(
        app.config['UPLOAD_FOLDER'], DEFAULT_IMG_NAME))
    imgs = os.listdir(app.config['UPLOAD_FOLDER'])
    for name in imgs:
        if name.startswith('src_img'):
            src_img_name = name
            break
    frame = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], src_img_name))
    classifier = cv2.CascadeClassifier(os.path.join(
        app.config['UPLOAD_FOLDER'], CASCADE_CLASSIFIER_NAME))
    # detect the faces
    faces_dimensions = classifier.detectMultiScale(convertToGRAY(frame), scaleFactor=1.2,
                                                   minNeighbors=5, minSize=(30, 30))
    # return nothing if no face is detected
    if len(faces_dimensions) == 0:
        return 'NO FACE(S) DETECTED'
    for rect in faces_dimensions:
        rectangle(frame, rect)
    # create suffix for image filename with format year_month_dayOfMonth_hour_minute_seconds
    timestamp = get_timestamp()
    img_name = RESULT_IMG_NAME_PREFIX + "_" + timestamp + IMG_FILE_EXT
    # save the file
    cv2.imwrite(os.path.join(
        app.config['UPLOAD_FOLDER'], img_name), frame)
    # return the filename
    return img_name


def detect_faces_mtcnn():
    """
    Detects faces using Multi-Task Cascaded Convolutional Neural Network
    """
    # read src image
    src_img_name = url_for('static', filename=os.path.join(
        app.config['UPLOAD_FOLDER'], DEFAULT_IMG_NAME))
    imgs = os.listdir(app.config['UPLOAD_FOLDER'])
    for name in imgs:
        if name.startswith('src_img'):
            src_img_name = name
            break
    frame = cv2.cvtColor(cv2.imread(os.path.join(
        app.config['UPLOAD_FOLDER'], src_img_name)), cv2.COLOR_BGR2RGB)
    # detect the faces
    detector = MTCNN()
    faces_results = detector.detect_faces(frame)
    # return nothing if no face is detected
    if len(faces_results) == 0:
        return 'NO FACE(S) DETECTED'
    for result in faces_results:
        rectangle(frame, result['box'])
    # create suffix for image filename with format year_month_dayOfMonth_hour_minute_seconds
    timestamp = get_timestamp()
    img_name = RESULT_IMG_NAME_PREFIX + "_" + timestamp + IMG_FILE_EXT
    # save the file
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(
        app.config['UPLOAD_FOLDER'], img_name), frame)
    # return the filename
    return img_name


def get_timestamp():
    """
    Returns a timestamp for naming the images
    """
    timestamp = time.localtime()
    timestamp = '_'.join((str(timestamp.tm_year), str(timestamp.tm_mon), str(
        timestamp.tm_mday), str(timestamp.tm_hour), str(timestamp.tm_min), str(timestamp.tm_sec)))
    return timestamp


def remove_existing_src_or_result_img(img_category):
    """
    Removes an already existing src or result image
    """
    imgs = os.listdir(app.config['UPLOAD_FOLDER'])
    for name in imgs:
        if name.startswith('src_img' if img_category == 'src' else 'result_img'):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], name))
            break


def convertToGRAY(frame):  # argument types: Mat
    """
    This method converts bgr image to grayscale
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def rectangle(img, rect):  # argument types: Mat, list
    """
    This method draws a rectangle around the detected face
    """
    (x, y, w, h) = rect
    cv2.rectangle(img, (x-10, y-10), (x+w+10, y+h+10),
                  (0, 255, 0), 2, cv2.LINE_AA)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=False)
