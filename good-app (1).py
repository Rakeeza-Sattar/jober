from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(
    __name__,
    template_folder='/home/ocottrell/unemployment/templates',
    static_folder='/home/ocottrell/unemployment/static',
    static_url_path='/static'
)

# Get your OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('Unemployment.html')

@app.route('/spiritual-guide')
def spiritual_guide():
    return render_template('SpiritualGuide.html')

@app.route('/ministers-role')
def ministers_role():
    return render_template('MinistersRole.html')

@app.route('/resume-draft')
def resume_draft():
    return render_template('Resume-Draft.html')

@app.route('/resume-submit2ai')
def resume_submit2ai():
   return render_template('Resume-Submit2ai.html')

@app.route('/cover-letter')
def cover_letter():
   return render_template('CoverLetterDraft.html')

@app.route('/cover-submit')
def cover_submit():
   return render_template('CoverLetterSubmit2ai.html')

@app.route('/email-stake')
def email_stake():
   return render_template('Noemails-message.html')

@app.route('/job-search')
def job_search():
   return render_template('JobSearch.html')

@app.route('/custom-cover')
def custom_resume():
   return render_template('Cover-Custom.html')

@app.route('/custom-resume')
def custom_cover():
   return render_template('Resume-Custom.html')

@app.route('/interview-quest')
def interview_quest():
   return render_template('InterviewQuestions.html')

@app.route('/feed-back')
def feed_back():
   return render_template('Feedback.html')

@app.route('/improve-resume', methods=['POST'])
def improve_resume():
    resume_text = request.json.get('resume_text')
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
                "content": "You are a professional resume editor. Improve the following resume by making it more concise, professional, and tailored for job applications."
            },
            {
                "role": "user",
                "content": resume_text
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({'error': 'API request failed', 'details': response.text}), 500

    data = response.json()
    improved_text = data['choices'][0]['message']['content']
    return jsonify({'improved_resume': improved_text})

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/improve-cover', methods=['POST'])
def improve_cover():
    resume_text = request.json.get('resume_text')
    if not resume_text or not resume_text.strip():
        return jsonify({'error': 'No cover letter text provided'}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional resume editor. Improve the following cover letter by making it more concise, professional, and tailored for job applications."
            },
            {
                "role": "user",
                "content": resume_text
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({'error': 'API request failed', 'details': response.text}), 500

    data = response.json()
    improved_text = data['choices'][0]['message']['content']
    return jsonify({'improved_resume': improved_text})

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/improve-custom-cover', methods=['POST'])
def improve_custom_cover():
    job_cover = request.json.get('job_cover')
    job_posting = request.json.get('job_posting')

    if not job_cover or not job_cover.strip():
        return jsonify({'error': 'No cover letter provided'}), 400

    if not job_posting or not job_posting.strip():
        return jsonify({'error': 'No job posting provided'}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "Improve the cover letter to align with the job posting. Focus on tailoring the tone, skills, and experience to match the job requirements."
            },
            {
                "role": "user",
                "content": f"Job Cover: {job_cover}\n\nJob Posting: {job_posting}"
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({'error': 'API request failed', 'details': response.text}), 500

    data = response.json()
    improved_cover_letter = data['choices'][0]['message']['content']
    return jsonify({'improved_cover_letter': improved_cover_letter})

if __name__ == '__main__':
    app.run(debug=True)



@app.route('/improve-custom-resume', methods=['POST'])
def improve_custom_resume():
    job_resume = request.json.get('job_resume')
    job_posting = request.json.get('job_posting')

    if not job_resume or not job_resume.strip():
        return jsonify({'error': 'No resume provided'}), 400

    if not job_posting or not job_posting.strip():
        return jsonify({'error': 'No job posting provided'}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "Improve the resume to align with the job posting. Focus on tailoring the tone, skills, and experience to match the job requirements."
            },
            {
                "role": "user",
                "content": f"Job Resume: {job_resume}\n\nJob Posting: {job_posting}"
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({'error': 'API request failed', 'details': response.text}), 500

    data = response.json()
    improved_cover_letter = data['choices'][0]['message']['content']
    return jsonify({'improved_cover_letter': improved_cover_letter})

if __name__ == '__main__':
    app.run(debug=True)

