"""
Unit tests for resource_optimizer.py
Tests PuLP-based linear programming optimization
"""
 
import pytest
import pandas as pd
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from resource_optimizer import ResourceOptimizer
 
 
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
 
 
def test_optimizer_initialization(sample_df):
    """Test ResourceOptimizer initialization"""
    optimizer = ResourceOptimizer(sample_df)
   
    assert optimizer.df is not None
    assert len(optimizer.tasks) == 5
    assert len(optimizer.resources) == 3
 
 
def test_optimize_basic(sample_df):
    """Test basic optimization run"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    assert 'status' in result
    assert 'baseline_duration' in result
    assert 'optimized_duration' in result
    assert 'improvement_percentage' in result
 
 
def test_optimize_duration_improvement(sample_df):
    """Test that optimization improves or maintains duration"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    assert result['optimized_duration'] <= result['baseline_duration']
    assert result['improvement_percentage'] >= 0
 
 
def test_optimize_result_structure(sample_df):
    """Test result dictionary structure"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    required_keys = ['status', 'baseline_duration', 'optimized_duration',
                    'improvement_percentage', 'recommendations']
    for key in required_keys:
        assert key in result
 
 
def test_optimize_recommendations_exist(sample_df):
    """Test that recommendations are generated"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    # Recommendations is a formatted string report
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], str)
    assert len(result['recommendations']) > 0
    assert 'OPTIMIZATION RECOMMENDATIONS' in result['recommendations']
 
 
def test_optimize_single_task():
    """Test optimization with single task"""
    df = pd.DataFrame({
        'Task_ID': [1],
        'Task_Name': ['Task A'],
        'Duration_Days': [10],
        'Resource_Name': ['Alice'],
        'Cost_Per_Day': [500],
        'Risk_Level': ['Low'],
        'Predecessors': [None]
    })
   
    optimizer = ResourceOptimizer(df)
    result = optimizer.optimize_allocation()
   
    assert 'status' in result
 
 
def test_optimize_parallel_tasks():
    """Test optimization with parallel tasks (no dependencies)"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3],
        'Task_Name': ['Task A', 'Task B', 'Task C'],
        'Duration_Days': [10, 10, 10],
        'Resource_Name': ['Alice', 'Bob', 'Charlie'],
        'Cost_Per_Day': [500, 500, 500],
        'Risk_Level': ['Low', 'Low', 'Low'],
        'Predecessors': [None, None, None]
    })
   
    optimizer = ResourceOptimizer(df)
    result = optimizer.optimize_allocation()
   
    assert result['status'] in ['success', 'suboptimal']
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 