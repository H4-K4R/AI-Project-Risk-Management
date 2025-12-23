"""
Unit tests for agents_autogen.py
Tests AutoGen multi-agent system functionality
"""
 
import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch, MagicMock, PropertyMock
import tempfile
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
 
@pytest.fixture
def sample_df():
    """Create sample project data"""
    return pd.DataFrame({
        'Task_ID': [1, 2, 3, 4, 5],
        'Task_Name': ['Task A', 'Task B', 'Task C', 'Task D', 'Task E'],
        'Duration_Days': [10, 15, 8, 12, 20],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
        'Cost_Per_Day': [500, 600, 500, 550, 600],
        'Risk_Level': ['High', 'Med', 'Low', 'High', 'Med'],
        'Predecessors': [None, '1', '1', '2,3', None]
    })
 
 
@pytest.fixture
def sample_csv(tmp_path, sample_df):
    """Create temporary CSV file"""
    csv_path = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_path, index=False)
    return str(csv_path)
 
 
@pytest.fixture
def sample_metrics():
    """Create sample metrics dictionary"""
    return {
        'total_tasks': 5,
        'total_duration': 65,
        'total_cost': 35000,
        'num_resources': 3,  # Match agents_autogen code
        'num_dependencies': 3,  # Match agents_autogen code
        'high_risk_count': 2,
        'med_risk_count': 2,
        'low_risk_count': 1,
        'complex_task_count': 1,
        'overloaded_resources': [],
        'underutilized_resources': [],
        'resource_breakdown': []
 
    }
 
 
def test_agents_autogen_import():
    """Test that agents_autogen module can be imported"""
    try:
        from Scripts import agents_autogen
        assert agents_autogen is not None
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token', 'HF_MODEL': 'test-model'})
@patch('agents_autogen.AssistantAgent')
@patch('agents_autogen.UserProxyAgent')
def test_project_management_agents_initialization(mock_user_proxy, mock_assistant):
    """Test ProjectManagementAgents initialization"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        agents = ProjectManagementAgents()
       
        assert agents is not None
        assert hasattr(agents, 'llm_config')
        assert hasattr(agents, 'risk_agent')
        assert hasattr(agents, 'resource_agent')
        assert hasattr(agents, 'decision_agent')
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_create_risk_agent(mock_assistant):
    """Test risk agent creation"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        mock_assistant.return_value = MagicMock()
        agents = ProjectManagementAgents()
       
        assert agents.risk_agent is not None
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_create_resource_agent(mock_assistant):
    """Test resource optimizer agent creation"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        mock_assistant.return_value = MagicMock()
        agents = ProjectManagementAgents()
       
        assert agents.resource_agent is not None
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_create_decision_agent(mock_assistant):
    """Test decision synthesizer agent creation"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        mock_assistant.return_value = MagicMock()
        agents = ProjectManagementAgents()
       
        assert agents.decision_agent is not None
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
@patch('agents_autogen.UserProxyAgent')
def test_llm_config_structure(mock_user_proxy, mock_assistant):
    """Test LLM configuration structure"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        agents = ProjectManagementAgents()
       
        assert 'config_list' in agents.llm_config
        assert len(agents.llm_config['config_list']) > 0
        assert 'timeout' in agents.llm_config
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_calculate_metrics(mock_assistant, sample_df):
    """Test _calculate_metrics method"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        agents = ProjectManagementAgents()
        metrics = agents._calculate_metrics(sample_df)
       
        assert 'total_tasks' in metrics
        assert 'total_duration' in metrics
        assert 'total_cost' in metrics
        assert 'resources' in metrics
        assert 'high_risk_count' in metrics
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_prepare_analysis_prompt(mock_assistant, sample_df):
    """Test _prepare_analysis_prompt method"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        agents = ProjectManagementAgents()
        metrics = agents._calculate_metrics(sample_df)
        prompt = agents._prepare_analysis_prompt(sample_df, metrics)
       
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'PROJECT OVERVIEW' in prompt
        assert 'RISK DISTRIBUTION' in prompt
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_analyze_with_metrics(mock_assistant, sample_metrics):
    """Test analyze_with_metrics method"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        # Mock agent responses
        mock_agent = MagicMock()
        mock_agent.generate_reply.return_value = "Mocked analysis response"
        mock_assistant.return_value = mock_agent
       
        agents = ProjectManagementAgents()
        result = agents.analyze_with_metrics(sample_metrics)
       
        assert isinstance(result, str)
        assert len(result) > 0
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_run_agent_workflow(mock_assistant):
    """Test _run_agent_workflow method"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        # Mock agent responses
        mock_agent = MagicMock()
        mock_agent.generate_reply.return_value = "Agent analysis"
        mock_assistant.return_value = mock_agent
       
        agents = ProjectManagementAgents()
        result = agents._run_agent_workflow("Test prompt")
       
        assert isinstance(result, str)
        assert "MULTI-AGENT PROJECT ANALYSIS REPORT" in result or "analysis" in result.lower()
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_analyze_project_success(mock_assistant, sample_csv):
    """Test analyze_project method with successful execution"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        mock_agent = MagicMock()
        mock_agent.generate_reply.return_value = "Analysis complete"
        mock_assistant.return_value = mock_agent
       
        agents = ProjectManagementAgents()
        result = agents.analyze_project(sample_csv)
       
        assert 'status' in result
        assert result['status'] == 'success'
        assert 'metrics' in result
        assert 'timestamp' in result
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_analyze_project_file_not_found(mock_assistant):
    """Test analyze_project with non-existent file"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        agents = ProjectManagementAgents()
        result = agents.analyze_project("nonexistent_file.csv")
       
        assert 'status' in result
        assert result['status'] == 'error'
        assert 'error_message' in result
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
def test_analyze_project_function_with_llm(sample_csv):
    """Test analyze_project convenience function with LLM"""
    try:
        from agents_autogen import analyze_project
       
        with patch('agents_autogen.ProjectManagementAgents') as mock_agents_class:
            mock_instance = MagicMock()
            mock_instance.analyze_project.return_value = {
                'status': 'success',
                'analysis_results': 'Mocked results',
                'metrics': {},
                'timestamp': '2025-12-23'
            }
            mock_agents_class.return_value = mock_instance
           
            result = analyze_project(sample_csv, use_llm=True)
           
            assert 'status' in result
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
@patch.dict(os.environ, {}, clear=True)
def test_analyze_project_function_without_token(sample_csv):
    """Test analyze_project function without API token"""
    try:
        from agents_autogen import analyze_project
       
        with patch('agents_autogen.simple_analyze') as mock_simple:
            mock_simple.return_value = {'status': 'success'}
           
            result = analyze_project(sample_csv, use_llm=False)
           
            # Should work without LLM
            assert result is not None
       
    except (ImportError, AttributeError):
        # If agents_simple import fails in agents_autogen, that's expected
        pytest.skip("AutoGen fallback not configured")
 
 
 
@patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'})
@patch('agents_autogen.AssistantAgent')
def test_agent_exception_handling(mock_assistant):
    """Test exception handling in agent workflow"""
    try:
        from agents_autogen import ProjectManagementAgents
       
        # Make agent raise exception
        mock_agent = MagicMock()
        mock_agent.generate_reply.side_effect = Exception("Agent failed")
        mock_assistant.return_value = mock_agent
       
        agents = ProjectManagementAgents()
        result = agents._run_agent_workflow("Test prompt")
       
        # Should handle exception gracefully
        assert isinstance(result, str)
        assert "unavailable" in result.lower() or "error" in result.lower()
       
    except ImportError:
        pytest.skip("AutoGen not installed")
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 