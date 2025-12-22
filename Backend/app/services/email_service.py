"""
Сервис для отправки email-сообщений
Используется для восстановления пароля и уведомлений пользователей
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email-сообщений"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> MIMEMultipart:
        """Создание email-сообщения"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        
        if text_content:
            part1 = MIMEText(text_content, "plain", "utf-8")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part2)
        
        return message
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Отправка email-сообщения
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            html_content: HTML содержимое письма
            text_content: Текстовая версия письма (опционально)
        
        Returns:
            True если отправлено успешно, False в случае ошибки
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("SMTP настройки не заданы. Email не отправлен.")
                logger.info(f"[РЕЖИМ ОТЛАДКИ] Email для {to_email}:")
                logger.info(f"Тема: {subject}")
                logger.info(f"Содержимое: {text_content or html_content}")
                return True
            
            message = self._create_message(to_email, subject, html_content, text_content)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email успешно отправлен на {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки email на {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str
    ) -> bool:
        """
        Отправка письма для восстановления пароля
        
        Args:
            to_email: Email пользователя
            reset_token: Токен для сброса пароля
            user_name: Имя пользователя
        
        Returns:
            True если письмо отправлено успешно
        """
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        subject = "Восстановление пароля - Social Skills Coach"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f4f4f4;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 20px -30px;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Восстановление пароля</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, {user_name}!</p>
                    
                    <p>Мы получили запрос на восстановление пароля для вашего аккаунта в приложении <strong>Social Skills Coach</strong>.</p>
                    
                    <p>Для сброса пароля нажмите на кнопку ниже:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Восстановить пароль</a>
                    </center>
                    
                    <p>Или скопируйте и вставьте эту ссылку в браузер:</p>
                    <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Важно:</strong> Ссылка действительна в течение 1 часа. После этого времени вам нужно будет запросить новую ссылку.
                    </div>
                    
                    <p>Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо. Ваш пароль останется без изменений.</p>
                </div>
                
                <div class="footer">
                    <p>С уважением,<br>Команда Social Skills Coach</p>
                    <p style="margin-top: 10px;">
                        Это автоматическое письмо. Пожалуйста, не отвечайте на него.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        

        text_content = f"""
Восстановление пароля - Social Skills Coach

Здравствуйте, {user_name}!

Мы получили запрос на восстановление пароля для вашего аккаунта в приложении Social Skills Coach.

Для сброса пароля перейдите по ссылке:
{reset_link}

⚠️ ВАЖНО: Ссылка действительна в течение 1 часа. После этого времени вам нужно будет запросить новую ссылку.

Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо. Ваш пароль останется без изменений.

С уважением,
Команда Social Skills Coach

---
Это автоматическое письмо. Пожалуйста, не отвечайте на него.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_changed_notification(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Отправка уведомления об успешной смене пароля
        
        Args:
            to_email: Email пользователя
            user_name: Имя пользователя
        
        Returns:
            True если письмо отправлено успешно
        """
        subject = "Ваш пароль был изменён - Social Skills Coach"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f4f4f4;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 20px -30px;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                }}
                .success {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 10px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Пароль изменён</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, {user_name}!</p>
                    
                    <div class="success">
                        Ваш пароль был успешно изменён.
                    </div>
                    
                    <p>Теперь вы можете использовать новый пароль для входа в приложение <strong>Social Skills Coach</strong>.</p>
                    
                    <p>Если вы не меняли пароль, немедленно свяжитесь с нами для защиты вашего аккаунта.</p>
                </div>
                
                <div class="footer">
                    <p>С уважением,<br>Команда Social Skills Coach</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Ваш пароль был изменён - Social Skills Coach

Здравствуйте, {user_name}!

✅ Ваш пароль был успешно изменён.

Теперь вы можете использовать новый пароль для входа в приложение Social Skills Coach.

Если вы не меняли пароль, немедленно свяжитесь с нами для защиты вашего аккаунта.

С уважением,
Команда Social Skills Coach
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_verification_email(
        self,
        to_email: str,
        verification_code: str,
        user_name: str
    ) -> bool:
        """
        Отправка письма с кодом подтверждения email
        
        Args:
            to_email: Email пользователя
            verification_code: 6-значный код подтверждения
            user_name: Имя пользователя
        
        Returns:
            True если письмо отправлено успешно
        """
        subject = "Подтверждение email - Social Skills Coach"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f4f4f4;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 20px -30px;
                }}
                .content {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                }}
                .code-box {{
                    background-color: #f0f0f0;
                    border: 2px dashed #4CAF50;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✉️ Подтверждение Email</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, {user_name}!</p>
                    
                    <p>Спасибо за регистрацию в <strong>Social Skills Coach</strong>!</p>
                    
                    <p>Для завершения регистрации и активации вашего аккаунта, пожалуйста, введите код подтверждения:</p>
                    
                    <div class="code-box">
                        <div class="code">{verification_code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Важно:</strong> Код действителен в течение 24 часов.
                    </div>
                    
                    <p>Если вы не регистрировались в нашем приложении, просто проигнорируйте это письмо.</p>
                </div>
                
                <div class="footer">
                    <p>С уважением,<br>Команда Social Skills Coach</p>
                    <p style="margin-top: 10px;">
                        Это автоматическое письмо. Пожалуйста, не отвечайте на него.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Подтверждение Email - Social Skills Coach

Здравствуйте, {user_name}!

Спасибо за регистрацию в Social Skills Coach!

Для завершения регистрации и активации вашего аккаунта, пожалуйста, введите код подтверждения:

КОД: {verification_code}

⚠️ ВАЖНО: Код действителен в течение 24 часов.

Если вы не регистрировались в нашем приложении, просто проигнорируйте это письмо.

С уважением,
Команда Social Skills Coach

---
Это автоматическое письмо. Пожалуйста, не отвечайте на него.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


email_service = EmailService()
