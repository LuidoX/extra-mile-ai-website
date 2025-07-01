from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def calculate_ai_readiness_score(data):
    """Calculate AI readiness score based on assessment responses"""
    score = 0
    max_score = 100
    
    # Business size scoring
    if data.get('employees') == '1-10':
        score += 15
    elif data.get('employees') == '11-50':
        score += 20
    elif data.get('employees') == '51-200':
        score += 25
    elif data.get('employees') == '200+':
        score += 30
    
    # Technology adoption scoring
    tech_tools = data.get('current_tools', [])
    if isinstance(tech_tools, list):
        score += min(len(tech_tools) * 5, 20)
    
    # Budget scoring
    if data.get('budget') == 'under-1k':
        score += 10
    elif data.get('budget') == '1k-5k':
        score += 15
    elif data.get('budget') == '5k-10k':
        score += 20
    elif data.get('budget') == '10k-25k':
        score += 25
    elif data.get('budget') == '25k+':
        score += 30
    
    # Timeline scoring
    if data.get('timeline') == 'immediately':
        score += 15
    elif data.get('timeline') == '1-3-months':
        score += 12
    elif data.get('timeline') == '3-6-months':
        score += 8
    elif data.get('timeline') == '6-12-months':
        score += 5
    
    # Goals scoring
    goals = data.get('goals', [])
    if isinstance(goals, list):
        score += min(len(goals) * 3, 15)
    
    return min(score, max_score)

def send_notification_email(assessment_data, score):
    """Send email notification about new assessment submission"""
    try:
        # Email configuration (you'll set these later in Vercel)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        email_user = os.environ.get('EMAIL_USER')
        email_password = os.environ.get('EMAIL_PASSWORD')
        recipient_email = os.environ.get('RECIPIENT_EMAIL')
        
        if not all([email_user, email_password, recipient_email]):
            print("Email configuration missing - will set up later")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = f"New AI Assessment Submission - Score: {score}%"
        
        # Email body
        body = f"""
        New AI Assessment Submission
        
        Contact Information:
        Name: {assessment_data.get('name', 'Not provided')}
        Email: {assessment_data.get('email', 'Not provided')}
        Phone: {assessment_data.get('phone', 'Not provided')}
        Company: {assessment_data.get('company', 'Not provided')}
        
        Assessment Details:
        AI Readiness Score: {score}%
        Employees: {assessment_data.get('employees', 'Not provided')}
        Industry: {assessment_data.get('industry', 'Not provided')}
        Current Tools: {', '.join(assessment_data.get('current_tools', []))}
        Budget: {assessment_data.get('budget', 'Not provided')}
        Timeline: {assessment_data.get('timeline', 'Not provided')}
        Goals: {', '.join(assessment_data.get('goals', []))}
        
        Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, recipient_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

@app.route('/api/submit-assessment', methods=['POST'])
def submit_assessment():
    try:
        # Get form data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'company']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Calculate AI readiness score
        score = calculate_ai_readiness_score(data)
        
        # Add timestamp
        data['submitted_at'] = datetime.now().isoformat()
        data['score'] = score
        
        # Send notification email (will work once you configure email settings)
        email_sent = send_notification_email(data, score)
        
        # Log the submission
        print(f"Assessment submitted: {data['name']} - Score: {score}%")
        
        # Return success response
        return jsonify({
            'success': True,
            'score': score,
            'message': 'Assessment submitted successfully',
            'email_sent': email_sent
        })
        
    except Exception as e:
        print(f"Error processing assessment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# For Vercel serverless functions
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)
