from traceback import print_list
from flask import Flask,render_template,request
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
    #Gestion de los eventos de cloudtrail
    ec2Events = ["RunInstances","RebootInstances","StartInstances","StopInstances","TerminateInstances","CreateSecurityGroup","DeleteSecurityGroup","RevokeSecurityGroupEgress","RevokeSecurityGroupIngress","ModifyInstanceAttribute"]
    ebsEvents = ["AttachVolume","DetachVolume","DeleteVolume","DeleteSnapshot","DeregisterImage"]
    iamEvents = ["CreatePolicy","CreateRole","CreateGroup","CreateUser","CreateInstanceProfile","DeleteGroup","DeletePolicy","DeleteRole","DeleteUser","CreateAccessKey","DeleteAccessKey","UpdateAccessKey","DetachGroupPolicy","DetachRolePolicy","DetachUserPolicy","PutGroupPolicy","PutRolePolicy","PutUserPolicy"]
    rdsEvents = ["CreateDBCluster","CreateDBInstance","CreateDBSecurityGroup","CreateDBClusterSnapshot","DeleteDBCluster","DeleteDBInstance","DeleteDBSnapshot","DeleteDBSecurityGroup","DeleteDBClusterSnapshot","ModifyDBCluster","ModifyDBInstance","ModifyDBSubnetGroup","RestoreDBInstanceFromDBSnapshot","RebootDBInstance"]
    s3Events = ["CreateBucket","DeleteBucket","DeleteBucketPolicy","DeleteBucketLifecycle","PutBucketAcl","PutBucketPolicy","PutBucketLifecycle"]
    elbEvents = ["CreateLoadBalancer","DeleteLoadBalancer","RegisterTargets","CreateTargetGroup","DeleteTargetGroup","DeregisterTargets","ModifyTargetGroup"]
    lambdaEvents = ["DeleteFunction20150331"]
    cloudtrailEvents = ["StopLogging"]
    guarddutyEvents = ["DeleteDetector"]
    vpcEvents = ["CreateNetworkAcl","DeleteNetworkAcl","DeleteNetworkAclEntry","ReplaceNetworkAclEntry"]
    route53Events = ["ChangeResourceRecordSets","DeleteHealthCheck"]
    #ArregloFinal
    AllEvents = ec2Events + ebsEvents + iamEvents + rdsEvents + s3Events + elbEvents + lambdaEvents + cloudtrailEvents + guarddutyEvents + vpcEvents + route53Events
    #AllEvents = "'StopInstances','StartInstances','TerminateInstances'"
    res = ""
    for ev in AllEvents:
        if ev != 'DeleteHealthCheck':
            res+="'"
            res+=ev
            res+="'"
            res+=","
        else:
            res+="'"
            res+=ev
            res+="'"
    AllEvents = res
    #print(AllEvents)
    #print(type(AllEvents))
    Athena = athena()
    ahora = date.today()
    hoy = date.today()
    mesPasado = ahora + timedelta(-(365/12))
    mesPasado = mesPasado + timedelta(+1)
    fs = mesPasado.strftime('%Y-%m-%d')
    #print(fs)
    #query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventname ='LookupEvents' AND account_id = '607000612831';".format(fs)
    query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol, account_id as cuenta FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventname IN ({}) AND account_id = '314165209276';".format(fs,AllEvents)
    result = Athena.execute_custom_query(query)
    #print(result)
    #print(result[0]['Fecha'])
    #print(type(result[0]['Fecha']))
    cuenta = result[0]['cuenta']
    return render_template('pgComunes/index.html',hoy = hoy,fs=fs,ahora=ahora,cambios=result,cuenta = cuenta)

################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/filtrarEventos',methods=['post'])
def filtrarEventos():
    Athena = athena()
    hoy = date.today()
    usuario = request.form["user"]
    inicio = request.form["fechaInicio"]
    fin= request.form["fechafin"]
    evento = request.form["evento"]
    cuenta = request.form["cuenta"]
    print('******* La consola es: '+cuenta+' la fecha de inicio: '+inicio+' lafecha fin: '+fin+' el usuario: '+usuario+' *******')
    ec2Events = ["EC2","RunInstances","RebootInstances","StartInstances","StopInstances","TerminateInstances","CreateSecurityGroup","DeleteSecurityGroup","RevokeSecurityGroupEgress","RevokeSecurityGroupIngress","ModifyInstanceAttribute"]
    ebsEvents = ["EBS","AttachVolume","DetachVolume","DeleteVolume","DeleteSnapshot","DeregisterImage"]
    iamEvents = ["IAM","CreatePolicy","CreateRole","CreateGroup","CreateUser","CreateInstanceProfile","DeleteGroup","DeletePolicy","DeleteRole","DeleteUser","CreateAccessKey","DeleteAccessKey","UpdateAccessKey","DetachGroupPolicy","DetachRolePolicy","DetachUserPolicy","PutGroupPolicy","PutRolePolicy","PutUserPolicy"]
    rdsEvents = ["RDS","CreateDBCluster","CreateDBInstance","CreateDBSecurityGroup","CreateDBClusterSnapshot","DeleteDBCluster","DeleteDBInstance","DeleteDBSnapshot","DeleteDBSecurityGroup","DeleteDBClusterSnapshot","ModifyDBCluster","ModifyDBInstance","ModifyDBSubnetGroup","RestoreDBInstanceFromDBSnapshot","RebootDBInstance"]
    s3Events = ["S3","CreateBucket","DeleteBucket","DeleteBucketPolicy","DeleteBucketLifecycle","PutBucketAcl","PutBucketPolicy","PutBucketLifecycle"]
    elbEvents = ["ELB","CreateLoadBalancer","DeleteLoadBalancer","RegisterTargets","CreateTargetGroup","DeleteTargetGroup","DeregisterTargets","ModifyTargetGroup"]
    lambdaEvents = ["LAMBDA","DeleteFunction20150331"]
    cloudtrailEvents = ["CLOUDTRAIL","StopLogging"]
    guarddutyEvents = ["GUARDDUTTY","DeleteDetector"]
    vpcEvents = ["VPC","CreateNetworkAcl","DeleteNetworkAcl","DeleteNetworkAclEntry","ReplaceNetworkAclEntry"]
    route53Events = ["ROUTE53","ChangeResourceRecordSets","DeleteHealthCheck"]
    #ArregloFinal
    AllEvents = ec2Events + ebsEvents + iamEvents + rdsEvents + s3Events + elbEvents + lambdaEvents + cloudtrailEvents + guarddutyEvents + vpcEvents + route53Events
    res = ""
    for ev in AllEvents:
        if ev != 'DeleteHealthCheck':
            res+="'"
            res+=ev
            res+="'"
            res+=","
        else:
            res+="'"
            res+=ev
            res+="'"
    eventos = res                

    if usuario == "":
        if evento=="":
            query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventtime <= '{}' AND eventname IN ({}) AND account_id = '{}';".format(inicio,fin,eventos,cuenta)
        else:
            query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventtime <= '{}' AND eventname = '{}' AND account_id = '{}';".format(inicio,fin,evento,cuenta)

    else:
        if evento=="":
            query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventtime <= '{}' AND eventname IN ({}) AND account_id = '{}' AND userIdentity.userName = '{}';".format(inicio,fin,eventos,cuenta,usuario)
        else:
            query = "SELECT SUBSTRING(eventtime,1,10) as Fecha, eventname as Evento, awsregion as Region, userIdentity.userName as Usuario, useridentity.sessioncontext.sessionissuer.username Rol FROM cloudtrail_logs WHERE eventtime >= '{}' AND eventtime <= '{}' AND eventname = '{}' AND account_id = '{}' AND userIdentity.userName = '{}';".format(inicio,fin,evento,cuenta,usuario)

    result = Athena.execute_custom_query(query)
    print('eventossss:')
    print(AllEvents)
    print(evento)
    return render_template('pgComunes/filtraciones.html',hoy = hoy,fs=inicio,ahora=fin,cambios=result, cuenta = request.form["cuenta"],eventos = AllEvents, even =evento)


@app.route('/obtenerFecha/<string:fecha>')
def obtenerFecha(fecha):
    r = fecha.split("T")
    f=r[0]
    return f


if __name__ == '__main__':
    app.run(debug=True)