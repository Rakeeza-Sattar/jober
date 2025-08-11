import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload settings - using absolute path for PythonAnywhere
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email configuration - PythonAnywhere specific
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.pythonanywhere.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', EMAIL_USERNAME)  # Use EMAIL_USERNAME as default

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with sample content and Email Myself button"""
    return render_template('index.html')

@app.route('/compose')
def compose():
    """Email composition page - shown after email is set"""
    if 'user_email' not in session:
        flash('Please set your email address first.', 'error')
        return redirect(url_for('index'))
    return render_template('compose.html')

@app.route('/set_email', methods=['POST'])
def set_email():
    """Set the user's email address in session"""
    email = request.form.get('email', '').strip()
    if email and '@' in email:
        session['user_email'] = email
        flash('Email address saved successfully!', 'success')
        return redirect(url_for('send_page_content'))
    else:
        flash('Please provide a valid email address.', 'error')
    return redirect(url_for('index'))

@app.route('/send_page_content')
def send_page_content():
    """Send the main page content to user's email"""
    if 'user_email' not in session:
        flash('Please set your email address first.', 'error')
        return redirect(url_for('index'))

    recipient = session['user_email']

    if not all([EMAIL_USERNAME, EMAIL_PASSWORD, FROM_EMAIL]):
        flash('Email service not configured. Please contact administrator.', 'error')
        return redirect(url_for('index'))

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = recipient
        msg['Subject'] = "Your Requested Page Content"

        page_content = """
        <h2>Welcome to Our Service</h2>
        <p>This is a sample page with interesting content that you requested to be emailed to yourself.</p>
        <h3>Features:</h3>
        <ul>
            <li>Easy email functionality</li>
            <li>Session-based user experience</li>
            <li>Professional email templates</li>
            <li>Secure file handling</li>
        </ul>
        <p>Thank you for using our Email Myself service!</p>
        """

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Requested Page Content</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f8f9fa; }}
                .footer {{ background: #e9ecef; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Requested Page Content</h1>
                    <p>Here's the content you requested to be emailed to you</p>
                </div>
                <div class="content">
                    {page_content}
                </div>
                <div class="footer">
                    <p>Sent via Email Myself Service</p>
                </div>
            </div>
        </body>
        </html>
        """

        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

        flash('Page content sent successfully to your email!', 'success')
        app.logger.info(f'Page content email sent successfully to {recipient}')

    except smtplib.SMTPAuthenticationError:
        flash('Email authentication failed. Please check your email credentials.', 'error')
    except Exception as e:
        flash(f'An error occurred while sending email: {str(e)}', 'error')
        app.logger.error(f'Error sending email: {str(e)}')

    return redirect(url_for('index'))

@app.route('/send_resume', methods=['POST'])
def send_resume():
    """Send resume and description to user's email"""
    if 'user_email' not in session:
        flash('Please set your email address first.', 'error')
        return redirect(url_for('index'))

    recipient = session['user_email']
    subject = request.form.get('subject', 'Resume and Description')
    description = request.form.get('description', '')

    if not all([EMAIL_USERNAME, EMAIL_PASSWORD, FROM_EMAIL]):
        flash('Email service not configured. Please contact administrator.', 'error')
        return redirect(url_for('compose'))

    resume_file = request.files.get('resume')
    if not resume_file or resume_file.filename == '':
        flash('Please select a resume file to upload.', 'error')
        return redirect(url_for('compose'))

    if not allowed_file(resume_file.filename):
        flash('Please upload a valid file (PDF, DOC, DOCX, or TXT).', 'error')
        return redirect(url_for('compose'))

    filepath = None
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject

        filename = secure_filename(resume_file.filename or 'resume')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)

        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .description {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Resume & Description</h1>
                    <p>Professional Profile Submission</p>
                </div>
                <div class="content">
                    <div class="description">
                        <h3>Professional Description:</h3>
                        <p>{description.replace(chr(10), '<br>')}</p>
                    </div>
                    <p><strong>Resume attached:</strong> {filename}</p>
                    <div class="footer">
                        <p>Sent via Email Myself Service</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(email_body, 'html'))

        with open(filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

        os.remove(filepath)
        flash('Resume and description sent successfully!', 'success')

    except smtplib.SMTPAuthenticationError:
        flash('Email authentication failed. Please check your email credentials.', 'error')
    except Exception as e:
        flash(f'An error occurred while sending your resume: {str(e)}', 'error')
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

    return redirect(url_for('compose'))

@app.route('/clear_email')
def clear_email():
    """Clear the stored email address from session"""
    session.pop('user_email', None)
    flash('Email address cleared.', 'info')
    return redirect(url_for('index'))

# For PythonAnywhere, this won't be executed when deployed
if __name__ == '__main__':
    app.run()