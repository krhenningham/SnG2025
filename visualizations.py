import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_match_score_radar(match_data):
    """
    Create a radar chart showing the match scores across different categories
    
    Parameters:
    - match_data: Dictionary with match scores
    
    Returns:
    - Plotly figure
    """
    categories = [
        'Skills', 'Experience', 'Certifications', 
        'Education', 'Soft Skills'
    ]
    
    values = [
        match_data['skill_match'],
        match_data['experience_match'],
        match_data['certification_match'],
        match_data['education_match'],
        match_data['soft_skills']
    ]
    
    # Add overall score to the data
    categories.append('Overall')
    values.append(match_data['overall'])
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Match Score',
        line_color='rgb(31, 119, 180)',
        fillcolor='rgba(31, 119, 180, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title="Match Score Components"
    )
    
    return fig

def plot_employee_role_match_heatmap(match_results, top_n=10):
    """
    Create a heatmap showing match scores between employees and roles
    
    Parameters:
    - match_results: Results from match_employees_to_roles function
    - top_n: Number of top matches to display
    
    Returns:
    - Plotly figure
    """
    # Extract top matches
    all_matches = match_results['all_matches'][:top_n*2]  # Get more than needed to ensure variety
    
    # Get unique employees and roles from the matches
    unique_employees = set()
    unique_roles = set()
    
    for match in all_matches:
        unique_employees.add(match['employee_name'])
        unique_roles.add(match['role_title'])
    
    # Limit to top_n of each if we have more
    if len(unique_employees) > top_n:
        unique_employees = set([match['employee_name'] for match in all_matches[:top_n]])
    
    if len(unique_roles) > top_n:
        unique_roles = set([match['role_title'] for match in all_matches[:top_n]])
    
    # Create a DataFrame for the heatmap
    heatmap_data = []
    
    for match in all_matches:
        if match['employee_name'] in unique_employees and match['role_title'] in unique_roles:
            heatmap_data.append({
                'Employee': match['employee_name'],
                'Role': match['role_title'],
                'Match Score': match['overall_score']
            })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create pivot table
    pivot_table = heatmap_df.pivot_table(
        values='Match Score', 
        index='Employee',
        columns='Role',
        fill_value=0
    )
    
    # Create heatmap
    fig = px.imshow(
        pivot_table.values,
        labels=dict(x="Role", y="Employee", color="Match Score"),
        x=pivot_table.columns,
        y=pivot_table.index,
        color_continuous_scale='Viridis',
        title="Employee-Role Match Heatmap"
    )
    
    fig.update_layout(
        xaxis=dict(tickangle=45),
        coloraxis_colorbar=dict(title="Score")
    )
    
    return fig

def plot_skill_distribution(employees=None):
    """
    Create a bar chart showing the distribution of skills across employees
    
    Parameters:
    - employees: DataFrame of employees (default: all employees in session state)
    
    Returns:
    - Plotly figure
    """
    if employees is None:
        employees = st.session_state.employees
    
    # Extract all skills and count occurrences
    skill_counts = {}
    
    for _, employee in employees.iterrows():
        skills = employee.get('skills', [])
        
        if not isinstance(skills, list):
            skills = [] if pd.isna(skills) else [skills]
        
        for skill in skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Convert to DataFrame for plotting
    skill_df = pd.DataFrame({
        'Skill': list(skill_counts.keys()),
        'Count': list(skill_counts.values())
    })
    
    # Sort by count
    skill_df = skill_df.sort_values('Count', ascending=False)
    
    # Take top 20 skills
    skill_df = skill_df.head(20)
    
    # Create bar chart
    fig = px.bar(
        skill_df,
        x='Skill',
        y='Count',
        title="Top Skills Distribution",
        color='Count',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(xaxis_tickangle=45)
    
    return fig

def plot_department_distribution(employees=None):
    """
    Create a pie chart showing the distribution of employees across departments
    
    Parameters:
    - employees: DataFrame of employees (default: all employees in session state)
    
    Returns:
    - Plotly figure
    """
    if employees is None:
        employees = st.session_state.employees
    
    # Count employees by department
    dept_counts = employees['department'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Count']
    
    # Create pie chart
    fig = px.pie(
        dept_counts,
        values='Count',
        names='Department',
        title="Employee Distribution by Department",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def plot_skill_gap_analysis(match_data):
    """
    Create a bar chart showing skill gaps for a specific match
    
    Parameters:
    - match_data: Dictionary with match data including skill gaps
    
    Returns:
    - Plotly figure
    """
    # Extract skill gaps
    skill_gaps = match_data.get('skill_gaps', {})
    missing_required = skill_gaps.get('missing_required', [])
    missing_preferred = skill_gaps.get('missing_preferred', [])
    
    # Create DataFrame for plotting
    gap_data = []
    
    for skill in missing_required:
        gap_data.append({
            'Skill': skill,
            'Type': 'Required',
            'Importance': 1
        })
    
    for skill in missing_preferred:
        gap_data.append({
            'Skill': skill,
            'Type': 'Preferred',
            'Importance': 0.5
        })
    
    if not gap_data:
        # No skill gaps, create a figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No skill gaps identified!",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(title="Skill Gap Analysis")
        return fig
    
    gap_df = pd.DataFrame(gap_data)
    
    # Sort by importance
    gap_df = gap_df.sort_values(['Importance', 'Skill'], ascending=[False, True])
    
    # Create horizontal bar chart
    fig = px.bar(
        gap_df,
        y='Skill',
        x='Importance',
        color='Type',
        title="Skill Gap Analysis",
        orientation='h',
        color_discrete_map={
            'Required': 'rgba(239, 85, 59, 0.8)',
            'Preferred': 'rgba(99, 110, 250, 0.8)'
        },
        category_orders={"Type": ["Required", "Preferred"]}
    )
    
    fig.update_layout(
        xaxis_title="Importance",
        yaxis_title="Missing Skills"
    )
    
    return fig

def plot_hiring_needs_forecast(roles=None):
    """
    Create a bar chart showing projected hiring needs based on role requirements
    and current employee matches
    
    Parameters:
    - roles: DataFrame of roles (default: all roles in session state)
    
    Returns:
    - Plotly figure
    """
    if roles is None:
        roles = st.session_state.roles
    
    # This is a simple model that assumes each role needs to be filled
    # In a real application, you would use more sophisticated forecasting
    
    # Count roles by department
    dept_counts = roles['department'].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Open Positions']
    
    # Create bar chart
    fig = px.bar(
        dept_counts,
        x='Department',
        y='Open Positions',
        title="Projected Hiring Needs by Department",
        color='Open Positions',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(xaxis_tickangle=45)
    
    return fig

def plot_match_history_trend(matches=None):
    """
    Create a line chart showing match scores over time
    
    Parameters:
    - matches: DataFrame of matches (default: all matches in session state)
    
    Returns:
    - Plotly figure
    """
    if matches is None:
        matches = st.session_state.matches
    
    # If no matches, create an empty figure with a message
    if len(matches) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No match history available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(title="Match Score Trend")
        return fig
    
    # Convert match_date to datetime if not already
    if 'match_date' in matches.columns:
        matches['match_date'] = pd.to_datetime(matches['match_date'])
        
        # Sort by date
        matches = matches.sort_values('match_date')
        
        # Create line chart
        fig = px.line(
            matches,
            x='match_date',
            y='match_score',
            title="Match Score Trend Over Time",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Match Score"
        )
    else:
        # If no match_date column, create an aggregated view
        # Group by some other field (e.g., employee_id)
        avg_scores = matches.groupby('employee_id')['match_score'].mean().reset_index()
        avg_scores = avg_scores.sort_values('match_score', ascending=False)
        
        fig = px.bar(
            avg_scores,
            x='employee_id',
            y='match_score',
            title="Average Match Scores by Employee",
            color='match_score',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig.update_layout(
            xaxis_title="Employee ID",
            yaxis_title="Average Match Score"
        )
    
    return fig
