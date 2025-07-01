from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/assessment')
def assessment():
    return send_from_directory('.', 'assessment.html')

@app.route('/submit-assessment', methods=['POST'])
def submit_assessment():
    try:
        data = request.get_json()
        
        # Calculate AI readiness score
        score = calculate_ai_score(data)
        
        # Send notification email (if configured)
        send_notification_email(data, score)
        
        return jsonify({
            'success': True,
            'score': score,
            'message': 'Assessment submitted successfully!',
            'recommendation': get_recommendation(score)
        })
    except Exception as e:
        print(f"Error processing assessment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_ai_score(data):
    """Calculate AI readiness score based on assessment responses"""
    score = 0
    total_possible = 0
    
    # Scoring weights for different factors
    scoring_map = {
        'current_tech': {'high': 25, 'medium': 15, 'low': 5, 'none': 0},
        'team_size': {'large': 20, 'medium': 15, 'small': 10, 'solo': 5},
        'budget': {'high': 25, 'medium': 15, 'low': 8, 'minimal': 3},
        'urgency': {'immediate': 20, 'soon': 15, 'exploring': 10, 'no_rush': 5},
        'data_usage': {'extensive': 15, 'moderate': 10, 'minimal': 5, 'none': 0},
        'automation_interest': {'very_interested': 15, 'interested': 10, 'somewhat': 5, 'not_interested': 0}
    }
    
    # Calculate score based on responses
    for key, value in data.items():
        if key in scoring_map and value in scoring_map[key]:
            score += scoring_map[key][value]
            total_possible += max(scoring_map[key].values())
    
    # Normalize to 0-100 scale
    if total_possible > 0:
        normalized_score = (score / total_possible) * 100
    else:
        normalized_score = 50  # Default score if no valid responses
    
    return round(min(100, max(0, normalized_score)))

def get_recommendation(score):
    """Get recommendation based on AI readiness score"""
    if score >= 80:
        return "Excellent! You're ready for advanced AI implementation. Let's discuss enterprise solutions."
    elif score >= 60:
        return "Great potential! You're well-positioned for AI adoption. Let's start with high-impact solutions."
    elif score >= 40:
        return "Good foundation! With some preparation, you can successfully implement AI solutions."
    elif score >= 20:
        return "Getting started! Let's begin with simple automation and build from there."
    else:
        return "Perfect timing! Let's explore how AI can transform your business step by step."

def send_notification_email(data, score):
    """Send email notification about new assessment submission"""
    try:
        # Email configuration from environment variables
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        email_user = os.environ.get('EMAIL_USER', '')
        email_password = os.environ.get('EMAIL_PASSWORD', '')
        
        if not email_user or not email_password:
            print("Email not configured - skipping notification")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user  # Send to yourself
        msg['Subject'] = f"🚀 New AI Assessment: {score}% Readiness - {data.get('name', 'Unknown')}"
        
        # Email body
        body = f"""
New AI Assessment Submission!

CONTACT INFORMATION:
━━━━━━━━━━━━━━━━━━━━
👤 Name: {data.get('name', 'Not provided')}
📧 Email: {data.get('email', 'Not provided')}
📱 Phone: {data.get('phone', 'Not provided')}
🏢 Company: {data.get('company', 'Not provided')}
💼 Role: {data.get('role', 'Not provided')}

BUSINESS DETAILS:
━━━━━━━━━━━━━━━━━━━━
👥 Team Size: {data.get('team_size', 'Not provided')}
💰 Annual Turnover: {data.get('turnover', 'Not provided')}
🎯 Primary Goal: {data.get('primary_goal', 'Not provided')}

AI READINESS ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━
🎯 AI Readiness Score: {score}%
📊 Current Tech Level: {data.get('current_tech', 'Not provided')}
⚡ Implementation Urgency: {data.get('urgency', 'Not provided')}
💡 Main Interest: {data.get('main_interest', 'Not provided')}

RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━
{get_recommendation(score)}

NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━
1. Follow up within 24 hours
2. Schedule consultation call
3. Prepare tailored AI solution proposal

Submission Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Full Response Data:
{json.dumps(data, indent=2)}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Notification email sent for assessment score: {score}%")
        
    except Exception as e:
        print(f"Failed to send notification email: {e}")

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

