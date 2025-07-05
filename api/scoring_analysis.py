"""
AI Assessment Scoring Analysis
Maps current assessment questions to the four service areas and creates scoring logic
"""

# Four Service Areas from Market Research
SERVICE_AREAS = {
    'marketing_sales': 'Marketing & Sales AI Solutions',
    'customer_service': 'Customer Service Automation', 
    'business_process': 'Business Process Automation',
    'data_analytics': 'Data Analytics & Business Intelligence'
}

# Current Assessment Questions Analysis
ASSESSMENT_QUESTIONS = {
    'name': {
        'type': 'text',
        'scoring': None,  # No scoring impact
        'purpose': 'identification'
    },
    'email': {
        'type': 'email', 
        'scoring': None,  # No scoring impact
        'purpose': 'identification'
    },
    'phone': {
        'type': 'tel',
        'scoring': None,  # No scoring impact  
        'purpose': 'identification'
    },
    'company': {
        'type': 'text',
        'scoring': None,  # No scoring impact
        'purpose': 'identification'
    },
    'employees': {
        'type': 'radio',
        'options': ['1-10', '11-50', '51-200', '200+'],
        'scoring': {
            # Larger companies have more complex needs across all areas
            '1-10': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 5, 'data_analytics': 5},
            '11-50': {'marketing_sales': 10, 'customer_service': 10, 'business_process': 10, 'data_analytics': 10},
            '51-200': {'marketing_sales': 15, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            '200+': {'marketing_sales': 20, 'customer_service': 20, 'business_process': 20, 'data_analytics': 20}
        },
        'rationale': 'Company size indicates complexity of needs and resources available for AI implementation'
    },
    'industry': {
        'type': 'select',
        'options': ['technology', 'healthcare', 'finance', 'retail', 'manufacturing', 'education', 'professional-services', 'other'],
        'scoring': {
            # Different industries have different AI readiness and needs
            'technology': {'marketing_sales': 15, 'customer_service': 15, 'business_process': 10, 'data_analytics': 20},
            'healthcare': {'marketing_sales': 5, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            'finance': {'marketing_sales': 10, 'customer_service': 10, 'business_process': 20, 'data_analytics': 20},
            'retail': {'marketing_sales': 20, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            'manufacturing': {'marketing_sales': 5, 'customer_service': 10, 'business_process': 20, 'data_analytics': 15},
            'education': {'marketing_sales': 10, 'customer_service': 15, 'business_process': 15, 'data_analytics': 10},
            'professional-services': {'marketing_sales': 15, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            'other': {'marketing_sales': 10, 'customer_service': 10, 'business_process': 10, 'data_analytics': 10}
        },
        'rationale': 'Industry determines specific AI use cases and readiness levels'
    },
    'current_tools': {
        'type': 'checkbox',
        'options': ['crm', 'analytics', 'automation', 'cloud', 'social-media', 'email-marketing', 'none'],
        'scoring': {
            # Each tool indicates readiness for specific service areas
            'crm': {'marketing_sales': 10, 'customer_service': 10, 'business_process': 5, 'data_analytics': 5},
            'analytics': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 5, 'data_analytics': 15},
            'automation': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 15, 'data_analytics': 5},
            'cloud': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 10, 'data_analytics': 10},
            'social-media': {'marketing_sales': 10, 'customer_service': 5, 'business_process': 0, 'data_analytics': 5},
            'email-marketing': {'marketing_sales': 10, 'customer_service': 5, 'business_process': 5, 'data_analytics': 5},
            'none': {'marketing_sales': 0, 'customer_service': 0, 'business_process': 0, 'data_analytics': 0}
        },
        'rationale': 'Current technology adoption indicates readiness for AI implementation'
    },
    'budget': {
        'type': 'radio',
        'options': ['under-1k', '1k-5k', '5k-10k', '10k-25k', '25k+'],
        'scoring': {
            # Budget determines scope of AI implementation possible
            'under-1k': {'marketing_sales': 5, 'customer_service': 10, 'business_process': 5, 'data_analytics': 5},
            '1k-5k': {'marketing_sales': 10, 'customer_service': 15, 'business_process': 10, 'data_analytics': 10},
            '5k-10k': {'marketing_sales': 15, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            '10k-25k': {'marketing_sales': 20, 'customer_service': 20, 'business_process': 20, 'data_analytics': 20},
            '25k+': {'marketing_sales': 25, 'customer_service': 25, 'business_process': 25, 'data_analytics': 25}
        },
        'rationale': 'Budget determines what AI solutions are feasible to implement'
    },
    'timeline': {
        'type': 'radio',
        'options': ['immediately', '1-3-months', '3-6-months', '6-12-months', 'exploring'],
        'scoring': {
            # Timeline indicates urgency and readiness to implement
            'immediately': {'marketing_sales': 15, 'customer_service': 15, 'business_process': 15, 'data_analytics': 15},
            '1-3-months': {'marketing_sales': 12, 'customer_service': 12, 'business_process': 12, 'data_analytics': 12},
            '3-6-months': {'marketing_sales': 8, 'customer_service': 8, 'business_process': 8, 'data_analytics': 8},
            '6-12-months': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 5, 'data_analytics': 5},
            'exploring': {'marketing_sales': 2, 'customer_service': 2, 'business_process': 2, 'data_analytics': 2}
        },
        'rationale': 'Implementation timeline indicates commitment level and urgency'
    },
    'goals': {
        'type': 'checkbox',
        'options': ['efficiency', 'cost-reduction', 'customer-experience', 'data-insights', 'competitive-advantage', 'automation'],
        'scoring': {
            # Goals map directly to service areas
            'efficiency': {'marketing_sales': 5, 'customer_service': 5, 'business_process': 15, 'data_analytics': 5},
            'cost-reduction': {'marketing_sales': 5, 'customer_service': 10, 'business_process': 15, 'data_analytics': 5},
            'customer-experience': {'marketing_sales': 15, 'customer_service': 20, 'business_process': 5, 'data_analytics': 5},
            'data-insights': {'marketing_sales': 10, 'customer_service': 5, 'business_process': 5, 'data_analytics': 20},
            'competitive-advantage': {'marketing_sales': 15, 'customer_service': 10, 'business_process': 10, 'data_analytics': 15},
            'automation': {'marketing_sales': 10, 'customer_service': 15, 'business_process': 20, 'data_analytics': 5}
        },
        'rationale': 'Business goals directly indicate which service areas are most relevant'
    }
}

# Score Ranges and Recommendations for Each Service Area
SCORE_RANGES = {
    'marketing_sales': {
        'ranges': [
            {'min': 0, 'max': 25, 'level': 'Basic', 'priority': 'Low'},
            {'min': 26, 'max': 50, 'level': 'Developing', 'priority': 'Medium'},
            {'min': 51, 'max': 75, 'level': 'Advanced', 'priority': 'High'},
            {'min': 76, 'max': 100, 'level': 'Expert', 'priority': 'Very High'}
        ],
        'recommendations': {
            'Basic': [
                'Start with basic email marketing automation',
                'Implement simple lead capture forms',
                'Set up basic customer segmentation',
                'Consider entry-level CRM with AI features'
            ],
            'Developing': [
                'Implement marketing automation workflows',
                'Add AI-powered lead scoring',
                'Create personalized email campaigns',
                'Integrate social media automation'
            ],
            'Advanced': [
                'Deploy predictive lead scoring',
                'Implement advanced customer segmentation',
                'Add AI-powered content personalization',
                'Create omnichannel marketing campaigns'
            ],
            'Expert': [
                'Implement advanced predictive analytics',
                'Deploy AI-powered customer journey optimization',
                'Add real-time personalization engines',
                'Create custom AI marketing solutions'
            ]
        }
    },
    'customer_service': {
        'ranges': [
            {'min': 0, 'max': 25, 'level': 'Basic', 'priority': 'Low'},
            {'min': 26, 'max': 50, 'level': 'Developing', 'priority': 'Medium'},
            {'min': 51, 'max': 75, 'level': 'Advanced', 'priority': 'High'},
            {'min': 76, 'max': 100, 'level': 'Expert', 'priority': 'Very High'}
        ],
        'recommendations': {
            'Basic': [
                'Implement basic FAQ chatbot',
                'Set up automated email responses',
                'Create simple ticket routing system',
                'Add basic customer feedback collection'
            ],
            'Developing': [
                'Deploy intelligent chatbot with NLP',
                'Implement automated ticket prioritization',
                'Add sentiment analysis for customer communications',
                'Create self-service knowledge base'
            ],
            'Advanced': [
                'Deploy advanced conversational AI',
                'Implement predictive customer support',
                'Add voice assistant integration',
                'Create proactive customer outreach'
            ],
            'Expert': [
                'Implement AI-powered customer success prediction',
                'Deploy advanced voice and video AI support',
                'Add real-time emotion detection',
                'Create fully autonomous customer service agents'
            ]
        }
    },
    'business_process': {
        'ranges': [
            {'min': 0, 'max': 25, 'level': 'Basic', 'priority': 'Low'},
            {'min': 26, 'max': 50, 'level': 'Developing', 'priority': 'Medium'},
            {'min': 51, 'max': 75, 'level': 'Advanced', 'priority': 'High'},
            {'min': 76, 'max': 100, 'level': 'Expert', 'priority': 'Very High'}
        ],
        'recommendations': {
            'Basic': [
                'Automate simple repetitive tasks',
                'Implement basic document management',
                'Set up automated invoicing',
                'Create simple workflow automation'
            ],
            'Developing': [
                'Deploy robotic process automation (RPA)',
                'Implement intelligent document processing',
                'Add automated approval workflows',
                'Create inventory management automation'
            ],
            'Advanced': [
                'Implement AI-powered process optimization',
                'Deploy predictive maintenance systems',
                'Add intelligent resource allocation',
                'Create end-to-end process automation'
            ],
            'Expert': [
                'Deploy autonomous business processes',
                'Implement AI-driven decision making',
                'Add self-optimizing workflows',
                'Create intelligent business orchestration'
            ]
        }
    },
    'data_analytics': {
        'ranges': [
            {'min': 0, 'max': 25, 'level': 'Basic', 'priority': 'Low'},
            {'min': 26, 'max': 50, 'level': 'Developing', 'priority': 'Medium'},
            {'min': 51, 'max': 75, 'level': 'Advanced', 'priority': 'High'},
            {'min': 76, 'max': 100, 'level': 'Expert', 'priority': 'Very High'}
        ],
        'recommendations': {
            'Basic': [
                'Set up basic analytics dashboards',
                'Implement simple reporting automation',
                'Create basic customer analytics',
                'Add performance tracking metrics'
            ],
            'Developing': [
                'Deploy predictive analytics models',
                'Implement customer behavior analysis',
                'Add business intelligence dashboards',
                'Create automated insights generation'
            ],
            'Advanced': [
                'Implement machine learning models',
                'Deploy real-time analytics systems',
                'Add advanced forecasting capabilities',
                'Create custom analytics solutions'
            ],
            'Expert': [
                'Deploy advanced AI/ML platforms',
                'Implement autonomous analytics systems',
                'Add real-time decision engines',
                'Create self-learning analytics models'
            ]
        }
    }
}

def calculate_service_area_scores(form_data):
    """
    Calculate scores for each of the four service areas based on form responses
    """
    scores = {
        'marketing_sales': 0,
        'customer_service': 0, 
        'business_process': 0,
        'data_analytics': 0
    }
    
    # Process each question
    for question, config in ASSESSMENT_QUESTIONS.items():
        if config['scoring'] is None:
            continue
            
        value = form_data.get(question)
        if not value:
            continue
            
        if config['type'] == 'checkbox':
            # Handle multiple selections
            if isinstance(value, list):
                for item in value:
                    if item in config['scoring']:
                        for area, points in config['scoring'][item].items():
                            scores[area] += points
        else:
            # Handle single selections
            if value in config['scoring']:
                for area, points in config['scoring'][value].items():
                    scores[area] += points
    
    # Normalize scores to 0-100 range
    max_possible_scores = {
        'marketing_sales': 140,  # Calculated based on maximum possible points
        'customer_service': 140,
        'business_process': 140, 
        'data_analytics': 140
    }
    
    normalized_scores = {}
    for area, score in scores.items():
        normalized_scores[area] = min(100, int((score / max_possible_scores[area]) * 100))
    
    return normalized_scores

def get_recommendations_for_scores(scores):
    """
    Get personalized recommendations based on scores for each service area
    """
    recommendations = {}
    
    for area, score in scores.items():
        area_config = SCORE_RANGES[area]
        
        # Find the appropriate range
        level = 'Basic'
        priority = 'Low'
        for range_config in area_config['ranges']:
            if range_config['min'] <= score <= range_config['max']:
                level = range_config['level']
                priority = range_config['priority']
                break
        
        recommendations[area] = {
            'score': score,
            'level': level,
            'priority': priority,
            'recommendations': area_config['recommendations'][level],
            'area_name': SERVICE_AREAS[area]
        }
    
    return recommendations

