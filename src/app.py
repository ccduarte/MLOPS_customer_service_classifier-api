import json
import spacy
import nltk
import string
import re
import boto3
import joblib
from datetime import datetime

# Carregar o modelo de linguagem do SpaCy
nlp = spacy.load('pt_core_news_sm')

# Configurar NLTK para usar o diretório de dados
nltk.data.path.append('/opt/nltk_data')

# Carregar stopwords do NLTK
from nltk.corpus import stopwords
stops = set(stopwords.words('portuguese'))

# Inicializar clientes do boto3
s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

# Carregar modelo e vetorizador localmente
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Ler a versão do modelo de um arquivo local
with open("model_version.txt", 'r', encoding='utf8') as file:
    model_version = file.read()

def limpar_padroes(texto):
    padroes = [
        'XXXX', 'XXX', 'xxxx', 'Xxxx', 'xx', 'XX',
        r'\r', r'\n',
        r'\d{1,2}/\d{1,2}/\d{4}',  # Data xx/xx/xxxx
        r'\d{2}/\d{2}/\d{4}',  # Data xx/xx/xxxx (sem espaço)
        r'\d{1,2}/\d{1,2}/\d{4}/\d{2}/\d{2}',  # Data xx/xx/xxxx/xx/xx
        r'/Xxxx', '\(', '\)', "'", '"',
        r'\{\$[\d\.,]+\}',
        r'XX/XX/',  # Padrão XX/XX/
        r'xx/xx/',  # Padrão xx/xx/
        r'//',  # Padrão //
        r'/xx/xx '  # Padrão /xx/xx com espaço
    ]

    for padrao in padroes:
        texto = re.sub(padrao, '', texto, flags=re.IGNORECASE)

    # Substituir "{$ qualquer_valor}" por "R$ qualquer_valor"
    texto = re.sub(r'\{\$ *([\d\.,]+)\}', lambda match: '$ ' + match.group(1), texto)

    return texto

def remove_punctuation(text):
    table = str.maketrans('', '', string.punctuation)
    text = text.translate(table)
    return text

def prepare_payload(data):
    processed_data = []
    for item in data:
        texto_limpo = limpar_padroes(item['descricao_reclamacao'])
        texto_sem_pontuacao = remove_punctuation(texto_limpo)
        processed_data.append(texto_sem_pontuacao)
    return processed_data

def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)

def write_real_data(data, prediction):
    now = datetime.now()
    now_formatted = now.strftime("%d-%m-%Y %H:%M")
    file_name = f"{now.strftime('%Y-%m-%d')}_text_classification_data.csv"
    data["prediction"] = prediction
    data["timestamp"] = now_formatted
    data["model_version"] = model_version
    s3 = boto3.client("s3")
    bucket_name = "customer-service-classifier"
    s3_path = "text-classification-real-data"
    try:
        existing_object = s3.get_object(Bucket=bucket_name, Key=f'{s3_path}/{file_name}')
        existing_data = existing_object['Body'].read().decode('utf-8').strip().split('\n')
        existing_data.append(','.join(map(str, data.values())))
        updated_content = '\n'.join(existing_data)
    except s3.exceptions.NoSuchKey:
        updated_content = ','.join(data.keys()) + '\n' + ','.join(map(str, data.values()))
    s3.put_object(Body=updated_content, Bucket=bucket_name, Key=f'{s3_path}/{file_name}')

def input_metrics(data, prediction):
    cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'Text Classification Prediction',
                'Value': 1,
                'Dimensions': [{'Name': "Prediction", 'Value': remove_non_ascii(str(prediction))}]
            },
        ], Namespace='Text Classification Model')
    for key, value in data.items():
        cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'Text Classification Feature',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [{'Name': key, 'Value': remove_non_ascii(str(value))}]
            },
        ], Namespace='Text Classification Features')

def handler(event, context=False):
    print(event)
    print(context)
    data = event["data"]
    print(data)
    data_processed = prepare_payload(data)
    text_vect = vectorizer.transform(data_processed)
    predictions = model.predict(text_vect)
    results = []
    for item, prediction in zip(data, predictions):
        result = {
            'id_reclamacao': item['id_reclamacao'],
            'data_abertura': item['data_abertura'],
            'descricao_reclamacao': item['descricao_reclamacao'],
            'prediction': prediction
        }
        results.append(result)
        input_metrics(item, prediction)
        write_real_data(item, prediction)
    return {
        'statusCode': 200,
        'body': json.dumps(results, ensure_ascii=False),  # Adiciona ensure_ascii=False para suportar caracteres não-ASCII
        'version': model_version
    }
