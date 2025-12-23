import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional
import os
import tempfile
from dotenv import load_dotenv
 
# Load environment variables from .env file
load_dotenv()
 
# Import the agent systems
try:
    from agents_autogen import analyze_project
    AGENT_SYSTEM = "AutoGen Multi-Agent"
except ImportError:
    from agents_simple import analyze_project
    AGENT_SYSTEM = "Simple Heuristic"
 
 
# Page Configuration
# Aligns with AI4SE Phase 17: UX Design for AI Systems
st.set_page_config(
    page_title="AI Project Risk & Resource Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)
 
 
def calculate_gantt_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate start and finish dates for Gantt chart visualization.
   
    # Aligns with AI4SE Phase 4: Temporal Data Processing
   
    Args:
        df: DataFrame with project data
       
    Returns:
        DataFrame with Start and Finish datetime columns
    """
    # Create a copy to avoid modifying original
    gantt_df = df.copy()
   
    # Initialize start dates dictionary
    task_dates = {}
   
    # Base start date (today)
    project_start = datetime.now()
   
    for idx, row in gantt_df.iterrows():
        task_id = row['Task_ID']
        duration = row['Duration_Days']
        predecessors = row['Predecessors']
       
        # Calculate start date based on predecessors
        if pd.isna(predecessors) or predecessors == '':
            start_date = project_start
        else:
            # Get predecessor task IDs
            pred_ids = [int(p.strip()) for p in str(predecessors).split(',')]
            # Start after all predecessors finish
            pred_finish_dates = [task_dates.get(pid, {}).get('finish', project_start)
                                for pid in pred_ids if pid in task_dates]
            start_date = max(pred_finish_dates) if pred_finish_dates else project_start
       
        finish_date = start_date + timedelta(days=duration)
       
        task_dates[task_id] = {
            'start': start_date,
            'finish': finish_date
        }
   
    # Add dates to dataframe
    gantt_df['Start'] = gantt_df['Task_ID'].map(lambda x: task_dates[x]['start'])
    gantt_df['Finish'] = gantt_df['Task_ID'].map(lambda x: task_dates[x]['finish'])
   
    return gantt_df
 
 
def create_gantt_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create an interactive Gantt chart using Plotly.
   
    # Aligns with AI4SE Phase 18: Interactive Visualization Design
   
    Args:
        df: DataFrame with project data including Start and Finish dates
       
    Returns:
        Plotly figure object
    """
    # Calculate dates
    gantt_df = calculate_gantt_dates(df)
   
    # Color mapping for risk levels
    risk_colors = {
        'High': '#d62728',    # Red
        'Med': '#ff7f0e',     # Orange
        'Low': '#2ca02c'      # Green
    }
   
    gantt_df['Color'] = gantt_df['Risk_Level'].map(risk_colors)
   
    # Create Gantt chart using px.timeline
    fig = px.timeline(
        gantt_df,
        x_start='Start',
        x_end='Finish',
        y='Task_Name',
        color='Risk_Level',
        color_discrete_map=risk_colors,
        hover_data={
            'Task_ID': True,
            'Resource_Name': True,
            'Duration_Days': True,
            'Cost_Per_Day': True,
            'Predecessors': True,
            'Start': '|%Y-%m-%d',
            'Finish': '|%Y-%m-%d'
        },
        title='Project Schedule - Interactive Gantt Chart'
    )
   
    # Update layout
    fig.update_layout(
        height=600,
        xaxis_title='Timeline',
        yaxis_title='Tasks',
        showlegend=True,
        legend_title_text='Risk Level',
        hovermode='closest'
    )
   
    # Update y-axis to show tasks in order
    fig.update_yaxes(categoryorder='total ascending')
   
    return fig
 
 
def create_resource_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create resource utilization bar chart.
   
    # Aligns with AI4SE Phase 19: Resource Metrics Visualization
   
    Args:
        df: DataFrame with project data
       
    Returns:
        Plotly figure object
    """
    resource_stats = df.groupby('Resource_Name').agg({
        'Task_ID': 'count',
        'Duration_Days': 'sum',
        'Cost_Per_Day': 'first'
    }).reset_index()
   
    resource_stats.columns = ['Resource', 'Task_Count', 'Total_Days', 'Cost_Per_Day']
    resource_stats['Total_Cost'] = resource_stats['Total_Days'] * resource_stats['Cost_Per_Day']
   
    fig = go.Figure()
   
    fig.add_trace(go.Bar(
        x=resource_stats['Resource'],
        y=resource_stats['Task_Count'],
        name='Number of Tasks',
        marker_color='#1f77b4',
        yaxis='y',
        offsetgroup=1
    ))
   
    fig.add_trace(go.Bar(
        x=resource_stats['Resource'],
        y=resource_stats['Total_Days'],
        name='Total Days',
        marker_color='#ff7f0e',
        yaxis='y2',
        offsetgroup=2
    ))
   
    fig.update_layout(
        title='Resource Workload Distribution',
        xaxis_title='Resource',
        yaxis=dict(title='Number of Tasks', side='left'),
        yaxis2=dict(title='Total Days', side='right', overlaying='y'),
        barmode='group',
        height=400,
        showlegend=True
    )
   
    return fig
 
 
def create_risk_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create risk level distribution pie chart.
   
    # Aligns with AI4SE Phase 7: Risk Visualization
   
    Args:
        df: DataFrame with project data
       
    Returns:
        Plotly figure object
    """
    risk_counts = df['Risk_Level'].value_counts()
   
    colors = ['#d62728', '#ff7f0e', '#2ca02c']  # Red, Orange, Green
   
    fig = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker_colors=colors,
        hole=0.3
    )])
   
    fig.update_layout(
        title='Risk Level Distribution',
        height=400
    )
   
    return fig
 
 
def display_project_metrics(df: pd.DataFrame):
    """
    Display key project metrics in columns.
   
    # Aligns with AI4SE Phase 20: Dashboard KPI Design
   
    Args:
        df: DataFrame with project data
    """
    col1, col2, col3, col4 = st.columns(4)
   
    with col1:
        st.metric(
            label="📋 Total Tasks",
            value=len(df)
        )
   
    with col2:
        total_duration = df['Duration_Days'].sum()
        st.metric(
            label="⏱️ Total Duration",
            value=f"{total_duration} days"
        )
   
    with col3:
        total_cost = (df['Duration_Days'] * df['Cost_Per_Day']).sum()
        st.metric(
            label="💰 Total Cost",
            value=f"${total_cost:,.2f}"
        )
   
    with col4:
        high_risk_count = len(df[df['Risk_Level'] == 'High'])
        st.metric(
            label="⚠️ High Risk Tasks",
            value=high_risk_count,
            delta="Critical" if high_risk_count > 0 else "None"
        )
 
 
def main():
    """
    Main Streamlit application.
   
    # Aligns with AI4SE Phase 21: End-to-End System Integration
    """
   
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Powered Project Risk & Resource Manager</h1>',
                unsafe_allow_html=True)
   
    # Sidebar
    st.sidebar.title("📁 Data Upload")
    st.sidebar.markdown("""
    <div class="info-box">
    <b>Expected CSV Format:</b><br>
    • Task_ID<br>
    • Task_Name<br>
    • Duration_Days<br>
    • Resource_Name<br>
    • Cost_Per_Day<br>
    • Predecessors<br>
    • Risk_Level (Low/Med/High)
    </div>
    """, unsafe_allow_html=True)
   
    # File uploader
    uploaded_file = st.sidebar.file_uploader(
        "Upload Project Schedule (CSV)",
        type=['csv'],
        help="Upload a CSV file with your project schedule data"
    )
   
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'df' not in st.session_state:
        st.session_state.df = None
   
    # Load data
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
           
            st.sidebar.success("✅ File uploaded successfully!")
           
            # Display data preview in sidebar
            st.sidebar.markdown("### 👀 Data Preview")
            st.sidebar.dataframe(df.head(3), use_container_width=True)
           
        except Exception as e:
            st.sidebar.error(f"❌ Error loading file: {str(e)}")
            return
   
    # Main content area
    if st.session_state.df is not None:
        df = st.session_state.df
       
        # Display project metrics
        st.markdown("## 📊 Project Overview")
        display_project_metrics(df)
       
        st.markdown("---")
       
        # Visualization tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 Gantt Chart",
            "👥 Resource Analysis",
            "⚠️ Risk Distribution",
            "🤖 AI Agent Analysis"
        ])
       
        with tab1:
            st.markdown("### Interactive Project Timeline")
            st.markdown("""
            <div class="info-box">
            <b>Features:</b> Hover over tasks for details. Color-coded by risk level.
            </div>
            """, unsafe_allow_html=True)
           
            gantt_fig = create_gantt_chart(df)
            st.plotly_chart(gantt_fig, use_container_width=True)
       
        with tab2:
            st.markdown("### Resource Workload Analysis")
            resource_fig = create_resource_chart(df)
            st.plotly_chart(resource_fig, use_container_width=True)
           
            # Resource details table
            st.markdown("#### 📋 Detailed Resource Breakdown")
            resource_detail = df.groupby('Resource_Name').agg({
                'Task_ID': 'count',
                'Duration_Days': 'sum',
                'Cost_Per_Day': 'first'
            }).reset_index()
            resource_detail.columns = ['Resource', 'Tasks', 'Total Days', 'Cost/Day']
            resource_detail['Total Cost'] = resource_detail['Total Days'] * resource_detail['Cost/Day']
            st.dataframe(resource_detail, use_container_width=True)
       
        with tab3:
            st.markdown("### Risk Level Distribution")
            risk_fig = create_risk_distribution_chart(df)
            st.plotly_chart(risk_fig, use_container_width=True)
           
            # High risk tasks table
            high_risk_tasks = df[df['Risk_Level'] == 'High']
            if len(high_risk_tasks) > 0:
                st.markdown("#### ⚠️ High Risk Tasks Requiring Attention")
                st.dataframe(high_risk_tasks[['Task_ID', 'Task_Name', 'Duration_Days',
                                               'Resource_Name', 'Predecessors']],
                           use_container_width=True)
            else:
                st.success("✅ No high-risk tasks identified!")
       
        with tab4:
            st.markdown("### 🤖 AI Multi-Agent Analysis")
            st.markdown("""
            <div class="info-box">
            <b>AI Agents:</b><br>
            • <b>Risk Agent:</b> Analyzes dependencies, identifies bottlenecks<br>
            • <b>Resource Agent:</b> Optimizes allocation, balances workload
            </div>
            """, unsafe_allow_html=True)
           
            # Analysis button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                run_analysis = st.button(
                    "🚀 Run AI Agent Analysis",
                    type="primary",
                    use_container_width=True
                )
           
            if run_analysis:
                with st.spinner("🔄 AI Agents are analyzing your project... This may take a moment."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                        df.to_csv(tmp_file.name, index=False)
                        tmp_path = tmp_file.name
                   
                    try:
                        # Run CrewAI analysis
                        # Aligns with AI4SE Phase 22: Agent Execution & Result Collection
                        results = analyze_project(tmp_path)
                        st.session_state.analysis_results = results
                       
                        # Clean up temp file
                        os.unlink(tmp_path)
                       
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        os.unlink(tmp_path)
           
            # Display results
            if st.session_state.analysis_results is not None:
                results = st.session_state.analysis_results
               
                if results['status'] == 'success':
                    st.markdown("""
                    <div class="success-box">
                    ✅ <b>Analysis Complete!</b> AI agents have finished analyzing your project.
                    </div>
                    """, unsafe_allow_html=True)
                   
                    # Timestamp and metadata
                    col_meta1, col_meta2 = st.columns([2, 1])
                    with col_meta1:
                        st.markdown(f"**📅 Generated:** {results['timestamp']}")
                    with col_meta2:
                        st.download_button(
                            label="📥 Download Report",
                            data=results['analysis_results'],
                            file_name=f"ai_analysis_{results['timestamp'].replace(':', '-').replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                   
                    st.markdown("---")
                   
                    # Parse and display the analysis report in a structured way
                    analysis_text = results['analysis_results']
                   
                    # Create tabs for different sections
                    analysis_tabs = st.tabs(["📊 Overview", "🔴 Risk Analysis", "👥 Resource Optimization", "💡 Recommendations"])
                   
                    with analysis_tabs[0]:
                        st.markdown("### 📊 Project Analysis Overview")
                       
                        # Extract metrics if available
                        if 'metrics' in results and results['metrics']:
                            metrics = results['metrics']
                           
                            # Display key metrics in columns
                            metric_cols = st.columns(4)
                            with metric_cols[0]:
                                st.metric("Total Tasks", metrics.get('total_tasks', 'N/A'))
                            with metric_cols[1]:
                                st.metric("Total Duration", f"{metrics.get('total_duration', 0)} days")
                            with metric_cols[2]:
                                total_cost = metrics.get('total_cost', 0)
                                st.metric("Total Budget", f"${total_cost:,.2f}" if isinstance(total_cost, (int, float)) else "N/A")
                            with metric_cols[3]:
                                st.metric("Resources", metrics.get('num_resources', 'N/A'))
                           
                            st.markdown("---")
                           
                            # Risk distribution
                            st.markdown("#### Risk Distribution")
                            risk_cols = st.columns(3)
                            with risk_cols[0]:
                                high_risk = metrics.get('high_risk_count', 0)
                                st.metric("🔴 High Risk", high_risk,
                                         delta="Critical" if high_risk > 0 else None,
                                         delta_color="inverse")
                            with risk_cols[1]:
                                st.metric("🟡 Medium Risk", metrics.get('med_risk_count', 0))
                            with risk_cols[2]:
                                st.metric("🟢 Low Risk", metrics.get('low_risk_count', 0))
                       
                        # Display full report in an expander
                        with st.expander("📄 View Complete Analysis Report", expanded=False):
                            st.text(analysis_text)
                   
                    with analysis_tabs[1]:
                        st.markdown("### 🔴 Risk Analysis")
                       
                        # Extract risk analysis section
                        risk_section = ""
                        if "RISK ANALYSIS" in analysis_text:
                            risk_start = analysis_text.find("RISK ANALYSIS")
                            risk_end = analysis_text.find("RESOURCE OPTIMIZATION")
                            if risk_end == -1:
                                risk_end = analysis_text.find("EXECUTIVE RECOMMENDATIONS")
                            if risk_end == -1:
                                risk_end = len(analysis_text)
                            risk_section = analysis_text[risk_start:risk_end]
                       
                        if risk_section:
                            # Display in formatted container
                            st.markdown(f"""
                            <div style="background-color: #fff3f3; padding: 1.5rem; border-radius: 0.5rem;
                                 border-left: 5px solid #dc3545; font-family: monospace; white-space: pre-wrap;">
                            {risk_section}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No specific risk analysis section found in the report.")
                   
                    with analysis_tabs[2]:
                        st.markdown("### 👥 Resource Optimization")
                       
                        # Extract resource optimization section
                        resource_section = ""
                        if "RESOURCE OPTIMIZATION" in analysis_text:
                            resource_start = analysis_text.find("RESOURCE OPTIMIZATION")
                            resource_end = analysis_text.find("EXECUTIVE RECOMMENDATIONS")
                            if resource_end == -1:
                                resource_end = analysis_text.find("═══════════════",
                                                                 analysis_text.find("RESOURCE OPTIMIZATION") + 100)
                            if resource_end == -1:
                                resource_end = len(analysis_text)
                            resource_section = analysis_text[resource_start:resource_end]
                       
                        if resource_section:
                            # Display in formatted container
                            st.markdown(f"""
                            <div style="background-color: #f3f9ff; padding: 1.5rem; border-radius: 0.5rem;
                                 border-left: 5px solid #007bff; font-family: monospace; white-space: pre-wrap;">
                            {resource_section}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No specific resource optimization section found in the report.")
                   
                    with analysis_tabs[3]:
                        st.markdown("### 💡 Executive Recommendations")
                       
                        # Extract recommendations section
                        recommendations_section = ""
                        if "EXECUTIVE RECOMMENDATIONS" in analysis_text or "RECOMMENDATIONS" in analysis_text:
                            rec_start = analysis_text.find("EXECUTIVE RECOMMENDATIONS")
                            if rec_start == -1:
                                rec_start = analysis_text.find("RECOMMENDATIONS")
                           
                            if rec_start != -1:
                                recommendations_section = analysis_text[rec_start:]
                       
                        if recommendations_section:
                            # Display in formatted container
                            st.markdown(f"""
                            <div style="background-color: #fffef3; padding: 1.5rem; border-radius: 0.5rem;
                                 border-left: 5px solid #ffc107; font-family: monospace; white-space: pre-wrap;">
                            {recommendations_section}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No specific recommendations section found in the report.")
                else:
                    st.error(f"❌ Error: {results.get('error_message', 'Unknown error')}")
   
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div class="info-box">
        <h3>👋 Welcome to the AI Project Risk & Resource Manager!</h3>
        <p>This intelligent system uses <b>Multi-Agent AI</b> powered by CrewAI to:</p>
        <ul>
            <li>🔍 Analyze project risks and dependencies</li>
            <li>📊 Optimize resource allocation</li>
            <li>📅 Visualize project timelines with interactive Gantt charts</li>
            <li>💡 Provide actionable recommendations</li>
        </ul>
        <p><b>Get started by uploading a CSV file in the sidebar! →</b></p>
        </div>
        """, unsafe_allow_html=True)
       
        # Sample data option
        st.markdown("### 🧪 Try with Sample Data")
        if st.button("📂 Load Sample Project Data", type="secondary"):
            try:
                sample_df = pd.read_csv("dummy_data.csv")
                st.session_state.df = sample_df
                st.rerun()
            except FileNotFoundError:
                st.warning("⚠️ Sample data file not found. Please upload your own CSV file.")
       
        # Instructions
        st.markdown("""
        ### 📋 CSV File Requirements
       
        Your CSV file should contain the following columns:
       
        | Column | Description | Example |
        |--------|-------------|---------|
        | **Task_ID** | Unique identifier | 1, 2, 3, ... |
        | **Task_Name** | Task description | "Design Phase", "Development" |
        | **Duration_Days** | Task duration | 5, 10, 15 |
        | **Resource_Name** | Assigned resource | "John Doe", "Team A" |
        | **Cost_Per_Day** | Daily cost | 500, 750, 1000 |
        | **Predecessors** | Dependent tasks | "1,2" or blank |
        | **Risk_Level** | Risk category | Low, Med, High |
        """)
   
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
    <small>
    AI-Powered Project Risk & Resource Manager | Built with CrewAI + Streamlit<br>
    University Project - Industrial Engineering & AI Systems
    </small>
    </div>
    """, unsafe_allow_html=True)
 
 
if __name__ == "__main__":
    main()
   
 
