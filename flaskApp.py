from flask import Flask, render_template,request
import socket


app = Flask(__name__)



@app.route('/')
def mainfunc():

    hostName = socket.gethostname()
    return render_template('response.html', hostname=hostName, content_type='application/json')




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)