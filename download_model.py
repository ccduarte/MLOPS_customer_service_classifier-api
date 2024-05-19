import requests
import os

# URL do modelo
model_url = "https://raw.githubusercontent.com/ccduarte/MLOPS_customer_service_classifier/master/models/model.pkl"
vectorizer_url = "https://raw.githubusercontent.com/ccduarte/MLOPS_customer_service_classifier/master/models/vectorizer.pkl"

# Diretório para salvar os arquivos baixados
output_dir = "downloaded_model"
os.makedirs(output_dir, exist_ok=True)

def download_file(url, output_path): 
    """
    Função para baixar um arquivo de um URL e salvá-lo localmente.
    
    Args:
        url (str): URL do arquivo a ser baixado.
        output_path (str): Caminho onde o arquivo será salvo.
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
        print(f"Arquivo salvo em {output_path}")
    else:
        print(f"Erro ao baixar o arquivo de {url}: {response.status_code}")

# Baixar o modelo
model_path = os.path.join(output_dir, "model.pkl")
download_file(model_url, model_path)

# Baixar o vectorizer
vectorizer_path = os.path.join(output_dir, "vectorizer.pkl")
download_file(vectorizer_url, vectorizer_path)
