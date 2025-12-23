"""
Additional tests for agents_simple.py to increase coverage
Tests LLM integration and report building
"""
 
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from agents_simple import calculate_project_metrics, analyze_project, build_report
 
 
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'Task_ID': [1, 2, 3],
        'Task_Name': ['Task A', 'Task B', 'Task C'],
        'Duration_Days': [10, 15, 8],
        'Resource_Name': ['Alice', 'Bob', 'Alice'],
        'Cost_Per_Day': [500, 600, 500],
        'Risk_Level': ['High', 'Med', 'Low'],
        'Predecessors': [None, '1', '1']
    })
 
 
@pytest.fixture
def sample_csv(tmp_path, sample_df):
    csv_path = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_path, index=False)
    return str(csv_path)
 
 
def test_build_report_no_ai(sample_df):
    """Test report building without AI analysis"""
    metrics = calculate_project_metrics(sample_df)
    report = build_report(metrics, None, None)
   
    assert 'PROJECT METRICS SUMMARY' in report
    assert 'Total Tasks: 3' in report
    assert 'AI ANALYSIS NOT AVAILABLE' in report or 'Metrics Only' in report
 
 
def test_build_report_with_autogen(sample_df):
    """Test report building with AutoGen analysis"""
    metrics = calculate_project_metrics(sample_df)
    autogen_analysis = "Mocked AutoGen Analysis Result"
    report = build_report(metrics, autogen_analysis, None)
   
    assert 'PROJECT METRICS SUMMARY' in report
    assert autogen_analysis in report
    assert 'AutoGen Multi-Agent' in report
 
 
def test_build_report_with_simple_llm(sample_df):
    """Test report building with simple LLM analysis"""
    metrics = calculate_project_metrics(sample_df)
    simple_analysis = "Mocked Simple LLM Analysis"
    report = build_report(metrics, None, simple_analysis)
   
    assert 'PROJECT METRICS SUMMARY' in report
    assert simple_analysis in report
    assert 'Simple LLM' in report
 
 
@patch('agents_simple.LLMClient')
def test_analyze_project_with_llm_mock(mock_llm_class, sample_csv):
    """Test analysis with mocked LLM"""
    # Setup mock
    mock_client = MagicMock()
    mock_client.available.return_value = True
    mock_client.generate.return_value = "Mocked LLM Response"
    mock_llm_class.return_value = mock_client
   
    result = analyze_project(sample_csv, use_llm=True, use_autogen=False)
   
    assert result['status'] == 'success'
    assert 'analysis_results' in result
 
 
@patch('agents_simple.ProjectManagementAgents')
def test_analyze_project_autogen_error_fallback(mock_agents_class, sample_csv):
    """Test fallback when AutoGen fails"""
    # Make AutoGen raise an error
    mock_agents_class.side_effect = Exception("AutoGen error")
   
    result = analyze_project(sample_csv, use_llm=False, use_autogen=True)
   
    # Should still succeed with metrics only
    assert result['status'] == 'success'
    assert 'metrics' in result
 
 
def test_metrics_with_no_dependencies(sample_df):
    """Test metrics when no tasks have dependencies"""
    df_no_deps = sample_df.copy()
    df_no_deps['Predecessors'] = None
   
    metrics = calculate_project_metrics(df_no_deps)
   
    assert metrics['num_dependencies'] == 0
    assert metrics['num_independent'] == 3
 
 
def test_metrics_with_all_high_risk(sample_df):
    """Test metrics when all tasks are high risk"""
    df_high_risk = sample_df.copy()
    df_high_risk['Risk_Level'] = 'High'
   
    metrics = calculate_project_metrics(df_high_risk)
   
    assert metrics['high_risk_count'] == 3
    assert metrics['med_risk_count'] == 0
    assert metrics['low_risk_count'] == 0
 
 
def test_metrics_overloaded_resources():
    """Test detection of overloaded resources"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4, 5, 6],
        'Task_Name': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'Duration_Days': [10, 10, 10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Alice', 'Alice', 'Alice', 'Bob', 'Bob'],
        'Cost_Per_Day': [500, 500, 500, 500, 600, 600],
        'Risk_Level': ['Low', 'Low', 'Low', 'Low', 'Low', 'Low'],
        'Predecessors': [None, None, None, None, None, None]
    })
   
    metrics = calculate_project_metrics(df)
   
    # Alice has 4 tasks, Bob has 2 - Alice should be overloaded
    assert len(metrics['overloaded_resources']) > 0
 
 
def test_metrics_underutilized_resources():
    """Test detection of underutilized resources"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4],
        'Task_Name': ['T1', 'T2', 'T3', 'T4'],
        'Duration_Days': [10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Alice', 'Alice', 'Bob'],
        'Cost_Per_Day': [500, 500, 500, 600],
        'Risk_Level': ['Low', 'Low', 'Low', 'Low'],
        'Predecessors': [None, None, None, None]
    })
   
    metrics = calculate_project_metrics(df)
   
    # Bob has only 1 task while average is 2 - should be underutilized
    assert len(metrics['underutilized_resources']) > 0
 
 
def test_analyze_project_invalid_csv():
    """Test handling of invalid CSV path"""
    result = analyze_project("invalid/path/file.csv", use_llm=False, use_autogen=False)
   
    assert result['status'] == 'error'
    assert 'error_message' in result
 
 
def test_metrics_total_cost_calculation(sample_df):
    """Test total cost calculation"""
    metrics = calculate_project_metrics(sample_df)
   
    expected_cost = (10*500) + (15*600) + (8*500)  # Duration * Cost_Per_Day
    assert metrics['total_cost'] == expected_cost
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 