"""
Unit tests for agents_simple.py
Tests metrics calculation and project analysis
"""
 
import pytest
import pandas as pd
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from agents_simple import calculate_project_metrics, analyze_project
 
 
@pytest.fixture
def sample_df():
    """Create sample project data matching dummy_data.csv structure"""
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
    """Create a temporary CSV file"""
    csv_path = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_path, index=False)
    return str(csv_path)
 
 
def test_calculate_project_metrics_basic(sample_df):
    """Test basic metrics calculation"""
    metrics = calculate_project_metrics(sample_df)
   
    assert metrics['total_tasks'] == 5
    assert metrics['num_resources'] == 3
    assert metrics['total_duration'] == 65
    assert metrics['total_cost'] > 0
 
 
def test_calculate_project_metrics_risk_distribution(sample_df):
    """Test risk distribution calculation"""
    metrics = calculate_project_metrics(sample_df)
   
    assert metrics['high_risk_count'] == 2
    assert metrics['med_risk_count'] == 2
    assert metrics['low_risk_count'] == 1
 
 
def test_calculate_project_metrics_dependencies(sample_df):
    """Test dependency analysis"""
    metrics = calculate_project_metrics(sample_df)
   
    assert metrics['num_dependencies'] == 3
    assert metrics['num_independent'] == 2
 
 
def test_calculate_project_metrics_resources(sample_df):
    """Test resource statistics"""
    metrics = calculate_project_metrics(sample_df)
   
    assert len(metrics['resource_stats']) == 3
    assert 'Total_Cost' in metrics['resource_stats'].columns
 
 
def test_analyze_project_without_llm(sample_csv):
    """Test analysis with LLM disabled"""
    result = analyze_project(sample_csv, use_llm=False, use_autogen=False)
   
    assert result['status'] == 'success'
    assert 'analysis_results' in result
    assert 'metrics' in result
    assert 'timestamp' in result
 
 
def test_analyze_project_file_not_found():
    """Test handling of missing file"""
    result = analyze_project("nonexistent_xyz.csv", use_llm=False, use_autogen=False)
   
    assert result['status'] == 'error'
    assert 'error_message' in result
 
 
def test_analyze_project_metrics_included(sample_csv):
    """Test that metrics are included in result"""
    result = analyze_project(sample_csv, use_llm=False, use_autogen=False)
   
    assert result['status'] == 'success'
    assert result['metrics']['total_tasks'] == 5
    assert result['metrics']['num_resources'] == 3
 
 
def test_metrics_complexity(sample_df):
    """Test complexity calculation"""
    metrics = calculate_project_metrics(sample_df)
   
    assert metrics['complex_task_count'] >= 1
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 
