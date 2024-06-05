from flask import Flask, render_template, request, flash, redirect, url_for
from config import email, senha
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Adicione uma chave secreta para as mensagens flash

@app.route('/')
def form():
    return render_template('index.html')

from flask import Flask, render_template, request, flash, redirect, url_for
from config import email, senha
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Adicione uma chave secreta para as mensagens flash

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    idade = request.form['idade']
    cidade = request.form['cidade']
    planos = request.form.getlist('planos')
    abrangencia = request.form['abrangencia']

    planos_selecionados = ", ".join(planos)
    
    # Formatando o número do telefone para o link do WhatsApp
    telefone_link = f"https://wa.me/{telefone}"

    mensagem = f"""
    <html>
        <body>
            <p>Nome: {nome}</p>
            <p>Email: {email}</p>
            <p>Telefone: <a href="{telefone_link}">{telefone_link}</a></p>
            <p>Idade: {idade}</p>
            <p>Cidade: {cidade}</p>
            <p>Planos Selecionados: {planos_selecionados}</p>
            <p>Tipo de Abrangência: {abrangencia}</p>
        </body>
    </html>
    """

    if send_email(mensagem):
        flash('Formulário enviado com sucesso!', 'success')
    else:
        flash('Erro ao enviar o formulário. Tente novamente mais tarde.', 'error')

    return redirect(url_for('form'))

def send_email(mensagem):
    sender_email = email
    receiver_email = email
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

if __name__ == '__main__':
    app.run(debug=True)


