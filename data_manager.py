import streamlit as st
import pandas as pd
import uuid
import datetime
import os
import json
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import text
import numpy as np
import psycopg2

# Get the database connection string from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Provide a default SQLite connection for local development
    DATABASE_URL = "sqlite:///chevron_skills.db"

# Create database engine and session
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define database models
class Employee(Base):
    __tablename__ = 'employees'
    
    employee_id = Column(String, primary_key=True)
    name = Column(String)
    department = Column(String)
    job_title = Column(String)
    joining_date = Column(DateTime)
    skills = Column(Text)  # Store as JSON string
    certifications = Column(Text)  # Store as JSON string
    experience = Column(Float)
    education = Column(String)
    projects = Column(Text)  # Store as JSON string
    performance_scores = Column(Text)  # Store as JSON string
    peer_reviews = Column(Text)
    last_updated = Column(DateTime)

class Role(Base):
    __tablename__ = 'roles'
    
    role_id = Column(String, primary_key=True)
    title = Column(String)
    department = Column(String)
    description = Column(Text)
    required_skills = Column(Text)  # Store as JSON string
    preferred_skills = Column(Text)  # Store as JSON string
    required_certifications = Column(Text)  # Store as JSON string
    required_experience = Column(Float)
    required_education = Column(String)
    responsibilities = Column(Text)  # Store as JSON string
    last_updated = Column(DateTime)

class Match(Base):
    __tablename__ = 'matches'
    
    match_id = Column(String, primary_key=True)
    employee_id = Column(String)
    role_id = Column(String)
    match_score = Column(Float)
    skill_match_score = Column(Float)
    experience_match_score = Column(Float)
    certification_match_score = Column(Float)
    education_match_score = Column(Float)
    soft_skills_score = Column(Float)
    match_date = Column(DateTime)
    notes = Column(Text)

class Skill(Base):
    __tablename__ = 'skills'
    
    skill_id = Column(Integer, primary_key=True)
    skill_name = Column(String, unique=True)

class Department(Base):
    __tablename__ = 'departments'
    
    department_id = Column(Integer, primary_key=True)
    department_name = Column(String, unique=True)

class Certification(Base):
    __tablename__ = 'certifications'
    
    certification_id = Column(Integer, primary_key=True)
    certification_name = Column(String, unique=True)

def initialize_data():
    """Initialize database tables and load initial data into session state"""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(engine, checkfirst=True)
        
        # Initialize empty DataFrames and sets in session state if they don't exist
        if 'employees' not in st.session_state:
            st.session_state.employees = pd.DataFrame()
        
        if 'roles' not in st.session_state:
            st.session_state.roles = pd.DataFrame()
        
        if 'matches' not in st.session_state:
            st.session_state.matches = pd.DataFrame()
        
        if 'skills' not in st.session_state:
            st.session_state.skills = set()
        
        if 'departments' not in st.session_state:
            st.session_state.departments = set()
        
        if 'certifications' not in st.session_state:
            st.session_state.certifications = set()
        
        # Load data from database into session state for convenience
        employees_df = get_all_employees()
        if not employees_df.empty:
            st.session_state.employees = employees_df
        
        roles_df = get_all_roles()
        if not roles_df.empty:
            st.session_state.roles = roles_df
        
        matches_df = get_all_matches()
        if not matches_df.empty:
            st.session_state.matches = matches_df
        
        # Load master data lists
        skills = get_all_skills()
        if skills:
            st.session_state.skills.update(skills)
        
        departments = get_all_departments()
        if not departments:
            # Add default departments if none exist
            default_departments = ['Engineering', 'Human Resources', 'Finance', 
                                  'Operations', 'Research & Development', 
                                  'Information Technology', 'Marketing', 'Legal']
            for dept in default_departments:
                add_department(dept)
            st.session_state.departments.update(default_departments)
        else:
            st.session_state.departments.update(departments)
        
        certs = get_all_certifications()
        if certs:
            st.session_state.certifications.update(certs)
            
    except Exception as e:
        st.error(f"Error initializing data: {e}")
        # Ensure we at least have empty session state variables
        if 'employees' not in st.session_state:
            st.session_state.employees = pd.DataFrame()
        if 'roles' not in st.session_state:
            st.session_state.roles = pd.DataFrame()
        if 'matches' not in st.session_state:
            st.session_state.matches = pd.DataFrame()
        if 'skills' not in st.session_state:
            st.session_state.skills = set()
        if 'departments' not in st.session_state:
            st.session_state.departments = set()
        if 'certifications' not in st.session_state:
            st.session_state.certifications = set()

def add_employee(employee_data):
    """Add a new employee to the database"""
    # Generate unique ID if not provided
    if 'employee_id' not in employee_data or not employee_data['employee_id']:
        employee_data['employee_id'] = str(uuid.uuid4())
    
    # Add timestamp
    employee_data['last_updated'] = datetime.datetime.now()
    
    try:
        # Process skills
        if 'skills' in employee_data and employee_data['skills']:
            skills_list = [skill.strip() for skill in employee_data['skills']]
            st.session_state.skills.update(skills_list)
            employee_data['skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
            
            skills_json = json.dumps(skills_list)
        else:
            skills_json = '[]'
        
        # Process certifications
        if 'certifications' in employee_data and employee_data['certifications']:
            cert_list = [cert.strip() for cert in employee_data['certifications']]
            st.session_state.certifications.update(cert_list)
            employee_data['certifications'] = cert_list
            
            # Add certifications to the certifications table
            for cert in cert_list:
                add_certification(cert)
                
            certs_json = json.dumps(cert_list)
        else:
            certs_json = '[]'
        
        # Process projects
        if 'projects' in employee_data and employee_data['projects']:
            if isinstance(employee_data['projects'], list):
                projects_list = employee_data['projects']
            else:
                projects_list = [p.strip() for p in employee_data['projects'].split(',') if p.strip()]
            projects_json = json.dumps(projects_list)
        else:
            projects_json = '[]'
        
        # Process department
        if 'department' in employee_data and employee_data['department']:
            st.session_state.departments.add(employee_data['department'])
            add_department(employee_data['department'])
        
        # Add to database
        db_session = Session()
        
        # Check if employee already exists
        existing = db_session.query(Employee).filter_by(employee_id=employee_data['employee_id']).first()
        
        if existing:
            # Update existing record
            existing.name = employee_data.get('name', '')
            existing.department = employee_data.get('department', '')
            existing.job_title = employee_data.get('job_title', '')
            existing.joining_date = employee_data.get('joining_date', datetime.datetime.now())
            existing.skills = skills_json
            existing.certifications = certs_json
            existing.experience = float(employee_data.get('experience', 0))
            existing.education = employee_data.get('education', '')
            existing.projects = projects_json
            existing.peer_reviews = employee_data.get('peer_reviews', '')
            existing.last_updated = datetime.datetime.now()
        else:
            # Create new record
            employee = Employee(
                employee_id=employee_data['employee_id'],
                name=employee_data.get('name', ''),
                department=employee_data.get('department', ''),
                job_title=employee_data.get('job_title', ''),
                joining_date=employee_data.get('joining_date', datetime.datetime.now()),
                skills=skills_json,
                certifications=certs_json,
                experience=float(employee_data.get('experience', 0)),
                education=employee_data.get('education', ''),
                projects=projects_json,
                peer_reviews=employee_data.get('peer_reviews', ''),
                last_updated=datetime.datetime.now()
            )
            db_session.add(employee)
        
        db_session.commit()
        
        # Update session state
        new_employee_df = pd.DataFrame([employee_data])
        st.session_state.employees = pd.concat([st.session_state.employees, new_employee_df], ignore_index=True)
        
        db_session.close()
        
        return employee_data['employee_id']
    
    except Exception as e:
        st.error(f"Error adding employee: {e}")
        return None

def update_employee(employee_id, updated_data):
    """Update an existing employee's information"""
    try:
        # Find the employee in session state
        employee_idx = st.session_state.employees.index[st.session_state.employees['employee_id'] == employee_id].tolist()
        
        if not employee_idx:
            return False
        
        # Update timestamp
        updated_data['last_updated'] = datetime.datetime.now()
        
        # Process skills
        if 'skills' in updated_data and updated_data['skills']:
            skills_list = [skill.strip() for skill in updated_data['skills']]
            st.session_state.skills.update(skills_list)
            updated_data['skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
            
            skills_json = json.dumps(skills_list)
        else:
            skills_json = '[]'
        
        # Process certifications
        if 'certifications' in updated_data and updated_data['certifications']:
            cert_list = [cert.strip() for cert in updated_data['certifications']]
            st.session_state.certifications.update(cert_list)
            updated_data['certifications'] = cert_list
            
            # Add certifications to the certifications table
            for cert in cert_list:
                add_certification(cert)
                
            certs_json = json.dumps(cert_list)
        else:
            certs_json = '[]'
        
        # Process projects
        if 'projects' in updated_data and updated_data['projects']:
            if isinstance(updated_data['projects'], list):
                projects_list = updated_data['projects']
            else:
                projects_list = [p.strip() for p in updated_data['projects'].split(',') if p.strip()]
            projects_json = json.dumps(projects_list)
        else:
            projects_json = '[]'
        
        # Process department
        if 'department' in updated_data and updated_data['department']:
            st.session_state.departments.add(updated_data['department'])
            add_department(updated_data['department'])
        
        # Update database
        db_session = Session()
        
        # Check if employee exists in database
        employee = db_session.query(Employee).filter_by(employee_id=employee_id).first()
        
        if not employee:
            # Employee doesn't exist in database, create new
            employee = Employee(
                employee_id=employee_id,
                name=updated_data.get('name', ''),
                department=updated_data.get('department', ''),
                job_title=updated_data.get('job_title', ''),
                joining_date=updated_data.get('joining_date', datetime.datetime.now()),
                skills=skills_json,
                certifications=certs_json,
                experience=float(updated_data.get('experience', 0)),
                education=updated_data.get('education', ''),
                projects=projects_json,
                peer_reviews=updated_data.get('peer_reviews', ''),
                last_updated=datetime.datetime.now()
            )
            db_session.add(employee)
        else:
            # Update existing record
            employee.name = updated_data.get('name', employee.name)
            employee.department = updated_data.get('department', employee.department)
            employee.job_title = updated_data.get('job_title', employee.job_title)
            if 'joining_date' in updated_data:
                employee.joining_date = updated_data['joining_date']
            if 'skills' in updated_data:
                employee.skills = skills_json
            if 'certifications' in updated_data:
                employee.certifications = certs_json
            if 'experience' in updated_data:
                employee.experience = float(updated_data['experience'])
            if 'education' in updated_data:
                employee.education = updated_data['education']
            if 'projects' in updated_data:
                employee.projects = projects_json
            if 'peer_reviews' in updated_data:
                employee.peer_reviews = updated_data['peer_reviews']
            employee.last_updated = datetime.datetime.now()
        
        db_session.commit()
        db_session.close()
        
        # Update session state
        for key, value in updated_data.items():
            st.session_state.employees.at[employee_idx[0], key] = value
        
        return True
    
    except Exception as e:
        st.error(f"Error updating employee: {e}")
        return False

def delete_employee(employee_id):
    """Remove an employee from the database"""
    try:
        # Find the employee in session state
        employee_idx = st.session_state.employees.index[st.session_state.employees['employee_id'] == employee_id].tolist()
        
        if not employee_idx:
            return False
        
        # Remove from database
        db_session = Session()
        employee = db_session.query(Employee).filter_by(employee_id=employee_id).first()
        
        if employee:
            db_session.delete(employee)
            
            # Also remove any matches for this employee from database
            matches = db_session.query(Match).filter_by(employee_id=employee_id).all()
            for match in matches:
                db_session.delete(match)
            
            db_session.commit()
        
        db_session.close()
        
        # Remove from session state
        st.session_state.employees = st.session_state.employees.drop(employee_idx[0])
        
        # Also remove any matches for this employee from session state
        st.session_state.matches = st.session_state.matches[st.session_state.matches['employee_id'] != employee_id]
        
        return True
    
    except Exception as e:
        st.error(f"Error deleting employee: {e}")
        return False

def add_role(role_data):
    """Add a new role to the database"""
    # Generate unique ID if not provided
    if 'role_id' not in role_data or not role_data['role_id']:
        role_data['role_id'] = str(uuid.uuid4())
    
    # Add timestamp
    role_data['last_updated'] = datetime.datetime.now()
    
    try:
        # Process required skills
        if 'required_skills' in role_data and role_data['required_skills']:
            skills_list = [skill.strip() for skill in role_data['required_skills']]
            st.session_state.skills.update(skills_list)
            role_data['required_skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
            
            req_skills_json = json.dumps(skills_list)
        else:
            req_skills_json = '[]'
        
        # Process preferred skills
        if 'preferred_skills' in role_data and role_data['preferred_skills']:
            skills_list = [skill.strip() for skill in role_data['preferred_skills']]
            st.session_state.skills.update(skills_list)
            role_data['preferred_skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
                
            pref_skills_json = json.dumps(skills_list)
        else:
            pref_skills_json = '[]'
        
        # Process certifications
        if 'required_certifications' in role_data and role_data['required_certifications']:
            cert_list = [cert.strip() for cert in role_data['required_certifications']]
            st.session_state.certifications.update(cert_list)
            role_data['required_certifications'] = cert_list
            
            # Add certifications to the certifications table
            for cert in cert_list:
                add_certification(cert)
                
            certs_json = json.dumps(cert_list)
        else:
            certs_json = '[]'
        
        # Process responsibilities
        if 'responsibilities' in role_data and role_data['responsibilities']:
            if isinstance(role_data['responsibilities'], list):
                resp_list = role_data['responsibilities']
            else:
                resp_list = [r.strip() for r in role_data['responsibilities'].split(',') if r.strip()]
            resp_json = json.dumps(resp_list)
        else:
            resp_json = '[]'
        
        # Process department
        if 'department' in role_data and role_data['department']:
            st.session_state.departments.add(role_data['department'])
            add_department(role_data['department'])
        
        # Add to database
        db_session = Session()
        
        # Check if role already exists
        existing = db_session.query(Role).filter_by(role_id=role_data['role_id']).first()
        
        if existing:
            # Update existing record
            existing.title = role_data.get('title', '')
            existing.department = role_data.get('department', '')
            existing.description = role_data.get('description', '')
            existing.required_skills = req_skills_json
            existing.preferred_skills = pref_skills_json
            existing.required_certifications = certs_json
            existing.required_experience = float(role_data.get('required_experience', 0))
            existing.required_education = role_data.get('required_education', '')
            existing.responsibilities = resp_json
            existing.last_updated = datetime.datetime.now()
        else:
            # Create new record
            role = Role(
                role_id=role_data['role_id'],
                title=role_data.get('title', ''),
                department=role_data.get('department', ''),
                description=role_data.get('description', ''),
                required_skills=req_skills_json,
                preferred_skills=pref_skills_json,
                required_certifications=certs_json,
                required_experience=float(role_data.get('required_experience', 0)),
                required_education=role_data.get('required_education', ''),
                responsibilities=resp_json,
                last_updated=datetime.datetime.now()
            )
            db_session.add(role)
        
        db_session.commit()
        
        # Update session state
        new_role_df = pd.DataFrame([role_data])
        st.session_state.roles = pd.concat([st.session_state.roles, new_role_df], ignore_index=True)
        
        db_session.close()
        
        return role_data['role_id']
    
    except Exception as e:
        st.error(f"Error adding role: {e}")
        return None

def update_role(role_id, updated_data):
    """Update an existing role's information"""
    try:
        # Find the role in session state
        role_idx = st.session_state.roles.index[st.session_state.roles['role_id'] == role_id].tolist()
        
        if not role_idx:
            return False
        
        # Update timestamp
        updated_data['last_updated'] = datetime.datetime.now()
        
        # Process required skills
        if 'required_skills' in updated_data and updated_data['required_skills']:
            skills_list = [skill.strip() for skill in updated_data['required_skills']]
            st.session_state.skills.update(skills_list)
            updated_data['required_skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
            
            req_skills_json = json.dumps(skills_list)
        else:
            req_skills_json = '[]'
        
        # Process preferred skills
        if 'preferred_skills' in updated_data and updated_data['preferred_skills']:
            skills_list = [skill.strip() for skill in updated_data['preferred_skills']]
            st.session_state.skills.update(skills_list)
            updated_data['preferred_skills'] = skills_list
            
            # Add skills to the skills table
            for skill in skills_list:
                add_skill(skill)
                
            pref_skills_json = json.dumps(skills_list)
        else:
            pref_skills_json = '[]'
        
        # Process certifications
        if 'required_certifications' in updated_data and updated_data['required_certifications']:
            cert_list = [cert.strip() for cert in updated_data['required_certifications']]
            st.session_state.certifications.update(cert_list)
            updated_data['required_certifications'] = cert_list
            
            # Add certifications to the certifications table
            for cert in cert_list:
                add_certification(cert)
                
            certs_json = json.dumps(cert_list)
        else:
            certs_json = '[]'
        
        # Process responsibilities
        if 'responsibilities' in updated_data and updated_data['responsibilities']:
            if isinstance(updated_data['responsibilities'], list):
                resp_list = updated_data['responsibilities']
            else:
                resp_list = [r.strip() for r in updated_data['responsibilities'].split(',') if r.strip()]
            resp_json = json.dumps(resp_list)
        else:
            resp_json = '[]'
        
        # Process department
        if 'department' in updated_data and updated_data['department']:
            st.session_state.departments.add(updated_data['department'])
            add_department(updated_data['department'])
        
        # Update database
        db_session = Session()
        
        # Check if role exists in database
        role = db_session.query(Role).filter_by(role_id=role_id).first()
        
        if not role:
            # Role doesn't exist in database, create new
            role = Role(
                role_id=role_id,
                title=updated_data.get('title', ''),
                department=updated_data.get('department', ''),
                description=updated_data.get('description', ''),
                required_skills=req_skills_json,
                preferred_skills=pref_skills_json,
                required_certifications=certs_json,
                required_experience=float(updated_data.get('required_experience', 0)),
                required_education=updated_data.get('required_education', ''),
                responsibilities=resp_json,
                last_updated=datetime.datetime.now()
            )
            db_session.add(role)
        else:
            # Update existing record
            role.title = updated_data.get('title', role.title)
            role.department = updated_data.get('department', role.department)
            role.description = updated_data.get('description', role.description)
            if 'required_skills' in updated_data:
                role.required_skills = req_skills_json
            if 'preferred_skills' in updated_data:
                role.preferred_skills = pref_skills_json
            if 'required_certifications' in updated_data:
                role.required_certifications = certs_json
            if 'required_experience' in updated_data:
                role.required_experience = float(updated_data['required_experience'])
            if 'required_education' in updated_data:
                role.required_education = updated_data['required_education']
            if 'responsibilities' in updated_data:
                role.responsibilities = resp_json
            role.last_updated = datetime.datetime.now()
        
        db_session.commit()
        db_session.close()
        
        # Update session state
        for key, value in updated_data.items():
            st.session_state.roles.at[role_idx[0], key] = value
        
        return True
    
    except Exception as e:
        st.error(f"Error updating role: {e}")
        return False

def delete_role(role_id):
    """Remove a role from the database"""
    try:
        # Find the role in session state
        role_idx = st.session_state.roles.index[st.session_state.roles['role_id'] == role_id].tolist()
        
        if not role_idx:
            return False
        
        # Remove from database
        db_session = Session()
        role = db_session.query(Role).filter_by(role_id=role_id).first()
        
        if role:
            db_session.delete(role)
            
            # Also remove any matches for this role from database
            matches = db_session.query(Match).filter_by(role_id=role_id).all()
            for match in matches:
                db_session.delete(match)
            
            db_session.commit()
        
        db_session.close()
        
        # Remove from session state
        st.session_state.roles = st.session_state.roles.drop(role_idx[0])
        
        # Also remove any matches for this role from session state
        st.session_state.matches = st.session_state.matches[st.session_state.matches['role_id'] != role_id]
        
        return True
    
    except Exception as e:
        st.error(f"Error deleting role: {e}")
        return False

def add_match(match_data):
    """Add a new employee-role match to the database"""
    try:
        # Generate unique ID if not provided
        if 'match_id' not in match_data or not match_data['match_id']:
            match_data['match_id'] = str(uuid.uuid4())
        
        # Add timestamp
        if 'match_date' not in match_data:
            match_data['match_date'] = datetime.datetime.now()
        
        # Add to database
        db_session = Session()
        
        # Check if match already exists
        existing = db_session.query(Match).filter_by(match_id=match_data['match_id']).first()
        
        if existing:
            # Update existing record
            existing.employee_id = match_data.get('employee_id', '')
            existing.role_id = match_data.get('role_id', '')
            existing.match_score = float(match_data.get('match_score', 0))
            existing.skill_match_score = float(match_data.get('skill_match_score', 0))
            existing.experience_match_score = float(match_data.get('experience_match_score', 0))
            existing.certification_match_score = float(match_data.get('certification_match_score', 0))
            existing.education_match_score = float(match_data.get('education_match_score', 0))
            existing.soft_skills_score = float(match_data.get('soft_skills_score', 0))
            existing.match_date = match_data.get('match_date', datetime.datetime.now())
            existing.notes = match_data.get('notes', '')
        else:
            # Create new record
            match = Match(
                match_id=match_data['match_id'],
                employee_id=match_data.get('employee_id', ''),
                role_id=match_data.get('role_id', ''),
                match_score=float(match_data.get('match_score', 0)),
                skill_match_score=float(match_data.get('skill_match_score', 0)),
                experience_match_score=float(match_data.get('experience_match_score', 0)),
                certification_match_score=float(match_data.get('certification_match_score', 0)),
                education_match_score=float(match_data.get('education_match_score', 0)),
                soft_skills_score=float(match_data.get('soft_skills_score', 0)),
                match_date=match_data.get('match_date', datetime.datetime.now()),
                notes=match_data.get('notes', '')
            )
            db_session.add(match)
        
        db_session.commit()
        
        # Update session state
        new_match_df = pd.DataFrame([match_data])
        st.session_state.matches = pd.concat([st.session_state.matches, new_match_df], ignore_index=True)
        
        db_session.close()
        
        return match_data['match_id']
    
    except Exception as e:
        st.error(f"Error adding match: {e}")
        return None

def get_employee_by_id(employee_id):
    """Retrieve an employee by ID"""
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]
    if len(employee) == 0:
        return None
    return employee.iloc[0]

def get_role_by_id(role_id):
    """Retrieve a role by ID"""
    role = st.session_state.roles[st.session_state.roles['role_id'] == role_id]
    if len(role) == 0:
        return None
    return role.iloc[0]

def get_match_by_id(match_id):
    """Retrieve a match by ID"""
    match = st.session_state.matches[st.session_state.matches['match_id'] == match_id]
    if len(match) == 0:
        return None
    return match.iloc[0]

def filter_employees(filters):
    """Filter employees based on provided criteria"""
    filtered_df = st.session_state.employees.copy()
    
    if 'name' in filters and filters['name']:
        filtered_df = filtered_df[filtered_df['name'].str.contains(filters['name'], case=False, na=False)]
    
    if 'department' in filters and filters['department']:
        filtered_df = filtered_df[filtered_df['department'] == filters['department']]
    
    if 'skills' in filters and filters['skills']:
        # For list-type columns, filter for rows that contain all the requested skills
        mask = filtered_df['skills'].apply(
            lambda x: all(skill in x for skill in filters['skills']) if isinstance(x, list) else False
        )
        filtered_df = filtered_df[mask]
    
    if 'certifications' in filters and filters['certifications']:
        # For list-type columns, filter for rows that contain all the requested certifications
        mask = filtered_df['certifications'].apply(
            lambda x: all(cert in x for cert in filters['certifications']) if isinstance(x, list) else False
        )
        filtered_df = filtered_df[mask]
    
    return filtered_df

def filter_roles(filters):
    """Filter roles based on provided criteria"""
    filtered_df = st.session_state.roles.copy()
    
    if 'title' in filters and filters['title']:
        filtered_df = filtered_df[filtered_df['title'].str.contains(filters['title'], case=False, na=False)]
    
    if 'department' in filters and filters['department']:
        filtered_df = filtered_df[filtered_df['department'] == filters['department']]
    
    if 'required_skills' in filters and filters['required_skills']:
        # For list-type columns, filter for rows that contain all the requested skills
        mask = filtered_df['required_skills'].apply(
            lambda x: all(skill in x for skill in filters['required_skills']) if isinstance(x, list) else False
        )
        filtered_df = filtered_df[mask]
    
    if 'required_certifications' in filters and filters['required_certifications']:
        # For list-type columns, filter for rows that contain all the requested certifications
        mask = filtered_df['required_certifications'].apply(
            lambda x: all(cert in x for cert in filters['required_certifications']) if isinstance(x, list) else False
        )
        filtered_df = filtered_df[mask]
    
    return filtered_df

def export_data(data_type, file_format="csv"):
    """Export data to a file"""
    if data_type == "employees":
        data = st.session_state.employees
    elif data_type == "roles":
        data = st.session_state.roles
    elif data_type == "matches":
        data = st.session_state.matches
    else:
        return None
    
    if file_format == "csv":
        return data.to_csv(index=False)
    elif file_format == "excel":
        # For Excel, we'll return the DataFrame directly
        return data
    elif file_format == "json":
        return data.to_json(orient="records")
    
    return None

def import_data(data_type, data, file_format="csv"):
    """Import data from a file"""
    try:
        if file_format == "csv":
            imported_df = pd.read_csv(data)
        elif file_format == "excel":
            imported_df = pd.read_excel(data)
        elif file_format == "json":
            imported_df = pd.read_json(data)
        else:
            return False
        
        if data_type == "employees":
            st.session_state.employees = imported_df
            
            # Update database
            db_session = Session()
            for _, row in imported_df.iterrows():
                # Convert list fields to JSON strings
                if isinstance(row.get('skills'), list):
                    skills_json = json.dumps(row['skills'])
                    st.session_state.skills.update(row['skills'])
                    for skill in row['skills']:
                        add_skill(skill)
                else:
                    skills_json = '[]'
                
                if isinstance(row.get('certifications'), list):
                    certs_json = json.dumps(row['certifications'])
                    st.session_state.certifications.update(row['certifications'])
                    for cert in row['certifications']:
                        add_certification(cert)
                else:
                    certs_json = '[]'
                
                if isinstance(row.get('projects'), list):
                    projects_json = json.dumps(row['projects'])
                else:
                    projects_json = '[]'
                
                if row.get('department'):
                    st.session_state.departments.add(row['department'])
                    add_department(row['department'])
                
                # Check if employee exists
                existing = db_session.query(Employee).filter_by(employee_id=row['employee_id']).first()
                
                if existing:
                    # Update existing record
                    existing.name = row.get('name', '')
                    existing.department = row.get('department', '')
                    existing.job_title = row.get('job_title', '')
                    existing.joining_date = row.get('joining_date', datetime.datetime.now())
                    existing.skills = skills_json
                    existing.certifications = certs_json
                    existing.experience = float(row.get('experience', 0))
                    existing.education = row.get('education', '')
                    existing.projects = projects_json
                    existing.peer_reviews = row.get('peer_reviews', '')
                    existing.last_updated = datetime.datetime.now()
                else:
                    # Create new record
                    employee = Employee(
                        employee_id=row['employee_id'],
                        name=row.get('name', ''),
                        department=row.get('department', ''),
                        job_title=row.get('job_title', ''),
                        joining_date=row.get('joining_date', datetime.datetime.now()),
                        skills=skills_json,
                        certifications=certs_json,
                        experience=float(row.get('experience', 0)),
                        education=row.get('education', ''),
                        projects=projects_json,
                        peer_reviews=row.get('peer_reviews', ''),
                        last_updated=datetime.datetime.now()
                    )
                    db_session.add(employee)
            
            db_session.commit()
            db_session.close()
        
        elif data_type == "roles":
            st.session_state.roles = imported_df
            
            # Update database
            db_session = Session()
            for _, row in imported_df.iterrows():
                # Convert list fields to JSON strings
                if isinstance(row.get('required_skills'), list):
                    req_skills_json = json.dumps(row['required_skills'])
                    st.session_state.skills.update(row['required_skills'])
                    for skill in row['required_skills']:
                        add_skill(skill)
                else:
                    req_skills_json = '[]'
                
                if isinstance(row.get('preferred_skills'), list):
                    pref_skills_json = json.dumps(row['preferred_skills'])
                    st.session_state.skills.update(row['preferred_skills'])
                    for skill in row['preferred_skills']:
                        add_skill(skill)
                else:
                    pref_skills_json = '[]'
                
                if isinstance(row.get('required_certifications'), list):
                    certs_json = json.dumps(row['required_certifications'])
                    st.session_state.certifications.update(row['required_certifications'])
                    for cert in row['required_certifications']:
                        add_certification(cert)
                else:
                    certs_json = '[]'
                
                if isinstance(row.get('responsibilities'), list):
                    resp_json = json.dumps(row['responsibilities'])
                else:
                    resp_json = '[]'
                
                if row.get('department'):
                    st.session_state.departments.add(row['department'])
                    add_department(row['department'])
                
                # Check if role exists
                existing = db_session.query(Role).filter_by(role_id=row['role_id']).first()
                
                if existing:
                    # Update existing record
                    existing.title = row.get('title', '')
                    existing.department = row.get('department', '')
                    existing.description = row.get('description', '')
                    existing.required_skills = req_skills_json
                    existing.preferred_skills = pref_skills_json
                    existing.required_certifications = certs_json
                    existing.required_experience = float(row.get('required_experience', 0))
                    existing.required_education = row.get('required_education', '')
                    existing.responsibilities = resp_json
                    existing.last_updated = datetime.datetime.now()
                else:
                    # Create new record
                    role = Role(
                        role_id=row['role_id'],
                        title=row.get('title', ''),
                        department=row.get('department', ''),
                        description=row.get('description', ''),
                        required_skills=req_skills_json,
                        preferred_skills=pref_skills_json,
                        required_certifications=certs_json,
                        required_experience=float(row.get('required_experience', 0)),
                        required_education=row.get('required_education', ''),
                        responsibilities=resp_json,
                        last_updated=datetime.datetime.now()
                    )
                    db_session.add(role)
            
            db_session.commit()
            db_session.close()
        
        elif data_type == "matches":
            st.session_state.matches = imported_df
            
            # Update database
            db_session = Session()
            for _, row in imported_df.iterrows():
                # Check if match exists
                existing = db_session.query(Match).filter_by(match_id=row['match_id']).first()
                
                if existing:
                    # Update existing record
                    existing.employee_id = row.get('employee_id', '')
                    existing.role_id = row.get('role_id', '')
                    existing.match_score = float(row.get('match_score', 0))
                    existing.skill_match_score = float(row.get('skill_match_score', 0))
                    existing.experience_match_score = float(row.get('experience_match_score', 0))
                    existing.certification_match_score = float(row.get('certification_match_score', 0))
                    existing.education_match_score = float(row.get('education_match_score', 0))
                    existing.soft_skills_score = float(row.get('soft_skills_score', 0))
                    existing.match_date = row.get('match_date', datetime.datetime.now())
                    existing.notes = row.get('notes', '')
                else:
                    # Create new record
                    match = Match(
                        match_id=row['match_id'],
                        employee_id=row.get('employee_id', ''),
                        role_id=row.get('role_id', ''),
                        match_score=float(row.get('match_score', 0)),
                        skill_match_score=float(row.get('skill_match_score', 0)),
                        experience_match_score=float(row.get('experience_match_score', 0)),
                        certification_match_score=float(row.get('certification_match_score', 0)),
                        education_match_score=float(row.get('education_match_score', 0)),
                        soft_skills_score=float(row.get('soft_skills_score', 0)),
                        match_date=row.get('match_date', datetime.datetime.now()),
                        notes=row.get('notes', '')
                    )
                    db_session.add(match)
            
            db_session.commit()
            db_session.close()
        
        else:
            return False
        
        return True
    
    except Exception as e:
        st.error(f"Error importing data: {e}")
        return False

# Database helper functions
def get_all_employees():
    """Retrieve all employees from the database"""
    try:
        db_session = Session()
        employees = db_session.query(Employee).all()
        
        # Convert to DataFrame
        employees_data = []
        for emp in employees:
            # Parse JSON strings back to lists
            skills = json.loads(emp.skills) if emp.skills else []
            certifications = json.loads(emp.certifications) if emp.certifications else []
            projects = json.loads(emp.projects) if emp.projects else []
            
            employees_data.append({
                'employee_id': emp.employee_id,
                'name': emp.name,
                'department': emp.department,
                'job_title': emp.job_title,
                'joining_date': emp.joining_date,
                'skills': skills,
                'certifications': certifications,
                'experience': emp.experience,
                'education': emp.education,
                'projects': projects,
                'peer_reviews': emp.peer_reviews,
                'last_updated': emp.last_updated
            })
        
        db_session.close()
        
        if employees_data:
            return pd.DataFrame(employees_data)
        else:
            return pd.DataFrame(
                columns=['employee_id', 'name', 'department', 'job_title', 'joining_date', 
                         'skills', 'certifications', 'experience', 'education', 'projects',
                         'peer_reviews', 'last_updated']
            )
    
    except Exception as e:
        st.error(f"Error retrieving employees: {e}")
        return pd.DataFrame(
            columns=['employee_id', 'name', 'department', 'job_title', 'joining_date', 
                     'skills', 'certifications', 'experience', 'education', 'projects',
                     'peer_reviews', 'last_updated']
        )

def get_all_roles():
    """Retrieve all roles from the database"""
    try:
        db_session = Session()
        roles = db_session.query(Role).all()
        
        # Convert to DataFrame
        roles_data = []
        for role in roles:
            # Parse JSON strings back to lists
            required_skills = json.loads(role.required_skills) if role.required_skills else []
            preferred_skills = json.loads(role.preferred_skills) if role.preferred_skills else []
            required_certifications = json.loads(role.required_certifications) if role.required_certifications else []
            responsibilities = json.loads(role.responsibilities) if role.responsibilities else []
            
            roles_data.append({
                'role_id': role.role_id,
                'title': role.title,
                'department': role.department,
                'description': role.description,
                'required_skills': required_skills,
                'preferred_skills': preferred_skills,
                'required_certifications': required_certifications,
                'required_experience': role.required_experience,
                'required_education': role.required_education,
                'responsibilities': responsibilities,
                'last_updated': role.last_updated
            })
        
        db_session.close()
        
        if roles_data:
            return pd.DataFrame(roles_data)
        else:
            return pd.DataFrame(
                columns=['role_id', 'title', 'department', 'description', 'required_skills',
                         'preferred_skills', 'required_certifications', 'required_experience',
                         'required_education', 'responsibilities', 'last_updated']
            )
    
    except Exception as e:
        st.error(f"Error retrieving roles: {e}")
        return pd.DataFrame(
            columns=['role_id', 'title', 'department', 'description', 'required_skills',
                     'preferred_skills', 'required_certifications', 'required_experience',
                     'required_education', 'responsibilities', 'last_updated']
        )

def get_all_matches():
    """Retrieve all matches from the database"""
    try:
        db_session = Session()
        matches = db_session.query(Match).all()
        
        # Convert to DataFrame
        matches_data = []
        for match in matches:
            matches_data.append({
                'match_id': match.match_id,
                'employee_id': match.employee_id,
                'role_id': match.role_id,
                'match_score': match.match_score,
                'skill_match_score': match.skill_match_score,
                'experience_match_score': match.experience_match_score,
                'certification_match_score': match.certification_match_score,
                'education_match_score': match.education_match_score,
                'soft_skills_score': match.soft_skills_score,
                'match_date': match.match_date,
                'notes': match.notes
            })
        
        db_session.close()
        
        if matches_data:
            return pd.DataFrame(matches_data)
        else:
            return pd.DataFrame(
                columns=['match_id', 'employee_id', 'role_id', 'match_score', 
                         'skill_match_score', 'experience_match_score', 'certification_match_score',
                         'education_match_score', 'soft_skills_score', 'match_date', 'notes']
            )
    
    except Exception as e:
        st.error(f"Error retrieving matches: {e}")
        return pd.DataFrame(
            columns=['match_id', 'employee_id', 'role_id', 'match_score', 
                     'skill_match_score', 'experience_match_score', 'certification_match_score',
                     'education_match_score', 'soft_skills_score', 'match_date', 'notes']
        )

def get_all_skills():
    """Retrieve all skills from the database"""
    try:
        db_session = Session()
        skills = db_session.query(Skill).all()
        
        result = set()
        for skill in skills:
            result.add(skill.skill_name)
        
        db_session.close()
        return result
    
    except Exception as e:
        st.error(f"Error retrieving skills: {e}")
        return set()

def get_all_departments():
    """Retrieve all departments from the database"""
    try:
        db_session = Session()
        departments = db_session.query(Department).all()
        
        result = set()
        for dept in departments:
            result.add(dept.department_name)
        
        db_session.close()
        return result
    
    except Exception as e:
        st.error(f"Error retrieving departments: {e}")
        return set()

def get_all_certifications():
    """Retrieve all certifications from the database"""
    try:
        db_session = Session()
        certifications = db_session.query(Certification).all()
        
        result = set()
        for cert in certifications:
            result.add(cert.certification_name)
        
        db_session.close()
        return result
    
    except Exception as e:
        st.error(f"Error retrieving certifications: {e}")
        return set()

def add_skill(skill_name):
    """Add a skill to the database if it doesn't exist"""
    try:
        db_session = Session()
        
        # Check if skill already exists
        existing = db_session.query(Skill).filter_by(skill_name=skill_name).first()
        
        if not existing:
            # Add new skill
            skill = Skill(skill_name=skill_name)
            db_session.add(skill)
            db_session.commit()
        
        db_session.close()
        return True
    
    except Exception as e:
        st.error(f"Error adding skill: {e}")
        return False

def add_department(department_name):
    """Add a department to the database if it doesn't exist"""
    try:
        db_session = Session()
        
        # Check if department already exists
        existing = db_session.query(Department).filter_by(department_name=department_name).first()
        
        if not existing:
            # Add new department
            department = Department(department_name=department_name)
            db_session.add(department)
            db_session.commit()
        
        db_session.close()
        return True
    
    except Exception as e:
        st.error(f"Error adding department: {e}")
        return False

def add_certification(certification_name):
    """Add a certification to the database if it doesn't exist"""
    try:
        db_session = Session()
        
        # Check if certification already exists
        existing = db_session.query(Certification).filter_by(certification_name=certification_name).first()
        
        if not existing:
            # Add new certification
            certification = Certification(certification_name=certification_name)
            db_session.add(certification)
            db_session.commit()
        
        db_session.close()
        return True
    
    except Exception as e:
        st.error(f"Error adding certification: {e}")
        return False
