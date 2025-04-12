import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from flask import current_app

def enviar_email(destinatario, assunto, mensagem):
    """
    Função para enviar emails utilizando o servidor SMTP do Gmail.

    Args:
        destinatario (str): Endereço de email do destinatário.
        assunto (str): Assunto do email.
        mensagem (str): Corpo do email (HTML).
    """
    # Configurações do servidor SMTP do Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Porta para TLS
    email_remetente = 'seu_email@gmail.com'  # Substitua pelo seu email
    senha_remetente = 'sua_senha'  # Substitua pela sua senha ou senha de aplicativo

    # Construção da mensagem
    msg = MIMEMultipart()
    msg['From'] = email_remetente
    msg['To'] = destinatario
    msg['Subject'] = Header(assunto, 'utf-8')
    msg.attach(MIMEText(mensagem, 'html', 'utf-8'))

    try:
        # Conexão com o servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Inicia a criptografia TLS
        server.login(email_remetente, senha_remetente)

        # Envio do email
        server.sendmail(email_remetente, destinatario, msg.as_string())
        print(f"Email enviado para {destinatario}!")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
    finally:
        if server:
            server.quit()

if __name__ == '__main__':
    # Exemplo de uso da função
    destinatario = 'email_do_destinatario@example.com'  # Substitua
    assunto = 'Assunto do Email'
    mensagem = """
    <html>
    <head>
    <title>Exemplo de Email</title>
    </head>
    <body>
    <p>Este é um email de exemplo enviado com Python!</p>
    </body>
    </html>
    """
    enviar_email(destinatario, assunto, mensagem)