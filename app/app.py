import os
import zipfile
import tempfile
import openai
import threading
from datetime import datetime
from flask import Flask, request, send_file, render_template, jsonify
from dotenv import load_dotenv
import logging

# Configuração de log
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurar o cliente OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Variáveis globais para armazenar o progresso e o resultado
progress = {"current": 0, "total": 0, "finished": False}
result = {"status": "Não iniciado", "file_path": None}

def generate_tests_with_gpt(java_code):
    prompt = f"""Generate a comprehensive JUnit test class for the following Java code:

{java_code}

Please ensure the following:
1. The test class name should be 'Test' followed by the original class name.
2. Include necessary JUnit and Mockito imports.
3. Create test methods for each public method in the original class.
4. Use appropriate JUnit assertions and Mockito verifications.
5. Include setup methods if necessary (e.g., @BeforeEach).
6. Add comments explaining the purpose of each test.
7. Provide ONLY the Java code for the test class, without any additional text or markdown formatting.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in generating JUnit tests for Java code. Provide only the Java code without any additional text or explanations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.2
    )
    test_code = response.choices[0].message['content']
    
    # Remove qualquer texto antes ou depois do código Java
    test_code = test_code.strip()
    if test_code.startswith("```java"):
        test_code = test_code[7:]
    if test_code.endswith("```"):
        test_code = test_code[:-3]
    
    logging.info("Teste JUnit gerado pelo GPT-4.")
    return test_code.strip()

def is_valid_junit_test(test_code):
    return "import org.junit" in test_code and "@Test" in test_code and "class Test" in test_code

def format_java_code(java_code):
    # Garantir que o código comece com uma declaração de pacote
    if not java_code.strip().startswith("package"):
        java_code = "package com.example;\n\n" + java_code

    # Garantir que o código termine com uma chave de fechamento
    java_code = java_code.strip()
    if not java_code.endswith("}"):
        java_code += "\n}"

    return java_code

def fix_java_code_with_gpt(java_code):
    prompt = f"""Please fix and improve the following Java code. Ensure it's a valid JUnit test class, follows best practices, and compiles correctly. Here's the code:

{java_code}

Please provide only the corrected Java code without any additional explanations or markdown formatting.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert Java developer specializing in writing and fixing JUnit tests. Provide only the corrected Java code without any additional text or explanations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.2
    )
    fixed_code = response.choices[0].message['content']
    
    # Remove qualquer texto antes ou depois do código Java
    fixed_code = fixed_code.strip()
    if fixed_code.startswith("```java"):
        fixed_code = fixed_code[7:]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code[:-3]
    
    logging.info("Código Java corrigido pelo GPT-4.")
    return fixed_code.strip()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate-tests', methods=['POST'])
def generate_tests_api():
    global result, progress
    
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    
    if not file.filename.endswith('.zip'):
        return 'Por favor, envie um arquivo ZIP', 400
    
    # Ler o conteúdo do arquivo para a memória
    file_content = file.read()
    
    # Redefinir progresso e resultado
    progress = {"current": 0, "total": 0, "finished": False}
    result = {"status": "Processando", "file_path": None}

    # Iniciar o processamento em uma thread separada
    thread = threading.Thread(target=process_zip, args=(file_content, file.filename))
    thread.start()
    
    return jsonify({"message": "Processamento iniciado"}), 202

def process_zip(file_content, filename):
    global progress, result
    
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    zip_output_path = os.path.join(output_dir, f'updated_project_{timestamp}.zip')
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logging.info(f"Arquivo {filename} salvo no diretório temporário.")
        
        # Salvar e descompactar o ZIP
        zip_path = os.path.join(temp_dir, filename)
        with open(zip_path, 'wb') as f:
            f.write(file_content)
        
        extract_dir = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        logging.info(f"Arquivo {filename} descompactado para {extract_dir}.")
        
        # Lista para armazenar os nomes dos arquivos de teste criados
        created_tests = []
        
        # Contar o número total de arquivos Java
        total_files = sum(1 for root, dirs, files in os.walk(extract_dir) for file in files if file.endswith('.java'))
        progress["total"] = total_files
        progress["current"] = 0

        logging.info(f"Total de arquivos Java encontrados: {total_files}")
        
        # Gerar testes unitários
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as java_file:
                        java_code = java_file.read()
                    
                    # Gerar testes usando GPT
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        try:
                            test_code = generate_tests_with_gpt(java_code)
                            if is_valid_junit_test(test_code):
                                # Formatar o código de teste gerado
                                test_code = format_java_code(test_code)
                                # Corrigir o código de teste usando GPT
                                test_code = fix_java_code_with_gpt(test_code)
                                break
                            logging.warning(f"Tentativa {attempt + 1} falhou ao gerar um teste JUnit válido para {file}.")
                        except Exception as e:
                            logging.error(f"Erro na tentativa {attempt + 1} ao gerar testes para o arquivo {file_path}: {e}")
                    else:
                        logging.error(f"Falha ao gerar um teste JUnit válido para {file} após {max_attempts} tentativas.")
                        continue

                    # Salvar o teste gerado, formatado e corrigido
                    test_file_name = f"Test{os.path.splitext(file)[0]}.java"
                    test_file_path = os.path.join(root, test_file_name)
                    with open(test_file_path, 'w') as test_file:
                        test_file.write(test_code)
                    
                    # Adicionar o nome do arquivo de teste à lista
                    created_tests.append(test_file_name)
                    
                    logging.info(f"Teste JUnit válido gerado, formatado, corrigido e salvo em {test_file_path}.")
                    
                    # Atualizar o progresso
                    progress["current"] += 1
        
        # Criar o arquivo markdown com a lista de testes criados
        markdown_content = "# Arquivos de Teste JUnit Criados\n\n"
        for test in created_tests:
            markdown_content += f"- {test}\n"
        
        markdown_file_path = os.path.join(extract_dir, 'junit-tests-created.md')
        with open(markdown_file_path, 'w') as md_file:
            md_file.write(markdown_content)
        
        logging.info(f"Arquivo markdown com lista de testes JUnit criado em {markdown_file_path}.")
        
        # Recompactar o projeto
        with zipfile.ZipFile(zip_output_path, 'w') as zipf:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extract_dir)
                    zipf.write(file_path, arcname)
        
        logging.info(f"Novo arquivo ZIP com testes JUnit criado em {zip_output_path}.")
        
        # Marcar como concluído
        progress["current"] = progress["total"]
        progress["finished"] = True
        result["status"] = "Concluído"
        result["file_path"] = zip_output_path

@app.route('/progress')
def get_progress():
    return jsonify(progress)

@app.route('/result')
def get_result():
    global result
    if result["status"] == "Concluído" and result["file_path"]:
        return send_file(result["file_path"], as_attachment=True, download_name=os.path.basename(result["file_path"]))
    else:
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')