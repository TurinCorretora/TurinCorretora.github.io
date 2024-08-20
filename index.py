from flask import Flask, render_template, request, flash, redirect, url_for
from config import email, senha
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from werkzeug.utils import secure_filename
from email.mime.base import MIMEBase
from email import encoders
import uuid
import tempfile

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Adicione uma chave secreta para as mensagens flash

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    email_form = request.form['email']
    telefone = request.form['telefone']
    idade = request.form['idade']
    cidade = request.form['cidade']
    planos = request.form.getlist('planos')
    abrangencia = request.form.getlist('abrangencia')
    observacoes = request.form.get('informacoes', '')  # Capture the "Observações" field, defaulting to an empty string if not provided

    planos_selecionados = ", ".join(planos)
    abrangencia_selecionada = ", ".join(abrangencia)
    
    # Formatando o número do telefone para o link do WhatsApp
    telefone_link = f"https://wa.me/{telefone}"

    # Start building the email message
    mensagem = f"""
    <html>
        <body>
            <p>Nome: {nome}</p>
            <p>Email: {email_form}</p>
            <p>Telefone: <a href="{telefone_link}">{telefone_link}</a></p>
            <p>Idade: {idade}</p>
            <p>Cidade: {cidade}</p>
            <p>Planos Selecionados: {planos_selecionados}</p>
            <p>Tipo de Abrangência: {abrangencia_selecionada}</p>
    """

    # Add "Observações" to the message if it's not empty
    if observacoes:
        mensagem += f"<p>Observações: {observacoes}</p>"

    # Close the HTML body
    mensagem += """
        </body>
    </html>
    """

    # Since this form submission does not include attachments, pass an empty list
    if send_email(mensagem, []):  # Adding an empty list for attachments
        flash('Formulário enviado com sucesso!', 'success')
    else:
        flash('Erro ao enviar o formulário. Tente novamente mais tarde.', 'error')

    return redirect(url_for('individual'))

def send_email(mensagem):
    sender_email = email
    receiver_email = 'turincorretora@gmail.com'
    password = senha

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Solicitação de Cotação"

    msg.attach(MIMEText(mensagem, 'html'))  # Mudando para 'html' para renderizar o link corretamente

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Habilita a saída de depuração
            server.starttls()  # Inicia a conexão TLS
            server.login(sender_email, password)  # Faz a autenticação
            server.sendmail(sender_email, receiver_email, msg.as_string())  # Envia o email
            print("Email enviado com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


# Defina o diretório de upload (pasta de downloads)
UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_unique_filename(filename):
    """Gera um nome de arquivo único, utilizando UUID."""
    unique_id = str(uuid.uuid4())
    ext = filename.split('.')[-1]
    return f"{unique_id}.{ext}"

@app.route('/cotar', methods=['POST'])
def cotar():
    try:
        # Captura os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        idade = request.form['idade']
        
        cnh = request.files['cnh']
        documento_veiculo = request.files['documento_veiculo']
        comprovante_residencia = request.files['comprovante_residencia']

        # Gera um arquivo temporário para armazenar as informações de depuração
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(f"Nome: {nome}\n".encode())
            temp_file.write(f"CPF: {cpf}\n".encode())
            temp_file.write(f"Idade: {idade}\n".encode())
            temp_file.write(f"Arquivos Recebidos: {cnh.filename}, {documento_veiculo.filename}, {comprovante_residencia.filename}\n".encode())
            debug_file_path = temp_file.name

        # Cria o diretório se ele não existir
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Gerando nomes de arquivos únicos
        cnh_filename = generate_unique_filename(secure_filename(cnh.filename))
        documento_veiculo_filename = generate_unique_filename(secure_filename(documento_veiculo.filename))
        comprovante_residencia_filename = generate_unique_filename(secure_filename(comprovante_residencia.filename))
        
        cnh_path = os.path.join(app.config['UPLOAD_FOLDER'], cnh_filename)
        documento_veiculo_path = os.path.join(app.config['UPLOAD_FOLDER'], documento_veiculo_filename)
        comprovante_residencia_path = os.path.join(app.config['UPLOAD_FOLDER'], comprovante_residencia_filename)
        
        # Salvando os arquivos com nomes únicos
        cnh.save(cnh_path)
        documento_veiculo.save(documento_veiculo_path)
        comprovante_residencia.save(comprovante_residencia_path)

        # Adicione as informações relevantes ao arquivo de depuração
        with open(debug_file_path, 'a') as temp_file:
            temp_file.write(f"CNH salva em: {cnh_path}\n")
            temp_file.write(f"Documento do Veículo salvo em: {documento_veiculo_path}\n")
            temp_file.write(f"Comprovante de Residência salvo em: {comprovante_residencia_path}\n")

        # Enviar o e-mail com o arquivo de depuração como anexo
        if send_email("Informações de Depuração", [], debug_file_path):
            flash('Formulário enviado com sucesso!', 'success')
        else:
            flash('Erro ao enviar o formulário. Tente novamente mais tarde.', 'error')

        return redirect(url_for('seguros'))

    except Exception as e:
        print(f"Erro ao processar o formulário: {e}")
        return "Ocorreu um erro ao processar o seu pedido. Tente novamente mais tarde."

def send_email(subject, attachments, debug_file_path):
    sender_email = email  # Seu email
    receiver_email = 'turincorretora@gmail.com'
    password = senha  # Sua senha

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Anexar arquivo de depuração
    with open(debug_file_path, 'rb') as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(debug_file_path)}')
    msg.attach(attachment)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email enviado com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

@app.route('/individual')
def individual():
    return render_template('individual.html')


@app.route('/seguros')
def seguros():
    return render_template('seguros.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
