import streamlit as st
import pandas as pd
import os
from data_manager import initialize_data

# Page configuration
st.set_page_config(
    page_title="Chevron Skills Assessment & Matching System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0f5499;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e6e6e6;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.15rem 1.75rem rgba(0, 0, 0, 0.15);
        margin-bottom: 1.5rem;
    }
    .dashboard-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        transition: transform 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        font-weight: bold;
        font-size: 1.1rem;
        color: #0f5499;
    }
    .getting-started-step {
        background-color: #f1f8ff;
        padding: 1rem;
        border-left: 4px solid #0f5499;
        margin-bottom: 0.5rem;
    }
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #6c757d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    
    # Initialize empty values for session state to prevent access errors
    st.session_state.employees = pd.DataFrame()
    st.session_state.roles = pd.DataFrame()
    st.session_state.matches = pd.DataFrame()
    st.session_state.skills = set()
    st.session_state.departments = set(['Engineering', 'Human Resources', 'Finance', 
                                     'Operations', 'Research & Development', 
                                     'Information Technology', 'Marketing', 'Legal'])
    st.session_state.certifications = set()

if not st.session_state.initialized:
    # Initialize data structures from database
    initialize_data()
    st.session_state.initialized = True

# Main page content with Chevron branding - official colors
chevron_blue = "#0050AA"  # Chevron's official blue color (PMS 2935 C)
chevron_red = "#E21836"   # Chevron's official red color (PMS 186 C)

# Load Chevron logo from local file
import base64
from pathlib import Path

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Use local Chevron logo
logo_path = "attached_assets/Chevron_Logo.svg.png"
try:
    encoded_logo = get_image_base64(logo_path)
    chevron_logo = f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <img src="data:image/png;base64,{encoded_logo}" alt="Chevron Logo" width="200">
    </div>
    """
except Exception as e:
    # Fallback if logo can't be loaded
    chevron_logo = """
    <div style="text-align: center; margin-bottom: 1rem;">
        <h2 style="color: #0050AA;">Chevron</h2>
    </div>
    """

# Display Chevron logo

st.markdown(chevron_logo, unsafe_allow_html=True)
st.markdown(f"<h1 class='main-header' style='color: {chevron_blue};'>Skills Assessment & Matching System</h1>", unsafe_allow_html=True)

# Hero section with Chevron branded colors
st.markdown(f"""
<div style="margin-bottom: 2rem;">
    <div>
        <h2 style="color: {chevron_blue};">Welcome to the AI-powered Employee Skill Assessment System</h2>
        <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
            The advanced platform that helps HR professionals optimize talent allocation through AI-powered skill matching.
        </p>
        <div style="background-color: #f5f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {chevron_blue};">
            <p style="font-weight: bold; margin-bottom: 0.5rem;">Key Features:</p>
            <ul style="margin-bottom: 0;">
                <li>AI-driven skill assessment and role matching</li>
                <li>Comprehensive employee profile management</li>
                <li>Detailed skill gap analysis for development planning</li>
                <li>Data visualization for better decision making</li>
                <li>Customizable reporting for stakeholder presentations</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dashboard statistics with enhanced cards using Chevron colors
st.markdown(f"<h3 style='color: {chevron_blue}; margin-top: 2rem;'>Dashboard Overview</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    employee_count = len(st.session_state.employees)
    st.markdown(f"""
    <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(0, 80, 170, 0.15), rgba(0, 80, 170, 0.05)); 
         border-left: 6px solid {chevron_blue}; box-shadow: 0 4px 12px rgba(0, 80, 170, 0.1); transform: translateY(0); 
         transition: all 0.3s;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 600; color: {chevron_blue};">TOTAL EMPLOYEES</div>
            <div style="background-color: rgba(0, 80, 170, 0.15); border-radius: 50%; width: 32px; height: 32px; 
                 display: flex; justify-content: center; align-items: center;">
                <i class="fas fa-users" style="color: {chevron_blue};"></i>
            </div>
        </div>
        <div style="font-size: 2.5rem; font-weight: bold; color: {chevron_blue}; margin: 0.8rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{employee_count}</div>
        <div style="font-size: 0.85rem; color: #555; display: flex; align-items: center;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                  background-color: {chevron_blue}; margin-right: 5px;"></span>
            Active profiles in system
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    role_count = len(st.session_state.roles)
    st.markdown(f"""
    <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(0, 80, 170, 0.15), rgba(0, 80, 170, 0.05)); 
         border-left: 6px solid {chevron_blue}; box-shadow: 0 4px 12px rgba(0, 80, 170, 0.1); transform: translateY(0); 
         transition: all 0.3s;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 600; color: {chevron_blue};">TOTAL ROLES</div>
            <div style="background-color: rgba(0, 80, 170, 0.15); border-radius: 50%; width: 32px; height: 32px; 
                 display: flex; justify-content: center; align-items: center;">
                <i class="fas fa-briefcase" style="color: {chevron_blue};"></i>
            </div>
        </div>
        <div style="font-size: 2.5rem; font-weight: bold; color: {chevron_blue}; margin: 0.8rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{role_count}</div>
        <div style="font-size: 0.85rem; color: #555; display: flex; align-items: center;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                  background-color: {chevron_blue}; margin-right: 5px;"></span>
            Available positions
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    skill_count = len(st.session_state.skills) if 'skills' in st.session_state else 0
    st.markdown(f"""
    <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(226, 24, 54, 0.15), rgba(226, 24, 54, 0.05)); 
         border-left: 6px solid {chevron_red}; box-shadow: 0 4px 12px rgba(226, 24, 54, 0.1); transform: translateY(0); 
         transition: all 0.3s;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 600; color: {chevron_red};">SKILLS DATABASE</div>
            <div style="background-color: rgba(226, 24, 54, 0.15); border-radius: 50%; width: 32px; height: 32px; 
                 display: flex; justify-content: center; align-items: center;">
                <i class="fas fa-cogs" style="color: {chevron_red};"></i>
            </div>
        </div>
        <div style="font-size: 2.5rem; font-weight: bold; color: {chevron_red}; margin: 0.8rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{skill_count}</div>
        <div style="font-size: 0.85rem; color: #555; display: flex; align-items: center;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                  background-color: {chevron_red}; margin-right: 5px;"></span>
            Tracked competencies
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    matches = st.session_state.matches if 'matches' in st.session_state else []
    match_count = len(matches)
    st.markdown(f"""
    <div class="dashboard-card" style="background: linear-gradient(135deg, rgba(226, 24, 54, 0.15), rgba(226, 24, 54, 0.05)); 
         border-left: 6px solid {chevron_red}; box-shadow: 0 4px 12px rgba(226, 24, 54, 0.1); transform: translateY(0); 
         transition: all 0.3s;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 0.9rem; font-weight: 600; color: {chevron_red};">RECENT MATCHES</div>
            <div style="background-color: rgba(226, 24, 54, 0.15); border-radius: 50%; width: 32px; height: 32px; 
                 display: flex; justify-content: center; align-items: center;">
                <i class="fas fa-handshake" style="color: {chevron_red};"></i>
            </div>
        </div>
        <div style="font-size: 2.5rem; font-weight: bold; color: {chevron_red}; margin: 0.8rem 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{match_count}</div>
        <div style="font-size: 0.85rem; color: #555; display: flex; align-items: center;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; 
                  background-color: {chevron_red}; margin-right: 5px;"></span>
            Employee-role matches
        </div>
    </div>
    """, unsafe_allow_html=True)

# Recent activity dashboard with enhanced UI using Chevron colors
st.markdown(f"<h3 style='color: {chevron_blue}; margin-top: 2rem;'>Recent Activity</h3>", unsafe_allow_html=True)

# Activity tabs for different data types
activity_tab1, activity_tab2, activity_tab3 = st.tabs(["Recent Employees", "Recent Roles", "Recent Matches"])

with activity_tab1:
    if len(st.session_state.employees) > 0:
        # Check if employees is a DataFrame
        if isinstance(st.session_state.employees, pd.DataFrame):
            recent_employees = st.session_state.employees.head(5) if len(st.session_state.employees) > 5 else st.session_state.employees
            
            # Enhanced dataframe with highlighting and styling using Chevron blue
            st.markdown(f"""
            <div style="background-color: rgba(0, 80, 170, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="margin: 0; color: {chevron_blue};">Recently Added/Updated Employees</h5>
                    <span style="background-color: {chevron_blue}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                        {len(recent_employees)} records
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            display_cols = ['employee_id', 'name', 'department', 'job_title']
            # Make sure all columns exist in the dataframe
            valid_cols = [col for col in display_cols if col in recent_employees.columns]
            
            # Use Streamlit's native dataframe with additional styling
            st.dataframe(
                recent_employees[valid_cols], 
                use_container_width=True,
                column_config={
                    "employee_id": "Employee ID",
                    "name": "Full Name",
                    "department": "Department",
                    "job_title": "Current Position"
                },
                hide_index=True
            )
        elif isinstance(st.session_state.employees, list):
            # Handle if employees is a list of dictionaries
            employee_list = st.session_state.employees[:5] if len(st.session_state.employees) > 5 else st.session_state.employees
            
            st.markdown(f"""
            <div style="background-color: rgba(0, 80, 170, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="margin: 0; color: {chevron_blue};">Recently Added/Updated Employees</h5>
                    <span style="background-color: {chevron_blue}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                        {len(employee_list)} records
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Convert list to DataFrame for display
            employees_df = pd.DataFrame(employee_list)
            if not employees_df.empty:
                display_cols = ['employee_id', 'name', 'department', 'job_title']
                # Make sure all columns exist in the dataframe
                valid_cols = [col for col in display_cols if col in employees_df.columns]
                
                st.dataframe(
                    employees_df[valid_cols] if valid_cols else employees_df,
                    use_container_width=True,
                    column_config={
                        "employee_id": "Employee ID",
                        "name": "Full Name",
                        "department": "Department",
                        "job_title": "Current Position"
                    },
                    hide_index=True
                )
            else:
                st.info("Employee data available but format needs conversion.")
    else:
        st.info("No employee records found. Add employees using the Employee Management page.")

with activity_tab2:
    if len(st.session_state.roles) > 0:
        # Check if roles is a DataFrame
        if isinstance(st.session_state.roles, pd.DataFrame):
            recent_roles = st.session_state.roles.head(5) if len(st.session_state.roles) > 5 else st.session_state.roles
            
            # Enhanced dataframe with highlighting and styling using Chevron blue
            st.markdown(f"""
            <div style="background-color: rgba(0, 80, 170, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="margin: 0; color: {chevron_blue};">Recently Added/Updated Roles</h5>
                    <span style="background-color: {chevron_blue}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                        {len(recent_roles)} records
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            display_cols = ['role_id', 'title', 'department', 'required_experience']
            # Make sure all columns exist in the dataframe
            valid_cols = [col for col in display_cols if col in recent_roles.columns]
            
            # Use Streamlit's native dataframe with additional styling
            st.dataframe(
                recent_roles[valid_cols], 
                use_container_width=True,
                column_config={
                    "role_id": "Role ID",
                    "title": "Position Title",
                    "department": "Department",
                    "required_experience": st.column_config.NumberColumn(
                        "Required Experience (Years)",
                        format="%.1f"
                    )
                },
                hide_index=True
            )
        elif isinstance(st.session_state.roles, list):
            # Handle if roles is a list of dictionaries
            role_list = st.session_state.roles[:5] if len(st.session_state.roles) > 5 else st.session_state.roles
            
            st.markdown(f"""
            <div style="background-color: rgba(0, 80, 170, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="margin: 0; color: {chevron_blue};">Recently Added/Updated Roles</h5>
                    <span style="background-color: {chevron_blue}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                        {len(role_list)} records
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Convert list to DataFrame for display
            roles_df = pd.DataFrame(role_list)
            if not roles_df.empty:
                display_cols = ['role_id', 'title', 'department', 'required_experience']
                # Make sure all columns exist in the dataframe
                valid_cols = [col for col in display_cols if col in roles_df.columns]
                
                st.dataframe(
                    roles_df[valid_cols] if valid_cols else roles_df,
                    use_container_width=True,
                    column_config={
                        "role_id": "Role ID",
                        "title": "Position Title",
                        "department": "Department",
                        "required_experience": st.column_config.NumberColumn(
                            "Required Experience (Years)",
                            format="%.1f"
                        )
                    },
                    hide_index=True
                )
            else:
                st.info("Role data available but format needs conversion.")
    else:
        st.info("No role records found. Add roles using the Role Management page.")

with activity_tab3:
    matches = st.session_state.matches if 'matches' in st.session_state else []
    if isinstance(matches, pd.DataFrame) and len(matches) > 0:
        recent_matches = matches.head(5) if len(matches) > 5 else matches
        
        # Enhanced dataframe with highlighting and styling using Chevron red
        st.markdown(f"""
        <div style="background-color: rgba(226, 24, 54, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: {chevron_red};">Recent Employee-Role Matches</h5>
                <span style="background-color: {chevron_red}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                    {len(recent_matches)} records
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit's native dataframe with additional styling
        display_cols = ['match_id', 'employee_id', 'role_id', 'match_score']
        # Make sure all columns exist in the dataframe
        valid_cols = [col for col in display_cols if col in recent_matches.columns]
        
        st.dataframe(
            recent_matches[valid_cols], 
            use_container_width=True,
            column_config={
                "match_id": "Match ID",
                "employee_id": "Employee",
                "role_id": "Role",
                "match_score": st.column_config.ProgressColumn(
                    "Match Score",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                )
            },
            hide_index=True
        )
    elif isinstance(matches, list) and len(matches) > 0:
        # Handle if matches is a list of dictionaries
        match_list = matches[:5] if len(matches) > 5 else matches
        st.markdown(f"""
        <div style="background-color: rgba(226, 24, 54, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: {chevron_red};">Recent Employee-Role Matches</h5>
                <span style="background-color: {chevron_red}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;">
                    {len(match_list)} records
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Convert list to DataFrame for display
        matches_df = pd.DataFrame(match_list)
        if not matches_df.empty:
            display_cols = ['match_id', 'employee_id', 'role_id', 'match_score']
            # Make sure all columns exist in the dataframe
            valid_cols = [col for col in display_cols if col in matches_df.columns]
            
            st.dataframe(
                matches_df[valid_cols] if valid_cols else matches_df,
                use_container_width=True,
                column_config={
                    "match_id": "Match ID",
                    "employee_id": "Employee",
                    "role_id": "Role",
                    "match_score": st.column_config.ProgressColumn(
                        "Match Score",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100
                    ) if 'match_score' in matches_df.columns else None
                },
                hide_index=True
            )
        else:
            st.info("Match data available but format needs conversion. Use Skill Matching to generate properly formatted matches.")
    else:
        st.info("No match records found. Create matches using the Skill Matching page.")

# Getting started guide with interactive cards
st.markdown(f"<h3 style='color: {chevron_blue}; margin-top: 2rem;'>Getting Started</h3>", unsafe_allow_html=True)

# Create tabs for different user flows
tab1, tab2 = st.tabs(["Features Overview", "Quick Start Guide"])

with tab1:
    # Feature cards in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4 style="color: {chevron_blue}; margin-top: 0;"><i class="fas fa-user-circle"></i> Employee Management</h4>
            <p>Create comprehensive employee profiles with detailed skills, education, certifications, and experience data.</p>
            <ul>
                <li>Add, edit, and search employee records</li>
                <li>Track skills and certifications</li>
                <li>Document project experience and performance</li>
            </ul>
            <div style="text-align: right;">
                <a href="Employee_Management" target="_self" style="text-decoration: none;">
                    <span style="background-color: {chevron_blue}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">
                        Manage Employees →
                    </span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card">
            <h4 style="color: {chevron_blue}; margin-top: 0;"><i class="fas fa-exchange-alt"></i> Skill Matching</h4>
            <p>Use AI-powered algorithms to match employees to roles based on skills, experience, and other factors.</p>
            <ul>
                <li>Run matching algorithms on selected employees and roles</li>
                <li>View match scores with detailed component breakdowns</li>
                <li>Identify skill gaps and development opportunities</li>
            </ul>
            <div style="text-align: right;">
                <a href="Skill_Matching" target="_self" style="text-decoration: none;">
                    <span style="background-color: {chevron_blue}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">
                        Start Matching →
                    </span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="card">
            <h4 style="color: {chevron_blue}; margin-top: 0;"><i class="fas fa-briefcase"></i> Role Management</h4>
            <p>Define role requirements with detailed skill needs, responsibilities, and qualification criteria.</p>
            <ul>
                <li>Create and modify role profiles</li>
                <li>Specify required and preferred skills</li>
                <li>Set experience and education requirements</li>
            </ul>
            <div style="text-align: right;">
                <a href="Role_Management" target="_self" style="text-decoration: none;">
                    <span style="background-color: {chevron_blue}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">
                        Manage Roles →
                    </span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card">
            <h4 style="color: {chevron_red}; margin-top: 0;"><i class="fas fa-chart-line"></i> Reports & Analytics</h4>
            <p>Generate comprehensive reports on workforce skills, role matches, and skill gap analysis.</p>
            <ul>
                <li>View department-level skill distribution</li>
                <li>Analyze skill gaps across the organization</li>
                <li>Export data for stakeholder presentations</li>
            </ul>
            <div style="text-align: right;">
                <a href="Reports" target="_self" style="text-decoration: none;">
                    <span style="background-color: {chevron_red}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8rem;">
                        View Reports →
                    </span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    # Step-by-step guide
    st.markdown(f"""
    <div style="padding: 1.5rem; background-color: rgba(0, 80, 170, 0.05); border-radius: 0.5rem;">
        <h4 style="margin-top: 0; color: {chevron_blue};">Quick Start in 4 Easy Steps</h4>
        
        <div class="getting-started-step">
            <div style="font-weight: bold; color: {chevron_blue};">Step 1: Add Employees</div>
            <p>Navigate to the Employee Management page and create profiles for your team members, including their skills, experience, and certifications.</p>
        </div>
        
        <div class="getting-started-step">
            <div style="font-weight: bold; color: {chevron_blue};">Step 2: Define Roles</div>
            <p>Go to Role Management to create role profiles with required skills, experience levels, and responsibilities.</p>
        </div>
        
        <div class="getting-started-step">
            <div style="font-weight: bold; color: {chevron_blue};">Step 3: Run Matching</div>
            <p>Use the Skill Matching page to match employees to roles using our AI algorithm. Review match scores and skill gap analysis.</p>
        </div>
        
        <div class="getting-started-step">
            <div style="font-weight: bold; color: {chevron_red};">Step 4: Generate Reports</div>
            <p>Access the Reports page to visualize data, generate insights, and export information for stakeholder presentations.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Pro Tip:** Use the sidebar to navigate between different sections of the application.")

# Enhanced modern footer with Chevron branding
st.markdown(f"""
<div class="footer" style="margin-top: 3rem; padding: 2rem; background-color: rgba(0, 80, 170, 0.05); border-radius: 0.5rem; text-align: center;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
        <div style="flex: 1; text-align: left;">
            <h4 style="color: {chevron_blue}; margin-top: 0;">Chevron Skills Assessment & Matching System</h4>
            <p style="color: #666; font-size: 0.9rem;">
                A powerful AI-driven platform for optimizing talent allocation<br>
                and workforce development at Chevron.
            </p>
        </div>
        <div style="flex: 1; text-align: center;">
            <h5 style="color: {chevron_blue}; margin-top: 0;">Quick Links</h5>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <li><a href="Employee_Management" style="color: {chevron_blue}; text-decoration: none;">Employee Management</a></li>
                <li><a href="Role_Management" style="color: {chevron_blue}; text-decoration: none;">Role Management</a></li>
                <li><a href="Skill_Matching" style="color: {chevron_blue}; text-decoration: none;">Skill Matching</a></li>
                <li><a href="Reports" style="color: {chevron_blue}; text-decoration: none;">Reports & Analytics</a></li>
            </ul>
        </div>
        <div style="flex: 1; text-align: right;">
            <h5 style="color: {chevron_blue}; margin-top: 0;">Contact Support</h5>
            <p style="color: #666; font-size: 0.9rem;">
                Need help using this application?<br>
                Contact HR Technology Support at:<br>
                <a href="mailto:hr.tech@chevron.example.com" style="color: {chevron_blue}; text-decoration: none;">hr.tech@chevron.example.com</a>
            </p>
        </div>
    </div>
    <div style="border-top: 1px solid #e6e6e6; padding-top: 1rem;">
        <p style="color: #666; font-size: 0.8rem; margin: 0;">
            © 2023 Chevron Skills Assessment & Matching System. All rights reserved.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
