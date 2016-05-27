# On this example we are going to show how to send a file
# to the browser for the user to "Download" it, instead
# of just outputing text.
# To ilustrate this, the default route will print a CSV file
# while the download route will open a "Save as..." dialog
# Browse the /download route to see it in action

from flask import Flask, make_response,send_file
from PIL import Image

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def return_files_tut():
    return app.send_static_file('/Users/abhay/PycharmProjects/BTechProject/static/Uploads/Screen_Shot_2016-05-10_at_12.09.17_PM.png')
     #return send_file('/Users/abhay/PycharmProjects/BTechProject/static/Uploads/Screen_Shot_2016-05-10_at_12.09.17_PM.png', attachment_filename='output.jpg')
     #  response = make_response(image)
      # response.headers["Content-Disposition"] = "attachment; filename=books.csv"
       #return response


app.run()