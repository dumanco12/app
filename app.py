import csv
import os
import socket
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Caminho do arquivo CSV onde os códigos serão armazenados
CAMINHO_CSV = "codigos_gerados.csv"

# Configurações da impressora Zebra
IP_IMPRESSORA = "192.168.0.117"  # Substitua pelo IP da sua impressora Zebra
PORTA_IMPRESSORA = 9100          # Porta padrão para impressoras Zebra

# Função para salvar os dados no arquivo CSV
def salvar_no_csv(nome_caixa, numero_nota, conteudo, sucesso):
    # Verificar se o arquivo CSV já existe
    arquivo_existe = os.path.exists(CAMINHO_CSV)
    
    # Abrir o arquivo CSV em modo de anexação (append)
    with open(CAMINHO_CSV, mode='a', newline='', encoding='utf-8') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)

        # Se o arquivo não existir, escreve o cabeçalho
        if not arquivo_existe:
            escritor_csv.writerow(['Nome da Caixa', 'Número da Nota Fiscal', 'Conteúdo da Caixa', 'Status'])

        # Dividir o conteúdo em linhas e formatar como uma tabela
        conteudo_formatado = ''
        for linha in conteudo.split("\n"):
            conteudo_formatado += f"{linha} | "  # Usamos " | " para separar as colunas de conteúdo

        # Remover o último " | "
        conteudo_formatado = conteudo_formatado.strip(" | ")

        # Escrever uma nova linha com os dados
        escritor_csv.writerow([nome_caixa, numero_nota, conteudo_formatado, sucesso])

# Função para gerar o comando ZPL do QR Code
def gerar_zpl(nome_caixa, conteudo):
    # Substitui as quebras de linha por " / " para evitar formatação inadequada no QR Code
    conteudo = conteudo.replace("\n", " / ")  # Substitui quebras de linha por um separador

    # Comando ZPL com o "Nome da Caixa" acima do QR Code e tamanho limitado
    zpl = (
        f"^XA"  # Inicia a impressão
        # Adiciona o "Nome da Caixa" acima do QR Code
        f"^FO250,50^A0,N,60,60^FD{nome_caixa}^FS"  # Posição e fonte para o nome da caixa
        # Adiciona o QR Code abaixo do "Nome da Caixa"
        f"^FO200,100"  # Posição do QR Code (ajuste para abaixo do nome da caixa)
        f"^BQN,3,5"  # Tipo e tamanho do QR Code (o número 2 controla o tamanho do QR Code)
        f"^FDQA,{conteudo}^FS"  # Dados do QR Code
        "^XZ"  # Finaliza a impressão
    )
    return zpl

# Função para enviar o comando ZPL para a impressora
def enviar_para_impressora(zpl_comando):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((IP_IMPRESSORA, PORTA_IMPRESSORA))
            cliente.sendall(zpl_comando.encode('utf-8'))
        return True
    except Exception as e:
        print(f"Erro ao enviar para a impressora: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_qr', methods=['POST'])
def gerar_qr_code():
    nome_caixa = request.form.get('nome_caixa')
    numero_nota = request.form.get('numero_nota')
    conteudo = request.form.get('conteudo')

    # Verificar se os campos estão preenchidos
    if not nome_caixa or not numero_nota or not conteudo:
        return jsonify({'status': 'erro', 'mensagem': 'Por favor, preencha todos os campos!'})

    # Substituir quebras de linha por uma sequência compactada
    conteudo = conteudo.replace("\n", " / ")  # Alterna \n por " / "

    # Montar o texto do QR Code com as quebras de linha convertidas
    dados_qr_code = f"Caixa Fracionada: {nome_caixa} / Nota Fiscal: {numero_nota} / Conteúdo da Caixa: {conteudo}"
    
    # Gerar o comando ZPL para o QR Code
    zpl_comando = gerar_zpl(nome_caixa, dados_qr_code)

    # Enviar para a impressora
    sucesso = enviar_para_impressora(zpl_comando)
    
    # Salvar as informações no arquivo CSV
    salvar_no_csv(nome_caixa, numero_nota, conteudo, 'Sucesso' if sucesso else 'Erro')

    if sucesso:
        return jsonify({'status': 'sucesso', 'mensagem': 'QR Code gerado e enviado para a impressora com sucesso!'})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Falha ao enviar para a impressora. Verifique a conexão.'})

if __name__ == '__main__':
    # Rodar Flask para acessar na rede local
    app.run(host='0.0.0.0', port=5000, debug=True)
