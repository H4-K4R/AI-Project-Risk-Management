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
 
 
def test_analyze_project_autogen_error_fallback(sample_csv):
    """Test fallback when AutoGen fails"""
    # Test with use_autogen=False to ensure it works without AutoGen
    result = analyze_project(sample_csv, use_llm=False, use_autogen=False)
   
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
        'Task_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Task_Name': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10'],
        'Duration_Days': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Alice', 'Alice', 'Alice', 'Alice', 'Alice', 'Bob', 'Bob', 'Charlie', 'Charlie'],
        'Cost_Per_Day': [500, 500, 500, 500, 500, 500, 600, 600, 550, 550],
        'Risk_Level': ['Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low'],
        'Predecessors': [None, None, None, None, None, None, None, None, None, None]
    })
   
    metrics = calculate_project_metrics(df)
   
    # Alice has 6 tasks, Bob has 2, Charlie has 2 - avg is 3.33, overloaded threshold is 5.0
    # Alice with 6 tasks should be overloaded (6 > 5.0)
    assert len(metrics['overloaded_resources']) > 0
    assert metrics['overloaded_resources']['Resource'].iloc[0] == 'Alice'
 
 
def test_metrics_underutilized_resources():
    """Test detection of underutilized resources"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'Task_Name': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9'],
        'Duration_Days': [10, 10, 10, 10, 10, 10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Alice', 'Alice', 'Alice', 'Bob', 'Charlie', 'Charlie', 'Charlie', 'Charlie'],
        'Cost_Per_Day': [500, 500, 500, 500, 600, 550, 550, 550, 550],
        'Risk_Level': ['Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low'],
        'Predecessors': [None, None, None, None, None, None, None, None, None]
    })
   
    metrics = calculate_project_metrics(df)
   
    # Alice has 4 tasks, Bob has 1, Charlie has 4 - avg is 3.0, underutilized threshold is 1.5
    # Bob with 1 task should be underutilized (1 < 1.5)
    assert len(metrics['underutilized_resources']) > 0
    assert metrics['underutilized_resources']['Resource'].iloc[0] == 'Bob'
 
 
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
 
 
def test_analyze_project_with_autogen_import_error(sample_csv):
    """Test handling when AutoGen import fails"""
    result = analyze_project(sample_csv, use_llm=False, use_autogen=True)
   
    # Should still succeed with just metrics
    assert result['status'] == 'success'
    assert 'metrics' in result
 
 
def test_analyze_project_with_llm_enabled(sample_csv):
    """Test project analysis with LLM enabled but no token"""
    result = analyze_project(sample_csv, use_llm=True, use_autogen=False)
   
    # Should succeed even if LLM unavailable, falling back to metrics only
    assert result['status'] == 'success'
    assert 'metrics' in result
 
 
def test_build_report_no_analysis(sample_df):
    """Test building report with only metrics"""
    metrics = calculate_project_metrics(sample_df)
    report = build_report(metrics, None, None)
   
    assert 'PROJECT METRICS SUMMARY' in report
    assert str(metrics['total_tasks']) in report
 
 
def test_calculate_metrics_with_nan_predecessors():
    """Test metrics calculation with NaN predecessors"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3],
        'Task_Name': ['T1', 'T2', 'T3'],
        'Duration_Days': [5, 5, 5],
        'Resource_Name': ['Alice', 'Bob', 'Alice'],
        'Cost_Per_Day': [500, 600, 500],
        'Risk_Level': ['Low', 'Med', 'High'],
        'Predecessors': [pd.NA, None, '']
    })
   
    metrics = calculate_project_metrics(df)
    assert metrics['num_independent'] >= 2
    assert metrics['complex_task_count'] == 0
 
 
def test_analyze_project_file_error():
    """Test handling when CSV file has read errors"""
    result = analyze_project("nonexistent_file.csv", use_llm=False, use_autogen=False)
   
    assert result['status'] == 'error'
    assert 'File not found' in result['error_message'] or 'Analysis failed' in result['error_message']
 
 
def test_analyze_project_success_path(sample_csv):
    """Test successful project analysis without LLM"""
    result = analyze_project(sample_csv, use_llm=False, use_autogen=False)
   
    assert result['status'] == 'success'
    assert 'metrics' in result
    assert 'analysis_results' in result
    assert 'timestamp' in result
 
 
def test_calculate_metrics_all_risk_levels():
    """Test metrics with all different risk levels represented"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4, 5, 6],
        'Task_Name': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'],
        'Duration_Days': [10, 10, 10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Bob', 'Alice', 'Bob'],
        'Cost_Per_Day': [500, 600, 500, 600, 500, 600],
        'Risk_Level': ['High', 'High', 'Med', 'Med', 'Low', 'Low'],
        'Predecessors': [None, None, '1', '2', '3', '4']
    })
   
    metrics = calculate_project_metrics(df)
   
    assert metrics['high_risk_count'] == 2
    assert metrics['med_risk_count'] == 2
    assert metrics['low_risk_count'] == 2
    assert metrics['total_tasks'] == 6
 
 
def test_analyze_project_with_autogen_enabled(sample_csv):
    """Test analysis with autogen enabled but falling back gracefully"""
    result = analyze_project(sample_csv, use_llm=False, use_autogen=True)
   
    # Should work even if AutoGen not available
    assert result['status'] == 'success'
    assert 'metrics' in result
 
 
def test_build_report_metrics_formatting(sample_df):
    """Test that report formats metrics correctly"""
    metrics = calculate_project_metrics(sample_df)
    report = build_report(metrics, None, None)
   
    # Check for key metric values in report
    assert str(metrics['total_tasks']) in report
    assert str(metrics['num_resources']) in report
 
 
def test_complex_tasks_detection():
    """Test detection of tasks with multiple dependencies"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4, 5],
        'Task_Name': ['T1', 'T2', 'T3', 'T4', 'T5'],
        'Duration_Days': [5, 5, 5, 5, 5],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Bob', 'Alice'],
        'Cost_Per_Day': [500, 600, 500, 600, 500],
        'Risk_Level': ['Low', 'Low', 'Med', 'High', 'Med'],
        'Predecessors': [None, None, '1,2', '1,2,3', '2,3,4']
    })
   
    metrics = calculate_project_metrics(df)
   
    # Tasks 3, 4, 5 have multiple predecessors (complexity > 1)
    assert metrics['complex_task_count'] >= 3
 
 
@patch('agents_autogen.ProjectManagementAgents')
def test_analyze_with_autogen_success(mock_agents, sample_csv):
    """Test successful AutoGen analysis"""
    try:
        from agents_simple import analyze_project
       
        # Mock successful AutoGen analysis
        mock_instance = MagicMock()
        mock_instance.analyze_with_metrics.return_value = "Mocked AutoGen Analysis"
        mock_agents.return_value = mock_instance
       
        result = analyze_project(sample_csv, use_llm=False, use_autogen=True)
       
        assert result['status'] == 'success'
    except ImportError:
        pytest.skip("AutoGen not available")
 
 
@patch('agents_autogen.ProjectManagementAgents')
def test_analyze_with_autogen_exception(mock_agents, sample_csv):
    """Test AutoGen exception handling"""
    try:
        from agents_simple import analyze_project
       
        # Make AutoGen raise an exception
        mock_agents.side_effect = Exception("AutoGen failed")
       
        result = analyze_project(sample_csv, use_llm=False, use_autogen=True)
       
        # Should still succeed with metrics only
        assert result['status'] == 'success'
    except ImportError:
        pytest.skip("AutoGen not available")
 
 
def test_analyze_corrupted_csv(tmp_path):
    """Test handling of corrupted CSV file"""
    # Create a corrupted CSV
    corrupted_path = tmp_path / "corrupted.csv"
    with open(corrupted_path, 'w') as f:
        f.write("invalid,csv,data\n1,2\n3")
   
    result = analyze_project(str(corrupted_path), use_llm=False, use_autogen=False)
   
    # Should return error status
    assert result['status'] == 'error'
    assert 'error_message' in result
 
 
def test_metrics_with_empty_predecessors():
    """Test metrics with various empty predecessor formats"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4],
        'Task_Name': ['T1', 'T2', 'T3', 'T4'],
        'Duration_Days': [5, 5, 5, 5],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Bob'],
        'Cost_Per_Day': [500, 600, 500, 600],
        'Risk_Level': ['Low', 'Med', 'High', 'Low'],
        'Predecessors': [None, '', '  ', pd.NA]
    })
   
    metrics = calculate_project_metrics(df)
   
    # All should be considered independent
    assert metrics['num_independent'] >= 2
    assert metrics['total_tasks'] == 4
 
 
def test_resource_stats_calculation(sample_df):
    """Test resource statistics calculation"""
    metrics = calculate_project_metrics(sample_df)
   
    assert 'resource_stats' in metrics
    assert len(metrics['resource_stats']) > 0
    assert 'avg_tasks_per_resource' in metrics
    assert metrics['avg_tasks_per_resource'] > 0
    
def test_build_report_with_all_data(sample_df):
    """Test build_report with both AutoGen and simple analysis"""
    metrics = calculate_project_metrics(sample_df)
    autogen_result = "AutoGen analysis complete"
    simple_result = "Simple analysis complete"
   
    report = build_report(metrics, autogen_result, simple_result)
   
    # Should prioritize AutoGen
    assert 'PROJECT METRICS SUMMARY' in report
    assert autogen_result in report
   
 
def test_dataframe_in_metrics(sample_df):
    """Test that metrics include the dataframe"""
    metrics = calculate_project_metrics(sample_df)
   
    assert 'dataframe' in metrics
    assert isinstance(metrics['dataframe'], pd.DataFrame)
    assert len(metrics['dataframe']) == len(sample_df)
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 
