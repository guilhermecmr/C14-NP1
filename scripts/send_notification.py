import os
import smtplib
from email.mime.text import MIMEText

def main():
    email_to = os.environ.get("NOTIFICATION_EMAIL")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("EMAIL_USER")
    smtp_pass = os.environ.get("EMAIL_PASS")

    tests = os.environ.get("TESTS_STATUS", "unknown")
    build = os.environ.get("BUILD_STATUS", "unknown")
    coverage = os.environ.get("COVERAGE_STATUS", "unknown")
    deploy = os.environ.get("DEPLOY_STATUS", "unknown")    

    if not email_to:
        raise RuntimeError("NOTIFICATION_EMAIL não definida.")
    if not smtp_user or not smtp_pass:
        raise RuntimeError("EMAIL_USER/EMAIL_PASS não definidos.")

    subject = "CI/CD Status"
    body = f"""Pipeline finalizado!\n\nResultados:\n
    - Tests: {tests.upper()}\n- Build: {build.upper()}\n- Coverage: {coverage.upper()}\n- Deploy: {deploy.upper()}\n"""

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = email_to

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"E-mail enviado para {email_to} com sucesso.")

if __name__ == "__main__":
    main()