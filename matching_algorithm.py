import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from text_processor import extract_soft_skills, process_text

# Download necessary NLTK data if not already downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')

def calculate_match_score(employee, role, include_soft_skills=True):
    """
    Calculate match score between an employee and a role
    
    Parameters:
    - employee: Employee data (DataFrame row or dict)
    - role: Role data (DataFrame row or dict)
    - include_soft_skills: Whether to include soft skills analysis (default: True)
    
    Returns:
    - Dictionary with overall and component scores
    """
    # Initialize scores dictionary
    scores = {
        'overall': 0,
        'skill_match': 0,
        'experience_match': 0,
        'certification_match': 0,
        'education_match': 0,
        'soft_skills': 0,
        'details': {}
    }
    
    # Convert pandas Series to dict if needed
    if hasattr(employee, 'to_dict'):
        employee = employee.to_dict()
    if hasattr(role, 'to_dict'):
        role = role.to_dict()
    
    # 1. Skill Matching (40% of total score)
    skill_score = calculate_skill_match(employee, role)
    scores['skill_match'] = skill_score
    
    # 2. Experience Matching (25% of total score)
    experience_score = calculate_experience_match(employee, role)
    scores['experience_match'] = experience_score
    
    # 3. Certification Matching (15% of total score)
    certification_score = calculate_certification_match(employee, role)
    scores['certification_match'] = certification_score
    
    # 4. Education Matching (10% of total score)
    education_score = calculate_education_match(employee, role)
    scores['education_match'] = education_score
    
    # 5. Soft Skills Analysis (10% of total score) if requested
    if include_soft_skills:
        soft_skills_score = calculate_soft_skills_score(employee)
        scores['soft_skills'] = soft_skills_score
    else:
        soft_skills_score = 0
        scores['soft_skills'] = 0
    
    # Calculate overall score with appropriate weights
    if include_soft_skills:
        scores['overall'] = (
            0.40 * skill_score +
            0.25 * experience_score +
            0.15 * certification_score +
            0.10 * education_score +
            0.10 * soft_skills_score
        )
    else:
        # Redistribute weights if soft skills are excluded
        scores['overall'] = (
            0.45 * skill_score +
            0.30 * experience_score +
            0.15 * certification_score +
            0.10 * education_score
        )
    
    # Add skill gap analysis
    scores['details']['skill_gaps'] = identify_skill_gaps(employee, role)
    
    return scores

def calculate_skill_match(employee, role):
    """Calculate a skill match score between employee skills and role requirements"""
    employee_skills = employee.get('skills', [])
    required_skills = role.get('required_skills', [])
    preferred_skills = role.get('preferred_skills', [])
    
    # Ensure we're working with lists
    if not isinstance(employee_skills, list):
        employee_skills = [] if pd.isna(employee_skills) else [employee_skills]
    if not isinstance(required_skills, list):
        required_skills = [] if pd.isna(required_skills) else [required_skills]
    if not isinstance(preferred_skills, list):
        preferred_skills = [] if pd.isna(preferred_skills) else [preferred_skills]
    
    # Edge case handling
    if not required_skills and not preferred_skills:
        return 0  # No skills to match against
    
    # Count matched required skills (these are weighted more heavily)
    required_matched = sum(1 for skill in required_skills if skill in employee_skills)
    required_ratio = required_matched / len(required_skills) if required_skills else 1
    
    # Count matched preferred skills (weighted less heavily)
    preferred_matched = sum(1 for skill in preferred_skills if skill in employee_skills)
    preferred_ratio = preferred_matched / len(preferred_skills) if preferred_skills else 1
    
    # Calculate weighted skill score (required skills are more important)
    if required_skills and preferred_skills:
        skill_score = (0.7 * required_ratio) + (0.3 * preferred_ratio)
    elif required_skills:
        skill_score = required_ratio
    else:  # Only preferred skills exist
        skill_score = preferred_ratio
    
    return skill_score

def calculate_experience_match(employee, role):
    """Calculate an experience match score between employee and role requirements"""
    # Get employee experience (years)
    employee_experience = employee.get('experience', 0)
    if isinstance(employee_experience, list):
        # If experience is a list of positions, calculate total years
        total_years = 0
        for exp in employee_experience:
            if isinstance(exp, dict) and 'years' in exp:
                total_years += exp['years']
        employee_experience = total_years
    
    # Handle different data types
    if isinstance(employee_experience, str):
        try:
            employee_experience = float(employee_experience)
        except ValueError:
            employee_experience = 0
    
    # Get required experience for the role
    required_experience = role.get('required_experience', 0)
    if isinstance(required_experience, str):
        try:
            required_experience = float(required_experience)
        except ValueError:
            required_experience = 0
    
    # Calculate experience match score
    if required_experience <= 0:  # No experience required
        return 1.0
    
    if employee_experience >= required_experience:
        # Full match if employee meets or exceeds requirements
        return 1.0
    else:
        # Partial match based on proportion
        return employee_experience / required_experience

def calculate_certification_match(employee, role):
    """Calculate a certification match score between employee and role requirements"""
    employee_certs = employee.get('certifications', [])
    required_certs = role.get('required_certifications', [])
    
    # Ensure we're working with lists
    if not isinstance(employee_certs, list):
        employee_certs = [] if pd.isna(employee_certs) else [employee_certs]
    if not isinstance(required_certs, list):
        required_certs = [] if pd.isna(required_certs) else [required_certs]
    
    # Edge case handling
    if not required_certs:
        return 1.0  # No certifications required
    
    # Count matched certifications
    matched = sum(1 for cert in required_certs if cert in employee_certs)
    
    # Calculate match ratio
    return matched / len(required_certs) if required_certs else 1.0

def calculate_education_match(employee, role):
    """Calculate an education match score between employee and role requirements"""
    employee_education = employee.get('education', '')
    required_education = role.get('required_education', '')
    
    # If either is missing, return partial score
    if not employee_education or not required_education:
        return 0.5
    
    # Education levels for scoring
    education_levels = {
        'high school': 1,
        'associate': 2,
        'bachelor': 3,
        'master': 4,
        'phd': 5,
        'doctorate': 5
    }
    
    # Determine employee education level
    employee_level = 0
    for level, score in education_levels.items():
        if level in str(employee_education).lower():
            employee_level = max(employee_level, score)
    
    # Determine required education level
    required_level = 0
    for level, score in education_levels.items():
        if level in str(required_education).lower():
            required_level = max(required_level, score)
    
    # Calculate match score
    if employee_level >= required_level:
        return 1.0  # Full match if employee meets or exceeds requirements
    else:
        # Partial match based on proportion
        return employee_level / required_level if required_level > 0 else 0.5

def calculate_soft_skills_score(employee):
    """Calculate a soft skills score based on peer reviews and performance data"""
    peer_reviews = employee.get('peer_reviews', '')
    
    # If no peer reviews are available, return a neutral score
    if not peer_reviews:
        return 0.5
    
    # Extract soft skills from peer reviews
    soft_skills = extract_soft_skills(peer_reviews)
    
    # Perform sentiment analysis on peer reviews
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(peer_reviews)
    
    # Calculate soft skills score based on sentiment and number of identified skills
    sentiment_component = (sentiment_scores['compound'] + 1) / 2  # Convert to 0-1 scale
    skills_component = min(1.0, len(soft_skills) / 5)  # Cap at 1.0
    
    # Combine components (sentiment is weighted more heavily)
    soft_skills_score = (0.7 * sentiment_component) + (0.3 * skills_component)
    
    return soft_skills_score

def identify_skill_gaps(employee, role):
    """Identify skills required by the role that the employee is missing"""
    employee_skills = employee.get('skills', [])
    required_skills = role.get('required_skills', [])
    preferred_skills = role.get('preferred_skills', [])
    
    # Ensure we're working with lists
    if not isinstance(employee_skills, list):
        employee_skills = [] if pd.isna(employee_skills) else [employee_skills]
    if not isinstance(required_skills, list):
        required_skills = [] if pd.isna(required_skills) else [required_skills]
    if not isinstance(preferred_skills, list):
        preferred_skills = [] if pd.isna(preferred_skills) else [preferred_skills]
    
    # Find missing required and preferred skills
    missing_required = [skill for skill in required_skills if skill not in employee_skills]
    missing_preferred = [skill for skill in preferred_skills if skill not in employee_skills]
    
    return {
        'missing_required': missing_required,
        'missing_preferred': missing_preferred
    }

def match_employees_to_roles(employees=None, roles=None, top_n=5):
    """
    Match all employees to all roles, or the provided subset
    
    Parameters:
    - employees: DataFrame of employees (default: all employees in session state)
    - roles: DataFrame of roles (default: all roles in session state)
    - top_n: Number of top matches to return for each employee/role
    
    Returns:
    - Dictionary with top employee matches for each role and top role matches for each employee
    """
    if employees is None:
        employees = st.session_state.employees
    
    if roles is None:
        roles = st.session_state.roles
    
    # Initialize results dictionary
    results = {
        'employee_to_role': {},  # For each employee, their top role matches
        'role_to_employee': {},  # For each role, their top employee matches
        'all_matches': []        # All employee-role match pairs with scores
    }
    
    # Calculate all matches
    all_matches = []
    
    for _, employee in employees.iterrows():
        employee_id = employee['employee_id']
        employee_matches = []
        
        for _, role in roles.iterrows():
            role_id = role['role_id']
            
            # Calculate match score
            match_scores = calculate_match_score(employee, role)
            
            # Create match record
            match = {
                'employee_id': employee_id,
                'employee_name': employee['name'],
                'role_id': role_id,
                'role_title': role['title'],
                'overall_score': match_scores['overall'],
                'skill_match': match_scores['skill_match'],
                'experience_match': match_scores['experience_match'],
                'certification_match': match_scores['certification_match'],
                'education_match': match_scores['education_match'],
                'soft_skills': match_scores['soft_skills'],
                'skill_gaps': match_scores['details']['skill_gaps']
            }
            
            employee_matches.append(match)
            all_matches.append(match)
        
        # Sort employee matches by overall score
        employee_matches = sorted(employee_matches, key=lambda x: x['overall_score'], reverse=True)
        
        # Store top N matches for this employee
        results['employee_to_role'][employee_id] = employee_matches[:top_n]
    
    # For each role, find the top N employee matches
    for _, role in roles.iterrows():
        role_id = role['role_id']
        
        # Get all matches for this role
        role_matches = [match for match in all_matches if match['role_id'] == role_id]
        
        # Sort by overall score
        role_matches = sorted(role_matches, key=lambda x: x['overall_score'], reverse=True)
        
        # Store top N matches for this role
        results['role_to_employee'][role_id] = role_matches[:top_n]
    
    # Store all matches
    results['all_matches'] = sorted(all_matches, key=lambda x: x['overall_score'], reverse=True)
    
    return results
