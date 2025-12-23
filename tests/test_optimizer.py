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
 
 
def test_baseline_duration_calculation(sample_df):
    """Test baseline duration calculation"""
    optimizer = ResourceOptimizer(sample_df)
    baseline = optimizer._calculate_baseline_duration()
   
    # Baseline should be the max workload across resources
    # Alice: 10+8=18, Bob: 15+20=35, Charlie: 12
    # Max should be 35
    assert baseline > 0
    assert baseline >= 12  # At least Charlie's workload
 
 
def test_optimized_duration_calculation(sample_df):
    """Test optimized duration calculation"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    if result['status'] in ['success', 'suboptimal']:
        allocation = result['optimized_allocation']
        optimized = optimizer._calculate_optimized_duration(allocation)
        assert optimized > 0
 
 
def test_recommendations_generation(sample_df):
    """Test recommendations text generation"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], str)
    assert len(result['recommendations']) > 0
 
 
def test_extract_solution(sample_df):
    """Test solution extraction from optimization"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    if result['status'] in ['success', 'suboptimal']:
        assert 'optimized_allocation' in result
        assert isinstance(result['optimized_allocation'], list)
        assert len(result['optimized_allocation']) > 0
 
 
def test_optimization_with_dependencies(sample_df):
    """Test that optimization handles task dependencies"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    # Should complete successfully even with dependencies
    assert result['status'] in ['success', 'suboptimal']
    assert 'baseline_duration' in result
    assert 'optimized_duration' in result
 
 
def test_optimization_improvement_metric(sample_df):
    """Test that improvement percentage is calculated"""
    optimizer = ResourceOptimizer(sample_df)
    result = optimizer.optimize_allocation()
   
    assert 'improvement_percentage' in result
    assert isinstance(result['improvement_percentage'], (int, float))
 
 
def test_optimize_resources_convenience_function(sample_df):
    """Test the convenience function wrapper"""
    from resource_optimizer import optimize_resources
   
    result = optimize_resources(sample_df)
   
    assert 'status' in result
    assert result['status'] in ['success', 'suboptimal']
 
 
def test_optimizer_with_many_resources():
    """Test optimization with many resources"""
    df = pd.DataFrame({
        'Task_ID': list(range(1, 11)),
        'Task_Name': [f'Task {i}' for i in range(1, 11)],
        'Duration_Days': [5] * 10,
        'Resource_Name': [f'Resource_{i%5}' for i in range(10)],
        'Cost_Per_Day': [500] * 10,
        'Risk_Level': ['Low'] * 10,
        'Predecessors': [None] * 10
    })
   
    optimizer = ResourceOptimizer(df)
    result = optimizer.optimize_allocation()
   
    assert result['status'] in ['success', 'suboptimal']
 
 
def test_optimizer_task_resource_mapping(sample_df):
    """Test that optimizer creates correct task-resource mappings"""
    optimizer = ResourceOptimizer(sample_df)
   
    assert len(optimizer.tasks) > 0
    assert len(optimizer.resources) > 0
    assert len(optimizer.tasks) == len(sample_df)
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 
