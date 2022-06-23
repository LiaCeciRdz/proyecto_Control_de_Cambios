from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from botocore.exceptions import ClientError
import boto3
import time
import csv
import re
from datetime import date, timedelta, datetime


app = Flask(__name__, template_folder='../vista', static_folder='../static')
Bootstrap(app)

@app.route('/')
def pgPrincipal():
    ahora = date.today()
    print('HOY: ', ahora)
    mesPasado = ahora + timedelta(-(365/12))
    print('Mes pasado: ',mesPasado)
    return render_template('pgComunes/index.html')



if __name__ == '__main__':
    app.run(debug=True)