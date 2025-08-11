
import os
import logging
import requests
from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('flask_app')

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_dev")

# Email configuration
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'thebooksoft@gmail.com',
    'password': 'knnw jaqe lyql xcps',
    'from_email': 'thebooksoft@gmail.com'
}

# OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')

# Subdomain support
ALLOWED_HOSTS = ['localhost:5000', '0.0.0.0:5000', 'stdavid.stake-employment.com', 'stjohns.stake-employment.com']

# ========== Helper Functions ==========
def format_resume_content(content):
    """Format the resume content for email display"""
    formatted = "RESUME\n"
    formatted += "=" * 50 + "\n\n"
    sections = content.split('\n\n')
    for section in sections:
        if section.strip():
            lines = section.split('\n')
            if lines[0].strip().isupper() and len(lines[0].strip()) > 2:
                formatted += lines[0].strip() + "\n"
                formatted += "-" * len(lines[0].strip()) + "\n"
                if len(lines) > 1:
                    formatted += '\n'.join(lines[1:]) + "\n\n"
                else:
                    formatted += "\n"
            else:
                formatted += section + "\n\n"
    return formatted

# ========== Routes ==========
@app.route('/')
def index():
    return render_template('Unemployment.html', host=request.host)

@app.route('/spiritual-guide')
def spiritual_guide():
    return render_template('SpiritualGuide.html', host=request.host)

@app.route('/spiritual-help')
def spiritual_help():
    return render_template('Spiritual-Help.html', host=request.host)

@app.route('/ministers-role')
def ministers_role():
    return render_template('MinistersRole.html', host=request.host)

@app.route('/ministers-help')
def ministers_help():
    return render_template('Minister-Help.html', host=request.host)

@app.route('/resume-draft')
def resume_draft():
    return render_template('Resume-Draft.html', host=request.host)

@app.route('/resume-draft-help')
def resume_draft_help():
    return render_template('Resume-Draft-Help.html', host=request.host)

@app.route('/resume-submit2ai-help')
def resume_submit2ai_help():
    return render_template('Resume-Submit2ai-Help.html', host=request.host)

@app.route('/resume-submit2ai')
def resume_submit2ai():
    return render_template('Resume-Submit2ai.html', host=request.host)

@app.route('/cover-letter')
def cover_letter():
    return render_template('CoverLetterDraft.html', host=request.host)

@app.route('/cover-letter-help')
def cover_letter_help():
    return render_template('CoverLetterDraft-Help.html', host=request.host)

@app.route('/cover-submit')
def cover_submit():
    return render_template('CoverLetterSubmit2ai.html', host=request.host)

@app.route('/cover-submit-help')
def cover_submit_help():
    return render_template('CoverLetterSubmit2ai-Help.html', host=request.host)

@app.route('/email-stake')
def email_stake():
    return render_template('Noemails-message.html', host=request.host)

@app.route('/email-stake-help')
def email_stake_help():
    return render_template('Email-Help.html', host=request.host)

@app.route('/job-search')
def job_search():
    return render_template('JobSearch.html', host=request.host)

@app.route('/job-search-help')
def job_search_help():
    return render_template('Job-Help.html', host=request.host)

@app.route('/custom-cover')
def custom_cover():
    return render_template('Cover-Custom.html', host=request.host)

@app.route('/improve-custom-cover', methods=['POST'])
def improve_custom_cover():
    """
    Customizes a cover letter to better match a specific job posting using AI
    Expects JSON with:
    - job_cover: The applicant's current cover letter text
    - job_posting: The job description to customize for
    """
    try:
        # Validate request
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({'error': 'Request must be JSON'}), 415

        data = request.get_json()
        job_cover = data.get('job_cover', '').strip()
        job_posting = data.get('job_posting', '').strip()

        if not job_cover:
            logger.warning("Empty cover letter received")
            return jsonify({'error': 'Cover letter text is required'}), 400
        if not job_posting:
            logger.warning("Empty job posting received")
            return jsonify({'error': 'Job posting is required'}), 400

        logger.info(f"Processing cover letter customization (Cover: {len(job_cover)} chars, Posting: {len(job_posting)} chars)")

        # Prepare AI prompt with clear instructions
        prompt = f"""
        **Task:** Customize this cover letter to perfectly match the job posting while maintaining professional tone.

        **Original Cover Letter:**
        {job_cover[:10000]}  # Limiting input size

        **Job Posting:**
        {job_posting[:5000]}

        **Instructions:**
        1. Maintain the original structure (salutation, body, closing)
        2. Highlight matching skills and qualifications
        3. Use keywords from the job description
        4. Keep professional tone
        5. Make it concise (1 page maximum when formatted)
        6. Output should be ready-to-use cover letter format
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional career coach with 15+ years experience writing cover letters."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.5,  # Balanced creativity and accuracy
            "max_tokens": 2000,
            "top_p": 0.9
        }

        # Call OpenAI API with timeout
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # 30-second timeout
        )

        # Handle API response
        response.raise_for_status()
        ai_response = response.json()

        if 'choices' not in ai_response or not ai_response['choices']:
            logger.error("Unexpected API response format")
            return jsonify({'error': 'Unexpected API response'}), 500

        improved_cover = ai_response['choices'][0]['message']['content']

        # Post-processing cleanup
        improved_cover = improved_cover.replace("```", "").strip()

        logger.info("Successfully generated customized cover letter")
        return jsonify({
            'improved_cover_letter': improved_cover,
            'word_count': len(improved_cover.split()),
            'status': 'success'
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"API connection error: {str(e)}")
        return jsonify({
            'error': 'AI service unavailable',
            'details': str(e)
        }), 503
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return jsonify({'error': 'Invalid API response'}), 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/improve-custom-resume', methods=['POST'])
def improve_custom_resume():
    """
    Customizes a resume to better match a specific job posting using AI
    Expects JSON with:
    - job_resume: The applicant's current resume text
    - job_posting: The job description to customize for
    """
    try:
        # Validate request
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({'error': 'Request must be JSON'}), 415

        data = request.get_json()
        job_resume = data.get('job_resume', '').strip()
        job_posting = data.get('job_posting', '').strip()

        if not job_resume:
            logger.warning("Empty resume received")
            return jsonify({'error': 'Resume text is required'}), 400
        if not job_posting:
            logger.warning("Empty job posting received")
            return jsonify({'error': 'Job posting is required'}), 400

        logger.info(f"Processing resume customization (Resume: {len(job_resume)} chars, Posting: {len(job_posting)} chars)")

        # Prepare AI prompt with clear instructions
        prompt = f"""
        **Task:** Customize this resume to perfectly match the job posting while maintaining original structure.

        **Resume Content:**
        {job_resume[:10000]}  # Limiting input size

        **Job Posting:**
        {job_posting[:5000]}

        **Instructions:**
        1. Keep original section structure (Experience, Education, etc.)
        2. Highlight matching skills and qualifications
        3. Reorder bullet points to prioritize relevant experience
        4. Use keywords from the job description
        5. Maintain professional tone
        6. Don't invent experience the applicant doesn't have
        7. Output should be ready-to-use resume format
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional resume writer with 15+ years experience. Customize resumes to match specific jobs."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,  # Lower for more factual responses
            "max_tokens": 3000,
            "top_p": 0.9
        }

        # Call OpenAI API with timeout
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # 30-second timeout
        )

        # Handle API response
        response.raise_for_status()
        ai_response = response.json()

        if 'choices' not in ai_response or not ai_response['choices']:
            logger.error("Unexpected API response format")
            return jsonify({'error': 'Unexpected API response'}), 500

        improved_resume = ai_response['choices'][0]['message']['content']

        # Post-processing cleanup
        improved_resume = improved_resume.replace("```", "").strip()

        logger.info("Successfully generated customized resume")
        return jsonify({
            'improved_cover_letter': improved_resume,
            'word_count': len(improved_resume.split()),
            'status': 'success'
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"API connection error: {str(e)}")
        return jsonify({
            'error': 'AI service unavailable',
            'details': str(e)
        }), 503
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return jsonify({'error': 'Invalid API response'}), 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
@app.route('/custom-cover-help')
def custom_cover_help():
    return render_template('Cover-Custom-Help.html', host=request.host)

@app.route('/custom-resume')
def custom_resume():
    return render_template('Resume-Custom.html', host=request.host)

@app.route('/custom-resume-help')
def custom_resume_help():
    return render_template('Resume-Custom-Help.html', host=request.host)

@app.route('/interview-quest')
def interview_quest():
    return render_template('InterviewQuestions.html', host=request.host)

@app.route('/generate-interview-questions', methods=['POST'])
def generate_interview_questions():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        job_title = data.get('job_title')
        job_description = data.get('job_description')

        if not job_title or not job_description:
            return jsonify({'error': 'Job title and description are required'}), 400

        prompt = f"""
        Generate 10-15 relevant interview questions for a {job_title} position based on:
        Job Description: {job_description}
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert career coach. Generate relevant interview questions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            return jsonify({'error': f'OpenAI API error: {error_msg}'}), 500

        questions = response.json()['choices'][0]['message']['content']
        return jsonify({'questions': questions})

    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        return jsonify({'error': 'Failed to generate questions'}), 500

@app.route('/send-questions-email', methods=['POST'])
def send_questions_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        recipient_email = data.get('email')
        subject = data.get('subject', 'Your Interview Questions')
        message = data.get('message', '')

        if not recipient_email:
            return jsonify({'error': 'Email is required'}), 400

        if not message:
            return jsonify({'error': 'No questions to send'}), 400

        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['from_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)

        return jsonify({'success': True, 'message': f'Questions sent to {recipient_email}'})

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/interview-help')
def interview_help():
    return render_template('Interview-Help.html', host=request.host)

@app.route('/feed-back')
def feed_back():
    return render_template('Feedback.html', host=request.host)

@app.route('/send-email-page')
def send_email_page():
    logger.info("Accessed /send-email-page")
    return render_template('send-email.html', host=request.host)

@app.route('/send-resume-email', methods=['POST'])
def send_resume_email():
    try:
        recipient_email = request.form.get('email')
        subject = request.form.get('subject', 'Your Resume')
        resume_content = request.form.get('message', '')

        logger.debug(f"Email request - Recipient: {recipient_email}")
        logger.debug(f"Resume content length: {len(resume_content) if resume_content else 0}")

        if not recipient_email:
            logger.error("No recipient email provided")
            return jsonify({'error': 'Email is required'}), 400

        if not resume_content or not resume_content.strip():
            logger.error("No resume content provided")
            return jsonify({'error': 'Resume content is required'}), 400

        formatted_content = format_resume_content(resume_content)

        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['from_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(formatted_content, 'plain', 'utf-8'))

        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)

        logger.info(f"Email sent successfully to {recipient_email}")
        return jsonify({
            'success': True,
            'message': f'Resume sent successfully to {recipient_email}'
        })

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return jsonify({'error': 'Email authentication failed'}), 500
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return jsonify({'error': 'Failed to send email'}), 500
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/improve-resume', methods=['POST'])
def improve_resume():
    resume_text = request.json.get('resume_text') if request.json else None
    if not resume_text or not resume_text.strip():
        return jsonify({'error': 'No resume text provided'}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional resume editor. Improve the following resume."
            },
            {
                "role": "user",
                "content": resume_text
            }
        ]
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({'error': 'API request failed', 'details': response.text}), 500

        data = response.json()
        improved_text = data['choices'][0]['message']['content']
        return jsonify({'improved_resume': improved_text})
    except Exception as e:
        logger.error(f"Error improving resume: {e}")
        return jsonify({'error': 'Failed to improve resume'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

