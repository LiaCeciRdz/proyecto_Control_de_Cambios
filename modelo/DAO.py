from botocore.exceptions import ClientError
import boto3
import time
import csv
import re

params = {
    'region': 'us-west-2',
    'database': 'default',
    'bucket': 'bucketpruebastrail',
    'path': 'athena/output',
    'catalog': 'AwsDataCatalog'
}

class athena:

    def execute_custom_query(self, query, max_execution=5):
        # Ejecuto la consulta en athena y la almaceno en el bucket de S3.
        athena = boto3.client('athena', region_name=params["region"])
        execution = ''
        try:
            execution = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': params['database'],
                    'Catalog': params['catalog']
                },
                ResultConfiguration={
                    'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
                }
            )

        except ClientError as e:
            return "Incorrect syntax: {}".format(e)

        execution_id = execution['QueryExecutionId']

        # Verifico el estatus de la consulta y obtengo el nombre del archivo csv.
        state = 'RUNNING'
        filename = ''
        while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
            max_execution = max_execution - 1
            try:
                response = athena.get_query_execution(QueryExecutionId=execution_id)
            except ClientError as e:
                return "Error: {}".format(e)

            if 'QueryExecution' in response and 'Status' in response['QueryExecution'] and 'State' in \
                    response['QueryExecution']['Status']:
                state = response['QueryExecution']['Status']['State']
                if state == 'FAILED':
                    return False
                elif state == 'SUCCEEDED':
                    s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                    filename = re.findall('.*\/(.*)', s3_path)[0]
            time.sleep(1)

        # Leer datos de la consulta desde el archivo CSV almacenado en el bucket
        s3_client = boto3.resource('s3', region_name=params["region"])
        bucket = params['bucket']
        key = '{}/{}'.format(params['path'], filename)
        try:
            s3_obj = s3_client.Object(bucket, key.replace('+', ' '))
        except ClientError as e:
            return "Error: {}".format(e)
        data = s3_obj.get()['Body'].read()
        data_csv = csv.DictReader(data.decode('utf-8').split('\n'), delimiter=',')
        rows = [l for l in data_csv]
        # Limpiar bucket
        s3 = boto3.resource('s3', region_name=params["region"])
        try:
            my_bucket = s3.Bucket(params['bucket'])
        except ClientError as e:
            return "Error: {}".format(e)
        for item in my_bucket.objects.filter(Prefix=params['path']):
            item.delete()
        return rows