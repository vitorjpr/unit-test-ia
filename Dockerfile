FROM python:3.9-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY app /app
COPY templates /app/templates

# Instala o gunicorn para produção
RUN pip install gunicorn

# Exponha a porta que a aplicação Flask está usando
EXPOSE 5000

# Comando para rodar o gunicorn, garantindo que o arquivo de ambiente .env seja carregado
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
