import os
from PIL import Image
import numpy as np

from flask import Flask, request, render_template,make_response,send_file
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['png','jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/Users/abhay/PycharmProjects/BTechProject/static/Uploads/Input'
app.config['OUTPUT_FOLDER'] = '/Users/abhay/PycharmProjects/BTechProject/static/Uploads/Output'

number = ["z","o","t","th","f","fo","s","se","e","n"]

def encripted(data):
    myhiddenData = list()
    hiddenData = encodeData(data)
    for d in hiddenData:
        myhiddenData.append(str(d))

    str1 = ''.join(myhiddenData)
    return str1


def encodeData(data):
    myList = list()
    for ch in data:
        if ('0' <= ch) & (ch <= '9'):
            myList.append(number[ord(ch) - 48])
        else:
            myList.append(ord(ch) - 15)
    return myList

def getMessage(image):

    return ''.join(decode_imdata(image.getdata()))


def decodeData(data):
    decoded = list()
    for ch in data:
        if (type(ch) == int):
            decoded.append(chr(ch + 15))
        else:
            decoded.append(number.index(ch))
    return decoded


def getDecodedMessage(data):
    secretMessage = list()
    message = decodeData(data)
    for m in message:
        secretMessage.append(str(m))

    str2 = ''.join(secretMessage)
    return str2

def decode_imdata(imdata):

    imdata = iter(imdata)
    while True:
        pixels = list(imdata.__next__()[:3] + imdata.__next__()[:3] + imdata.__next__()[:3])
        byte = 0
        for c in range(7):
            byte |= pixels[c] & 1
            byte <<= 1
        byte |= pixels[7] & 1
        yield chr(byte)
        if pixels[-1] & 1:
            break

app.route("/error_page")
def error_page():
    return render_template("error.html")

def encode_imdata(imdata, data):
    '''given a sequence of pixels, returns an iterator of pixels with
    encoded data'''

    datalen = len(data)
    if datalen == 0:
        raise ValueError('data is empty')
    if datalen * 3 > len(imdata):
        error_page()
        # return render_template("error.html")
        # raise ValueError('data is too large for image')

    imdata = iter(imdata)
    for i in range(datalen):
        pixels = [value & ~1 for value in
                  imdata.__next__()[:3] + imdata.__next__()[:3] + imdata.__next__()[:3]]

        pix = pixels;
        pix = iter(pix)
        block = np.array([[pix.__next__(), pix.__next__(), pix.__next__()],
                          [pix.__next__(), pix.__next__(), pix.__next__()],
                          [pix.__next__(), pix.__next__(), pix.__next__()]])

        tranformMat = np.array([[7, 1, 5], [1, 6, 6], [5, 6, 7]])
        inverse = np.linalg.inv(tranformMat)

        block = np.dot(tranformMat,block)

        byte = ord(data[i])
        for j in range(7, -1, -1):
            pixels[j] |= byte & 1
            byte >>= 1
        if i == datalen - 1:
            pixels[-1] |= 1
        pixels = tuple(pixels)
        block = np.dot(inverse,block)
        yield pixels[0:3]
        yield pixels[3:6]
        yield pixels[6:9]



def encode_inplace(image, data):
    '''hides data in an image'''

    w = image.size[0]
    (x, y) = (0, 0)
    for pixel in encode_imdata(image.getdata(), data):
        image.putpixel((x, y), (pixel))

        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


def encode(image, data):
    '''generates an image with hidden data, starting with an existing
    image and arbitrary data'''

    image = image.copy()
    encode_inplace(image, data)
    return image


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    global filepath
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            data = list(request.form['text'])
            return encodem(data,filepath,filename)
        else:
            render_template("index.html")

#@app.route("/encodem", methods=['POST'])
def encodem(data,filepath,filename):
  #  data = list(request.form['text'])
    img = Image.open(filepath)
   # data = encripted(data)
    data = list(data)
    image = encode(img,data)
    pre, ext = os.path.splitext(filename)
    pre =pre +".png"

    image.save(os.path.join('/Users/abhay/PycharmProjects/BTechProject/static/Uploads/EncodedImage/', pre))
    return  send_file(os.path.join('/Users/abhay/PycharmProjects/BTechProject/static/Uploads/EncodedImage/', pre))





@app.route("/decodeMessage", methods=['GET', 'POST'])
def decodeMessage():
    global filepath
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['OUTPUT_FOLDER'], filename))
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    #image = Image.open("/Users/abhay/PycharmProjects/BTechProject/static/Uploads/Output.png")
            image = Image.open(filepath)
            data = getMessage(image)
            #data2 = getDecodedMessage(data)
            response = make_response(data)
            response.headers["Content-Disposition"] = "attachment; filename=output.csv"
            return response



if __name__ == '__main__':
    app.run()