"""
AI Assessment Report Generator
Generates personalized HTML reports based on assessment scores and recommendations
"""

from datetime import datetime
from api.scoring_analysis import calculate_service_area_scores, get_recommendations_for_scores, SERVICE_AREAS

def generate_overall_score(service_area_scores):
    """
    Calculate overall AI readiness score as weighted average of service areas
    """
    # Weight the service areas based on typical business importance
    weights = {
        'marketing_sales': 0.25,
        'customer_service': 0.25,
        'business_process': 0.30,  # Slightly higher weight for process automation
        'data_analytics': 0.20
    }
    
    weighted_score = sum(score * weights[area] for area, score in service_area_scores.items())
    return int(weighted_score)

def get_overall_description(overall_score):
    """
    Get description based on overall AI readiness score
    """
    if overall_score >= 80:
        return "Excellent! Your business is highly ready for AI implementation across multiple areas."
    elif overall_score >= 60:
        return "Great! You have a solid foundation for AI adoption with strong potential in key areas."
    elif overall_score >= 40:
        return "Good potential! Some preparation needed, but you're well-positioned to benefit from AI."
    else:
        return "Perfect starting point! AI can provide significant value as you build your digital foundation."

def get_priority_class(priority):
    """
    Convert priority text to CSS class
    """
    priority_map = {
        'Very High': 'very-high-priority',
        'High': 'high-priority',
        'Medium': 'medium-priority',
        'Low': 'low-priority'
    }
    return priority_map.get(priority, 'low-priority')

def format_recommendations_html(recommendations_list):
    """
    Convert recommendations list to HTML list items
    """
    return '\n'.join([f'<li>{rec}</li>' for rec in recommendations_list])

def create_priority_matrix(recommendations):
    """
    Create priority matrix HTML based on service area priorities
    """
    # Sort areas by priority and score
    priority_order = ['Very High', 'High', 'Medium', 'Low']
    sorted_areas = []
    
    for priority in priority_order:
        for area, rec in recommendations.items():
            if rec['priority'] == priority:
                sorted_areas.append((area, rec))
    
    matrix_html = ""
    for i, (area, rec) in enumerate(sorted_areas[:4]):  # Top 4 priorities
        priority_num = i + 1
        area_name = SERVICE_AREAS[area]
        matrix_html += f'''
        <div class="priority-item priority-{priority_num}">
            <div>Priority {priority_num}</div>
            <div style="font-size: 0.9rem; margin-top: 5px;">{area_name}</div>
            <div style="font-size: 0.8rem; margin-top: 3px;">{rec['score']}% - {rec['level']}</div>
        </div>
        '''
    
    return matrix_html

def get_top_priority_area(recommendations):
    """
    Get the name of the top priority service area
    """
    priority_order = ['Very High', 'High', 'Medium', 'Low']
    
    for priority in priority_order:
        for area, rec in recommendations.items():
            if rec['priority'] == priority:
                return SERVICE_AREAS[area]
    
    return "Business Process Automation"  # Default fallback

def generate_personalized_report(form_data):
    """
    Generate a complete personalized report based on form data
    """
    # Calculate scores and recommendations
    service_area_scores = calculate_service_area_scores(form_data)
    recommendations = get_recommendations_for_scores(service_area_scores)
    overall_score = generate_overall_score(service_area_scores)
    
    # Read the HTML template
    with open('api/report.html', 'r') as f:
        template = f.read()
    
    # Prepare template variables
    template_vars = {
        # Company information
        'company_name': form_data.get('company', 'Your Company'),
        'contact_name': form_data.get('name', 'Contact Name'),
        'industry': form_data.get('industry', 'Not specified').title(),
        'company_size': form_data.get('employees', 'Not specified'),
        'assessment_date': datetime.now().strftime('%B %d, %Y'),
        
        # Overall score
        'overall_score': overall_score,
        'overall_description': get_overall_description(overall_score),
        
        # Marketing & Sales AI
        'marketing_score': recommendations['marketing_sales']['score'],
        'marketing_level': recommendations['marketing_sales']['level'],
        'marketing_priority': recommendations['marketing_sales']['priority'],
        'marketing_priority_class': get_priority_class(recommendations['marketing_sales']['priority']),
        'marketing_recommendations': format_recommendations_html(recommendations['marketing_sales']['recommendations']),
        
        # Customer Service Automation
        'customer_service_score': recommendations['customer_service']['score'],
        'customer_service_level': recommendations['customer_service']['level'],
        'customer_service_priority': recommendations['customer_service']['priority'],
        'customer_service_priority_class': get_priority_class(recommendations['customer_service']['priority']),
        'customer_service_recommendations': format_recommendations_html(recommendations['customer_service']['recommendations']),
        
        # Business Process Automation
        'business_process_score': recommendations['business_process']['score'],
        'business_process_level': recommendations['business_process']['level'],
        'business_process_priority': recommendations['business_process']['priority'],
        'business_process_priority_class': get_priority_class(recommendations['business_process']['priority']),
        'business_process_recommendations': format_recommendations_html(recommendations['business_process']['recommendations']),
        
        # Data Analytics & Business Intelligence
        'data_analytics_score': recommendations['data_analytics']['score'],
        'data_analytics_level': recommendations['data_analytics']['level'],
        'data_analytics_priority': recommendations['data_analytics']['priority'],
        'data_analytics_priority_class': get_priority_class(recommendations['data_analytics']['priority']),
        'data_analytics_recommendations': format_recommendations_html(recommendations['data_analytics']['recommendations']),
        
        # Priority matrix and roadmap
        'priority_matrix': create_priority_matrix(recommendations),
        'top_priority_area': get_top_priority_area(recommendations)
    }
    
    # Replace template variables
    for key, value in template_vars.items():
        template = template.replace('{{' + key + '}}', str(value))
    
    return template, {
        'service_area_scores': service_area_scores,
        'recommendations': recommendations,
        'overall_score': overall_score,
        'template_vars': template_vars
    }

