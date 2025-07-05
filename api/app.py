from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import our scoring and report generation functions
from api.scoring_analysis import calculate_service_area_scores, get_recommendations_for_scores, SERVICE_AREAS
from api.report_generator import generate_personalized_report

def calculate_ai_readiness_score_legacy(data):
    """
    Legacy scoring function for backward compatibility
    """
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

def send_notification_email(assessment_data, score, service_area_scores=None):
    """Send email notification about new assessment submission"""
    try:
        # Email configuration (you'll need to set these environment variables)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        email_user = os.environ.get('EMAIL_USER')
        email_password = os.environ.get('EMAIL_PASSWORD')
        recipient_email = os.environ.get('RECIPIENT_EMAIL')
        
        if not all([email_user, email_password, recipient_email]):
            print("Email configuration missing")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = f"New AI Assessment Submission - Overall Score: {score}%"
        
        # Enhanced email body with service area scores
        service_area_info = ""
        if service_area_scores:
            service_area_info = f"""
        
        Service Area Breakdown:
        • Marketing & Sales AI: {service_area_scores.get('marketing_sales', 0)}%
        • Customer Service Automation: {service_area_scores.get('customer_service', 0)}%
        • Business Process Automation: {service_area_scores.get('business_process', 0)}%
        • Data Analytics & BI: {service_area_scores.get('data_analytics', 0)}%
        """
        
        body = f"""
        New AI Assessment Submission
        
        Contact Information:
        Name: {assessment_data.get('name', 'Not provided')}
        Email: {assessment_data.get('email', 'Not provided')}
        Phone: {assessment_data.get('phone', 'Not provided')}
        Company: {assessment_data.get('company', 'Not provided')}
        
        Assessment Details:
        Overall AI Readiness Score: {score}%
        Company Size: {assessment_data.get('employees', 'Not provided')}
        Industry: {assessment_data.get('industry', 'Not provided')}
        Current Tools: {', '.join(assessment_data.get('current_tools', []))}
        Budget: {assessment_data.get('budget', 'Not provided')}
        Timeline: {assessment_data.get('timeline', 'Not provided')}
        Goals: {', '.join(assessment_data.get('goals', []))}
        {service_area_info}
        
        Additional Info: {assessment_data.get('additional_info', 'None provided')}
        
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
        
        # Calculate enhanced AI readiness scores
        service_area_scores = calculate_service_area_scores(data)
        recommendations = get_recommendations_for_scores(service_area_scores)
        
        # Calculate overall score (weighted average)
        weights = {
            'marketing_sales': 0.25,
            'customer_service': 0.25,
            'business_process': 0.30,
            'data_analytics': 0.20
        }
        overall_score = int(sum(score * weights[area] for area, score in service_area_scores.items()))
        
        # Add timestamp and scores to data
        data['submitted_at'] = datetime.now().isoformat()
        data['overall_score'] = overall_score
        data['service_area_scores'] = service_area_scores
        data['recommendations'] = recommendations
        
        # Generate personalized report HTML
        report_html, report_data = generate_personalized_report(data)
        
        # Send notification email with enhanced information
        email_sent = send_notification_email(data, overall_score, service_area_scores)
        
        # Store data (you might want to add database storage here)
        print(f"Enhanced Assessment submitted: {data['name']} - Overall Score: {overall_score}%")
        print(f"Service Area Scores: {service_area_scores}")
        
        # Return success response with report URL
        return jsonify({
            'success': True,
            'overall_score': overall_score,
            'service_area_scores': service_area_scores,
            'recommendations': recommendations,
            'report_url': f'/api/report/{data["email"].replace("@", "_at_").replace(".", "_dot_")}',
            'message': 'Assessment submitted successfully',
            'email_sent': email_sent
        })
        
    except Exception as e:
        print(f"Error processing assessment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/report/<email_identifier>')
def get_report(email_identifier):
    """
    Serve personalized report for a specific user
    Note: In production, you'd want to implement proper authentication/security
    """
    try:
        # For demo purposes, we'll generate a sample report
        # In production, you'd retrieve the actual assessment data from a database
        
        sample_data = {
            'name': 'Sample User',
            'email': email_identifier.replace('_at_', '@').replace('_dot_', '.'),
            'company': 'Sample Company',
            'employees': '11-50',
            'industry': 'retail',
            'current_tools': ['crm', 'analytics'],
            'budget': '5k-10k',
            'timeline': '1-3-months',
            'goals': ['customer-experience', 'automation']
        }
        
        report_html, report_data = generate_personalized_report(sample_data)
        
        return report_html, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Report generation failed'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Extra Mile AI Assessment API',
        'version': '2.0.0',
        'endpoints': {
            'submit_assessment': '/api/submit-assessment',
            'get_report': '/api/report/<email_identifier>',
            'health_check': '/api/health'
        }
    })

# For Vercel serverless functions
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

