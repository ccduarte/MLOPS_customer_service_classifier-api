# Use a imagem oficial Python como base para Lambda
FROM public.ecr.aws/lambda/python:3.10

# Defina o diretório de trabalho do Lambda
WORKDIR ${LAMBDA_TASK_ROOT}

# Copie os arquivos de requisitos e script de pós-instalação
COPY requirements.txt .
COPY post_install.sh .

# Instale os pacotes especificados e execute o script de pós-instalação
RUN pip install -r requirements.txt
RUN bash post_install.sh

# Baixar os recursos necessários do NLTK
RUN python -m nltk.downloader -d /opt/nltk_data stopwords

# Copie o código da função, o modelo, o vetor e a versão
COPY src/app.py .
COPY model.pkl .
COPY vectorizer.pkl .
COPY model_version.txt .

# Defina a variável de ambiente NLTK_DATA para o diretório de dados NLTK
ENV NLTK_DATA=/opt/nltk_data

# Defina o CMD para o handler da função Lambda
CMD [ "app.handler" ]
