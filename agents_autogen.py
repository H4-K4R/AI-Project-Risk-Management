"""
AutoGen-Based Multi-Agent System
AI-Powered Project Risk & Resource Management
 
# Aligns with AI4SE Phase 9: Multi-Agent Architecture
# Aligns with AI4SE Phase 2: Data Modeling & Analysis
# Aligns with AI4SE Phase 12: Resource Planning & Optimization
"""
 
import os
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
 
load_dotenv()
 
 
class ProjectManagementAgents:
    """
    Multi-Agent System for Project Risk & Resource Management.
    Uses AutoGen to orchestrate 3 specialized agents:
    1. Risk Analysis Agent
    2. Resource Optimization Agent  
    3. Decision Synthesis Agent
    """
   
    def __init__(self):
        # Configure LLM for HuggingFace
        self.llm_config = {
            "config_list": [
                {
                    "model": os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"),
                    "base_url": "https://router.huggingface.co/v1",
                    "api_key": os.getenv("HF_API_TOKEN"),
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            ],
            "timeout": 120,
        }
       
        # Initialize agents
        self.risk_agent = self._create_risk_agent()
        self.resource_agent = self._create_resource_agent()
        self.decision_agent = self._create_decision_agent()
        self.user_proxy = self._create_user_proxy()
       
    def _create_risk_agent(self) -> AssistantAgent:
        """Create Risk Analysis Agent"""
        return AssistantAgent(
            name="RiskAnalyst",
            system_message="""
            You are a Senior Project Risk Analyst with expertise in identifying and assessing project risks.
           
            Your responsibilities:
            - Analyze task dependencies and identify bottlenecks
            - Assess risk levels (High/Medium/Low) and their impact
            - Identify complex dependencies that may cause delays
            - Predict potential failure points in the project timeline
            - Calculate overall risk scores
           
            Provide concise, data-driven risk assessments with specific metrics.
            Focus on actionable insights.
            """,
            llm_config=self.llm_config,
        )
   
    def _create_resource_agent(self) -> AssistantAgent:
        """Create Resource Optimization Agent"""
        return AssistantAgent(
            name="ResourceOptimizer",
            system_message="""
            You are a Resource Planning and Optimization Specialist.
           
            Your responsibilities:
            - Analyze resource allocation and workload distribution
            - Identify overloaded and underutilized resources
            - Calculate cost breakdowns and budget impacts
            - Suggest resource reallocation strategies
            - Optimize task assignments to minimize project duration
           
            Provide specific recommendations with quantitative justifications.
            Focus on cost-effectiveness and efficiency.
            """,
            llm_config=self.llm_config,
        )
   
    def _create_decision_agent(self) -> AssistantAgent:
        """Create Decision Synthesis Agent"""
        return AssistantAgent(
            name="DecisionSynthesizer",
            system_message="""
            You are a Project Management Decision Advisor.
           
            Your responsibilities:
            - Synthesize insights from Risk and Resource analyses
            - Generate comprehensive project recommendations
            - Prioritize actions based on impact and urgency
            - Create executive summaries for stakeholders
            - Provide clear next steps and success criteria
           
            Deliver well-structured, actionable decision support.
            Balance risk mitigation with resource optimization.
            """,
            llm_config=self.llm_config,
        )
   
    def _create_user_proxy(self) -> UserProxyAgent:
        """Create User Proxy for interaction"""
        return UserProxyAgent(
            name="ProjectManager",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
   
    def analyze_with_metrics(self, metrics: Dict) -> str:
        """
        Analyze project using pre-calculated metrics.
        This is called by agents_simple.py hybrid system.
        """
        analysis_prompt = f"""
Analyze this project management scenario:
 
PROJECT OVERVIEW:
- Total Tasks: {metrics['total_tasks']}
- Total Duration: {metrics['total_duration']} days
- Total Budget: ${metrics['total_cost']:,.2f}
- Resources: {metrics['num_resources']}
- Tasks with Dependencies: {metrics['num_dependencies']}
 
RISK DISTRIBUTION:
- High Risk: {metrics['high_risk_count']} tasks ({metrics['high_risk_count']/metrics['total_tasks']*100:.1f}%)
- Medium Risk: {metrics['med_risk_count']} tasks ({metrics['med_risk_count']/metrics['total_tasks']*100:.1f}%)
- Low Risk: {metrics['low_risk_count']} tasks ({metrics['low_risk_count']/metrics['total_tasks']*100:.1f}%)
- Complex Dependencies (>1 predecessor): {metrics['complex_task_count']} tasks
 
RESOURCE INDICATORS:
- Overloaded Resources (>150% avg workload): {len(metrics['overloaded_resources'])}
- Underutilized Resources (<50% avg workload): {len(metrics['underutilized_resources'])}
 
TASK: Provide comprehensive analysis from your specialized perspective.
"""
       
        return self._run_agent_workflow(analysis_prompt)
   
    def analyze_project(self, csv_file_path: str) -> Dict[str, Any]:
        """
        Run multi-agent analysis on project data.
       
        Args:
            csv_file_path: Path to project CSV file
           
        Returns:
            Dictionary with analysis results from all agents
        """
        try:
            # Load and process project data
            df = pd.read_csv(csv_file_path)
           
            # Calculate key metrics
            metrics = self._calculate_metrics(df)
           
            # Prepare analysis prompt
            analysis_prompt = self._prepare_analysis_prompt(df, metrics)
           
            # Run multi-agent conversation
            print("\n" + "="*60)
            print("🤖 Starting Multi-Agent Analysis...")
            print("="*60)
           
            results = self._run_agent_workflow(analysis_prompt)
           
            return {
                'status': 'success',
                'analysis_results': results,
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
   
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate project metrics for agent analysis"""
        # Risk analysis
        high_risk = df[df['Risk_Level'] == 'High']
        med_risk = df[df['Risk_Level'] == 'Med']
        low_risk = df[df['Risk_Level'] == 'Low']
       
        # Complexity
        df['Complexity'] = df['Predecessors'].apply(
            lambda x: len(str(x).split(',')) if pd.notna(x) and str(x).strip() else 0
        )
        complex_tasks = df[df['Complexity'] > 1]
       
        # Resource stats
        resource_stats = df.groupby('Resource_Name').agg({
            'Task_ID': 'count',
            'Duration_Days': 'sum',
            'Cost_Per_Day': 'first'
        }).reset_index()
        resource_stats.columns = ['Resource', 'Task_Count', 'Total_Days', 'Cost_Per_Day']
        resource_stats['Total_Cost'] = resource_stats['Total_Days'] * resource_stats['Cost_Per_Day']
       
        avg_tasks = resource_stats['Task_Count'].mean()
        overloaded = resource_stats[resource_stats['Task_Count'] > avg_tasks * 1.5]
        underutilized = resource_stats[resource_stats['Task_Count'] < avg_tasks * 0.5]
       
        return {
            'total_tasks': len(df),
            'total_duration': df['Duration_Days'].sum(),
            'total_cost': (df['Duration_Days'] * df['Cost_Per_Day']).sum(),
            'resources': df['Resource_Name'].nunique(),
            'dependencies': len(df[df['Predecessors'].notna()]),
            'high_risk_count': len(high_risk),
            'med_risk_count': len(med_risk),
            'low_risk_count': len(low_risk),
            'complex_tasks_count': len(complex_tasks),
            'overloaded_resources': len(overloaded),
            'underutilized_resources': len(underutilized),
            'resource_breakdown': resource_stats.to_dict('records')
        }
   
    def _prepare_analysis_prompt(self, df: pd.DataFrame, metrics: Dict) -> str:
        """Prepare comprehensive prompt for agents"""
        return f"""
        Analyze this project management scenario:
       
        PROJECT OVERVIEW:
        - Total Tasks: {metrics['total_tasks']}
        - Total Duration: {metrics['total_duration']} days
        - Total Budget: ${metrics['total_cost']:,.2f}
        - Resources: {metrics['resources']}
        - Tasks with Dependencies: {metrics['dependencies']}
       
        RISK DISTRIBUTION:
        - High Risk: {metrics['high_risk_count']} tasks ({metrics['high_risk_count']/metrics['total_tasks']*100:.1f}%)
        - Medium Risk: {metrics['med_risk_count']} tasks ({metrics['med_risk_count']/metrics['total_tasks']*100:.1f}%)
        - Low Risk: {metrics['low_risk_count']} tasks ({metrics['low_risk_count']/metrics['total_tasks']*100:.1f}%)
        - Complex Dependencies (>1 predecessor): {metrics['complex_tasks_count']} tasks
       
        RESOURCE INDICATORS:
        - Overloaded Resources (>150% avg workload): {metrics['overloaded_resources']}
        - Underutilized Resources (<50% avg workload): {metrics['underutilized_resources']}
       
        TASK: Provide comprehensive analysis from your specialized perspective.
        """
   
    def _run_agent_workflow(self, prompt: str) -> str:
        """Execute multi-agent workflow with sequential analysis"""
        results = []
       
        # Step 1: Risk Analysis
        try:
            print("\n🔴 Risk Analyst analyzing...")
            risk_response = self.risk_agent.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            if risk_response:
                results.append(f"\n{'='*60}\n🔴 RISK ANALYSIS\n{'='*60}\n{risk_response}")
        except Exception as e:
            results.append(f"\n⚠️ Risk Analysis unavailable: {str(e)}")
       
        # Step 2: Resource Optimization
        try:
            print("\n👥 Resource Optimizer analyzing...")
            resource_response = self.resource_agent.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            if resource_response:
                results.append(f"\n{'='*60}\n👥 RESOURCE OPTIMIZATION\n{'='*60}\n{resource_response}")
        except Exception as e:
            results.append(f"\n⚠️ Resource Analysis unavailable: {str(e)}")
       
        # Step 3: Decision Synthesis
        try:
            print("\n💡 Decision Synthesizer consolidating...")
            synthesis_prompt = f"""
            Based on the following analyses, provide executive recommendations:
           
            CONTEXT: {prompt}
           
            Synthesize insights and provide:
            1. Top 3 Critical Actions
            2. Risk Mitigation Priorities
            3. Resource Optimization Strategy
            4. Expected Outcomes
            """
            decision_response = self.decision_agent.generate_reply(
                messages=[{"role": "user", "content": synthesis_prompt}]
            )
            if decision_response:
                results.append(f"\n{'='*60}\n💡 EXECUTIVE RECOMMENDATIONS\n{'='*60}\n{decision_response}")
        except Exception as e:
            results.append(f"\n⚠️ Decision Synthesis unavailable: {str(e)}")
       
        # Combine all results
        if results:
            final_report = f"""
╔═══════════════════════════════════════════════════════════════╗
║   MULTI-AGENT PROJECT ANALYSIS REPORT                         ║
║   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
║   System: AutoGen Multi-Agent Framework                       ║
╚═══════════════════════════════════════════════════════════════╝
 
{''.join(results)}
 
═══════════════════════════════════════════════════════════════
Multi-Agent Analysis Complete | AutoGen Framework Active
═══════════════════════════════════════════════════════════════
"""
            return final_report
        else:
            return """
⚠️ MULTI-AGENT ANALYSIS UNAVAILABLE
 
The multi-agent system could not complete the analysis.
Please check:
1. HF_API_TOKEN is set in .env
2. HuggingFace API is accessible
3. Model is available (current: meta-llama/Meta-Llama-3-8B-Instruct)
"""
 
 
def analyze_project(csv_file_path: str, *, use_llm: bool = True) -> Dict[str, Any]:
    """
    Main entry point for project analysis using AutoGen multi-agent system.
   
    Args:
        csv_file_path: Path to the project CSV file
        use_llm: Whether to use LLM agents (requires HF_API_TOKEN)
       
    Returns:
        Dictionary containing analysis results
    """
    if not use_llm or not os.getenv("HF_API_TOKEN"):
        # Fallback to simple analysis
        from agents_simple import analyze_project as simple_analyze
        return simple_analyze(csv_file_path, use_llm=False)
   
    # Use AutoGen multi-agent system
    agents = ProjectManagementAgents()
    return agents.analyze_project(csv_file_path)
 
 
if __name__ == "__main__":
    # Test the multi-agent system
    print("Testing AutoGen Multi-Agent System...")
    results = analyze_project("dummy_data.csv")
    print("\n" + "="*50)
    print("ANALYSIS RESULTS:")
    print("="*50)
    if results['status'] == 'success':
        print(results['analysis_results'])
    else:
        print(f"Error: {results['error_message']}")
 
 
