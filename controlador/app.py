from flask import Flask,render_template
from flask_bootstrap import Bootstrap
import time
from datetime import date, timedelta, datetime
from botocore.exceptions import ClientError
import boto3
import time
import csv
import re
from DAO import athena

app = Flask(__name__, template_folder='../vista', static_folder='../static')
Bootstrap(app)

@app.route('/')
def pgPrincipal():
    Athena = athena()
    ahora = date.today()
    mesPasado = ahora + timedelta(-(365/12))
    mesPasado = mesPasado + timedelta(+1)
    fs = mesPasado.strftime('%Y-%m-%d')
    #print(fs)
    query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventname IN ('RunInstances', 'RebootInstances','StartInstances','StopInstances','TerminateInstances','CreateVolume','DeleteVolume','AttachVolume','DetachVolume','ModifyInstanceAttribute','CreateBucket','DeleteBucket','PutObject','CopyObject','DeleteObject','PutBucketLifecycle','DeleteBucketLifecycle','PutBucketPolicy','DeleteBucketPolicy');".format(fs)
    result = Athena.execute_custom_query(query)
    print(result[0]['Fecha'])
    print(type(result[0]['Fecha']))
    
    return render_template('pgComunes/index.html',fs=fs,ahora=ahora,cambios=result)

@app.route('/obtenerFecha/<string:fecha>')
def obtenerFecha(fecha):
    r = fecha.split("T")
    f=r[0]
    return f


if __name__ == '__main__':
    app.run(debug=True)