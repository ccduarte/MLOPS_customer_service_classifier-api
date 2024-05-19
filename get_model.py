import json
import os
import requests

# URL da API do Iterative Studio
url = "https://studio.iterative.ai/api/model-registry/get-download-uris"

# Defina o seu token de acesso do Studio como um cabeçalho para a solicitação
headers = {
    "Authorization": "token dsat_1XwP6Xd7PMaytm5hnH56jIwEKklRGsQvf7P5lMFFTvEYvKWCg"
}

# Parâmetros da solicitação
params = {
    "repo": "github:ccduarte/MLOPS_customer_service_classifier",
    "name": "customer_service_classifier",
    "version": "v0.0.3"
}

# Enviar solicitação para obter os URIs de download
response = requests.get(url, headers=headers, params=params)

# Verificar se a solicitação foi bem-sucedida
if response.status_code != 200:
    print(f"Erro na solicitação: {response.status_code}")
    print(response.content)
    exit(1)

# Analisar a resposta JSON
download_uris = json.loads(response.content)

# Criar diretório para salvar os arquivos, se não existir
output_dir = "downloaded_model"
os.makedirs(output_dir, exist_ok=True)

# Baixar e salvar cada arquivo
for rel_path, obj_url in download_uris.items():
    # Verificar se a URL é válida
    if not obj_url.startswith("http"):
        print(f"URL inválida: {obj_url}")
        continue

    print(f"Baixando {rel_path} de {obj_url}")

    # Enviar solicitação para baixar o arquivo
    obj_response = requests.get(obj_url)

    # Verificar se a solicitação foi bem-sucedida
    if obj_response.status_code == 200:
        file_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(obj_response.content)
        print(f"Arquivo salvo em {file_path}")
    else:
        print(f"Erro ao baixar {rel_path}: {obj_response.status_code}")
        print(obj_response.content)
