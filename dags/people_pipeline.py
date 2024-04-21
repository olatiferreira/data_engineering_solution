# Importa libs
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.models import Variable
from io import BytesIO, StringIO
from botocore.exceptions import ClientError
import pandas as pd
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
import json

# Importa variáveis do Airflow
filename_silver = Variable.get('filename_silver')
filename_gold = Variable.get('filename_gold')
s3_bucket = Variable.get('s3_bucket')

def send_notification_slack(message):

    data = {"text": message}

    # Serializar o dicionário para uma string JSON
    json_data = json.dumps(data)

    slack_notification = SimpleHttpOperator(
        task_id='slack_notification',
        http_conn_id='slack_webhook_connection',
        method='POST',
        endpoint='',  # Deixe vazio, pois o URL completo está na conexão        
        data=json_data,
        dag=dag,
    )
    slack_notification.execute(context={})

# Função para ler os dados da camada bronze
def read_bronze_data(**kwargs):
    s3_client = boto3.client('s3')    
    bronze_prefix = 'data/bronze/'

    # Contador de arquivos
    num_files = 0

    try:
        # Listar os objetos na camada bronze
        response = s3_client.list_objects_v2(
            Bucket=s3_bucket,
            Prefix=bronze_prefix
        )

        # Inicializar um DataFrame vazio
        df = pd.DataFrame()

        # Iterar sobre cada objeto CSV
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('.csv'):
                num_files += 1

                # Ler o arquivo CSV do S3
                obj = s3_client.get_object(Bucket=s3_bucket, Key=key)
                body = obj['Body'].read().decode('utf-8')
                csv_data = StringIO(body)
                temp_df = pd.read_csv(csv_data)
                
                # Incrementar os dados no DataFrame principal
                df = pd.concat([df, temp_df], ignore_index=True)    

        # Mensagem a ser enviada no slack
        message = ''
        if num_files > 0:
            message = f'*[Camada Bronze]*\n\nEtapa concluída com sucesso!\n\nSerão processados {num_files} arquivos'
        else:
            message = f'Nenhum arquivo para processar!'

    except ClientError as e:

        # Mensagem a ser enviada no slack
        message = f'*[Camada Bronze]*\n\nOcorreu o erro abaixo:\n\n{str(e)}'

    send_notification_slack(message)

    return df

# Função para gravar os dados na camada silver em formato Parquet
def write_silver_data(**kwargs):
    s3_client = boto3.client('s3')    
    silver_prefix = 'data/silver/'

    ti = kwargs['ti']
    bronze_data = ti.xcom_pull(task_ids='read_bronze_data')

    try:
        # Converter o DataFrame para o formato Parquet
        parquet_buffer = BytesIO()
        pq.write_table(pa.Table.from_pandas(bronze_data), parquet_buffer)
        parquet_buffer.seek(0)

        # Gravar o arquivo Parquet no S3
        s3_client.put_object(Body=parquet_buffer.getvalue(), Bucket=s3_bucket, Key=silver_prefix + f'{filename_silver}.parquet')

        # Mensagem a ser enviada no slack
        message = f'*[Camada Silver]*\n\nEtapa concluída com sucesso!\n\nDados atualizados no arquivo "{filename_silver}.parquet"'

    except ClientError as e:

        # Mensagem a ser enviada no slack
        message = f'*[Camada Silver]*\n\nOcorreu o erro abaixo:\n\n{str(e)}'        

    send_notification_slack(message)

# Função para gravar os dados na camada gold sem duplicidades
def write_gold_data(**kwargs):
    s3_client = boto3.client('s3')
    silver_prefix = 'data/silver/'
    gold_prefix = 'data/gold/'

    try:
        # Ler o arquivo Parquet da camada silver do S3
        silver_obj = s3_client.get_object(Bucket=s3_bucket, Key=silver_prefix + filename_silver + '.parquet')
        silver_body = silver_obj['Body'].read()
        
        # Ler o arquivo Parquet em um DataFrame
        silver_df = pq.read_table(BytesIO(silver_body)).to_pandas()

        # Contar registros duplicados
        num_duplicates = silver_df.duplicated(subset=['User Id']).sum()

        # Remover duplicidades com base no campo "User Id"
        gold_df = silver_df.drop_duplicates(subset=['User Id'])

        # Converter o DataFrame para o formato Parquet
        parquet_buffer = BytesIO()
        pq.write_table(pa.Table.from_pandas(gold_df), parquet_buffer)
        parquet_buffer.seek(0)

        # Gravar o arquivo Parquet na camada gold no S3
        s3_client.put_object(Body=parquet_buffer.getvalue(), Bucket=s3_bucket, Key=gold_prefix + f'{filename_gold}.parquet')

        # Mensagem a ser enviada no slack
        message = f'*[Camada Gold]*\n\nEtapa concluída com sucesso!\n\nDados atualizados no arquivo "{filename_gold}.parquet"\n\n{num_duplicates} registros duplicados foram removidos'

    except ClientError as e:
        # Mensagem a ser enviada no slack em caso de erro
        message = f'*[Camada Gold]*\n\nOcorreu o erro abaixo:\n\n{str(e)}'

    send_notification_slack(message)

# Definir argumentos padrão da DAG
default_args = {
    'owner': 'Ítalo Ferreira',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 21),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir DAG
dag = DAG(
    'people_pipeline',
    default_args=default_args,
    description='Processa dados da camada bronze para a camada silver e gold',
    schedule_interval='@daily',
)

# Definir operadores

start = EmptyOperator(
    task_id='Start'
)

read_bronze_task = PythonOperator(
    task_id='read_bronze_data',
    python_callable=read_bronze_data,
    provide_context=True,
    dag=dag,
)

write_silver_task = PythonOperator(
    task_id='write_silver_data',
    python_callable=write_silver_data,
    dag=dag,
)

write_gold_task = PythonOperator(
    task_id='write_gold_data',
    python_callable=write_gold_data,
    dag=dag,
)

end = EmptyOperator(
    task_id='End'
)

# Definir dependência entre tarefas
start >> read_bronze_task >> write_silver_task >> write_gold_task >> end