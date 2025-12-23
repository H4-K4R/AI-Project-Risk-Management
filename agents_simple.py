"""
Windows-Compatible Simplified Agent System
AI-Powered Project Risk & Resource Management
 
# Aligns with AI4SE Phase 2: Data Modeling & Analysis
# Aligns with AI4SE Phase 12: Resource Planning & Optimization
"""
 
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from llm_client import LLMClient
 
 
def calculate_project_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate deterministic project metrics (fast, always works).
    This is the foundation that AutoGen agents will analyze.
   
    # Aligns with AI4SE Phase 2: Data Modeling & Analysis
    """
    # === RISK ANALYSIS ===
    high_risk_tasks = df[df['Risk_Level'] == 'High']
    med_risk_tasks = df[df['Risk_Level'] == 'Med']
    low_risk_tasks = df[df['Risk_Level'] == 'Low']
   
    # Calculate complexity based on dependencies
    df['Complexity'] = df['Predecessors'].apply(
        lambda x: len(str(x).split(',')) if pd.notna(x) and str(x).strip() else 0
    )
    complex_tasks = df[df['Complexity'] > 1]
   
    # === RESOURCE STATISTICS ===
    resource_stats = df.groupby('Resource_Name').agg({
        'Task_ID': 'count',
        'Duration_Days': 'sum',
        'Cost_Per_Day': 'first'
    }).reset_index()
   
    resource_stats.columns = ['Resource', 'Task_Count', 'Total_Days', 'Cost_Per_Day']
    resource_stats['Total_Cost'] = resource_stats['Total_Days'] * resource_stats['Cost_Per_Day']
   
    # Calculate workload distribution
    avg_tasks = resource_stats['Task_Count'].mean()
    avg_days = resource_stats['Total_Days'].mean()
   
    overloaded = resource_stats[resource_stats['Task_Count'] > avg_tasks * 1.5]
    underutilized = resource_stats[resource_stats['Task_Count'] < avg_tasks * 0.5]
   
    # === PROJECT SUMMARY ===
    total_duration = df['Duration_Days'].sum()
    total_cost = (df['Duration_Days'] * df['Cost_Per_Day']).sum()
   
    return {
        'dataframe': df,
        'total_tasks': len(df),
        'total_duration': total_duration,
        'total_cost': total_cost,
        'num_resources': df['Resource_Name'].nunique(),
        'num_dependencies': len(df[df['Predecessors'].notna()]),
        'num_independent': len(df[df['Predecessors'].isna()]),
        'high_risk_count': len(high_risk_tasks),
        'med_risk_count': len(med_risk_tasks),
        'low_risk_count': len(low_risk_tasks),
        'complex_task_count': len(complex_tasks),
        'resource_stats': resource_stats,
        'avg_tasks_per_resource': avg_tasks,
        'avg_days_per_resource': avg_days,
        'overloaded_resources': overloaded,
        'underutilized_resources': underutilized,
        'high_risk_tasks': high_risk_tasks,
        'med_risk_tasks': med_risk_tasks,
        'low_risk_tasks': low_risk_tasks,
        'complex_tasks': complex_tasks
    }
 
 
def analyze_project(csv_file_path: str, *, use_llm: bool = True, use_autogen: bool = True) -> Dict[str, Any]:
    """
    Analyze project data using hybrid approach:
    1. Calculate metrics (deterministic, fast)
    2. Use AutoGen multi-agent system for deep analysis (if available)
    3. Fallback to simple LLM if AutoGen unavailable
   
    # Aligns with AI4SE Phase 9: Multi-Agent Architecture
   
    Args:
        csv_file_path: Path to the project CSV file
        use_llm: Whether to use LLM for additional insights
        use_autogen: Whether to use AutoGen multi-agent system
       
    Returns:
        Dictionary containing analysis results
    """
    try:
        # === STEP 1: CALCULATE METRICS (Always works) ===
        print("\\n" + "="*60)
        print("📊 STEP 1: Calculating Project Metrics...")
        print("="*60)
       
        df = pd.read_csv(csv_file_path)
        metrics = calculate_project_metrics(df)
       
        print(f"✅ Metrics calculated: {metrics['total_tasks']} tasks, {metrics['num_resources']} resources")
       
        # === STEP 2: TRY AUTOGEN MULTI-AGENT ANALYSIS ===
        autogen_analysis = None
        if use_autogen:
            try:
                print("\\n" + "="*60)
                print("🤖 STEP 2: Running AutoGen Multi-Agent Analysis...")
                print("="*60)
               
                from agents_autogen import ProjectManagementAgents
                agents = ProjectManagementAgents()
                autogen_result = agents.analyze_with_metrics(metrics)
                autogen_analysis = autogen_result
                print("✅ AutoGen analysis complete!")
               
            except ImportError:
                print("⚠️  AutoGen not installed. Install with: pip install pyautogen")
            except Exception as e:
                print(f"⚠️  AutoGen analysis failed: {str(e)}")
       
        # === STEP 3: FALLBACK TO SIMPLE LLM (if AutoGen failed) ===
        simple_llm_analysis = None
        if not autogen_analysis and use_llm:
            print("\\n" + "="*60)
            print("🔄 STEP 3: Fallback to Simple LLM Analysis...")
            print("="*60)
           
            client = LLMClient()
            if client.available():
                prompt = (
                    "You are an AI project analyst. Provide a comprehensive project analysis.\\n\\n"
                    f"DATA TO ANALYZE:\\n"
                    f"Total Tasks: {metrics['total_tasks']}\\n"
                    f"Total Duration: {metrics['total_duration']} days\\n"
                    f"Total Budget: ${metrics['total_cost']:,.2f}\\n"
                    f"Resources: {metrics['num_resources']}\\n"
                    f"Dependencies: {metrics['num_dependencies']}\\n\\n"
                    f"RISK: High={metrics['high_risk_count']}, Med={metrics['med_risk_count']}, Low={metrics['low_risk_count']}\\n"
                    f"Complex tasks: {metrics['complex_task_count']}\\n\\n"
                    f"RESOURCES:\\n{metrics['resource_stats'].to_string(index=False)}\\n\\n"
                    "Provide detailed analysis with actionable recommendations."
                )
                simple_llm_analysis = client.generate(prompt, max_tokens=800, temperature=0.3)
                print("✅ Simple LLM analysis complete!")
       
        # === BUILD FINAL REPORT ===
        final_output = build_report(metrics, autogen_analysis, simple_llm_analysis)
       
        return {
            'status': 'success',
            'analysis_results': final_output,
            'metrics': metrics,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
       
    except FileNotFoundError:
        return {
            'status': 'error',
            'error_message': f'File not found: {csv_file_path}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'status': 'error',
            'error_message': f'Analysis failed: {str(e)}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
 
 
def build_report(metrics: Dict, autogen_analysis: Optional[str], simple_analysis: Optional[str]) -> str:
    """Build the final analysis report combining all sources."""
   
    header = f"""
╔═══════════════════════════════════════════════════════════════╗
║   AI-POWERED PROJECT RISK & RESOURCE MANAGEMENT ANALYSIS      ║
║   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚═══════════════════════════════════════════════════════════════╝
"""
   
    # Always show metrics summary
    metrics_section = f"""
📊 PROJECT METRICS SUMMARY
═══════════════════════════════════════════════════════════════
Total Tasks: {metrics['total_tasks']}
Total Duration: {metrics['total_duration']} days
Total Budget: ${metrics['total_cost']:,.2f}
Resources: {metrics['num_resources']}
Dependencies: {metrics['num_dependencies']}
 
Risk Distribution:
  • High Risk: {metrics['high_risk_count']} tasks ({metrics['high_risk_count']/metrics['total_tasks']*100:.1f}%)
  • Medium Risk: {metrics['med_risk_count']} tasks ({metrics['med_risk_count']/metrics['total_tasks']*100:.1f}%)
  • Low Risk: {metrics['low_risk_count']} tasks ({metrics['low_risk_count']/metrics['total_tasks']*100:.1f}%)
 
Complex Dependencies: {metrics['complex_task_count']} tasks
Overloaded Resources: {len(metrics['overloaded_resources'])}
Underutilized Resources: {len(metrics['underutilized_resources'])}
═══════════════════════════════════════════════════════════════
"""
   
    # Add AutoGen analysis if available
    if autogen_analysis:
        ai_section = f"""
{autogen_analysis}
"""
    elif simple_analysis:
        ai_section = f"""
🤖 AI ANALYSIS (Single LLM)
═══════════════════════════════════════════════════════════════
{simple_analysis}
═══════════════════════════════════════════════════════════════
"""
    else:
        ai_section = """
⚠️  AI ANALYSIS NOT AVAILABLE
═══════════════════════════════════════════════════════════════
LLM integration is not configured. To enable:
1. Get a free token from https://huggingface.co/settings/tokens
2. Add to .env file: HF_API_TOKEN=hf_your_token_here
3. Install AutoGen: pip install pyautogen
═══════════════════════════════════════════════════════════════
"""
   
    footer = f"""
Analysis Mode: {'✅ AutoGen Multi-Agent' if autogen_analysis else '✅ Simple LLM' if simple_analysis else '⚠️  Metrics Only'}
═══════════════════════════════════════════════════════════════
"""
   
    return header + metrics_section + ai_section + footer
 
 
if __name__ == "__main__":
    # Test the hybrid analysis system
    print("Testing Hybrid Project Management Analysis...")
    results = analyze_project("dummy_data.csv")
    print("\n" + "="*50)
    print("ANALYSIS RESULTS:")
    print("="*50)
    print(results['analysis_results'])
 
 