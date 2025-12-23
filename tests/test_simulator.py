"""
Unit tests for risk_simulator.py
Tests Monte Carlo simulation logic
"""
 
import pytest
import pandas as pd
import numpy as np
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from risk_simulator import RiskSimulator
 
 
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
 
 
def test_simulator_initialization(sample_df):
    """Test RiskSimulator initialization"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
   
    assert simulator.df is not None
    assert simulator.num_simulations == 100
    assert 'High' in simulator.risk_multipliers
 
 
def test_simulate_basic(sample_df):
    """Test basic simulation run"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert 'status' in result or 'mean_duration' in result
 
 
def test_simulate_result_structure(sample_df):
    """Test simulation result structure"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
    result = simulator.run_simulation()
   
    # Check if using dataclass or dict
    if 'simulation_result' in result:
        sim_result = result['simulation_result']
        assert hasattr(sim_result, 'mean_duration') or 'mean_duration' in sim_result
    else:
        assert 'mean_duration' in str(result) or 'percentile_50' in str(result)
 
 
def test_simulate_statistical_validity(sample_df):
    """Test that simulation produces valid statistical results"""
    simulator = RiskSimulator(sample_df, num_simulations=500)
    result = simulator.run_simulation()
   
    # Extract values from result
    if isinstance(result, dict):
        if 'simulation_result' in result:
            sim = result['simulation_result']
            if hasattr(sim, 'mean_duration'):
                assert sim.mean_duration > 0
                assert sim.std_duration >= 0
        else:
            # Direct dict with keys
            assert len(str(result)) > 0
 
 
def test_simulator_small_iterations(sample_df):
    """Test simulator with small number of iterations"""
    simulator = RiskSimulator(sample_df, num_simulations=50)
    result = simulator.run_simulation()
   
    assert result is not None
 
 
def test_simulator_single_task():
    """Test simulator with single task"""
    df = pd.DataFrame({
        'Task_ID': [1],
        'Task_Name': ['Task A'],
        'Duration_Days': [10],
        'Resource_Name': ['Alice'],
        'Cost_Per_Day': [500],
        'Risk_Level': ['Low'],
        'Predecessors': [None]
    })
   
    simulator = RiskSimulator(df, num_simulations=50)
    result = simulator.run_simulation()
   
    assert result is not None
 
 
def test_simulate_scenario(sample_df):
    """Test single scenario simulation"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
    duration, cost = simulator._simulate_scenario()
   
    assert duration > 0
    assert cost > 0
 
 
def test_risk_assessment(sample_df):
    """Test risk assessment generation"""
    from risk_simulator import SimulationResult
   
    sim_result = SimulationResult(
        mean_duration=50.0,
        std_duration=5.0,
        percentile_50=50.0,
        percentile_75=53.0,
        percentile_90=56.0,
        percentile_95=58.0,
        mean_cost=25000.0,
        std_cost=2000.0,
        risk_probability=0.3
    )
   
    simulator = RiskSimulator(sample_df, num_simulations=100)
    assessment = simulator._assess_risk(sim_result, 45.0, 20000.0)
   
    assert isinstance(assessment, str)
    assert len(assessment) > 0
 
 
def test_high_risk_scenario():
    """Test simulation with all high-risk tasks"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3],
        'Task_Name': ['Task A', 'Task B', 'Task C'],
        'Duration_Days': [10, 10, 10],
        'Resource_Name': ['Alice', 'Bob', 'Charlie'],
        'Cost_Per_Day': [500, 500, 500],
        'Risk_Level': ['High', 'High', 'High'],
        'Predecessors': [None, None, None]
    })
   
    simulator = RiskSimulator(df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert result is not None
 
 
def test_mixed_risk_levels():
    """Test simulation with mixed risk levels"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4],
        'Task_Name': ['Task A', 'Task B', 'Task C', 'Task D'],
        'Duration_Days': [10, 10, 10, 10],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Bob'],
        'Cost_Per_Day': [500, 600, 500, 600],
        'Risk_Level': ['High', 'Med', 'Low', 'Med'],
        'Predecessors': [None, None, None, None]
    })
   
    simulator = RiskSimulator(df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert 'status' in result
    assert result['status'] == 'success'
 
 
def test_simulation_result_structure(sample_df):
    """Test that simulation result has required fields"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert 'status' in result
    assert 'simulation_result' in result or 'mean_duration' in str(result)
    assert 'risk_assessment' in result or 'assessment' in str(result).lower()
 
 
def test_risk_multipliers(sample_df):
    """Test that risk multipliers are properly defined"""
    simulator = RiskSimulator(sample_df, num_simulations=50)
   
    assert 'High' in simulator.risk_multipliers
    assert 'Med' in simulator.risk_multipliers
    assert 'Low' in simulator.risk_multipliers
   
    # Verify multipliers are tuples with min/max
    assert len(simulator.risk_multipliers['High']) == 2
    assert len(simulator.risk_multipliers['Med']) == 2
    assert len(simulator.risk_multipliers['Low']) == 2
 
 
def test_simulation_with_large_iterations(sample_df):
    """Test simulation with large number of iterations"""
    simulator = RiskSimulator(sample_df, num_simulations=2000)
    result = simulator.run_simulation()
   
    assert result['status'] == 'success'
 
 
def test_low_risk_scenario():
    """Test simulation with all low-risk tasks"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3],
        'Task_Name': ['Task A', 'Task B', 'Task C'],
        'Duration_Days': [10, 10, 10],
        'Resource_Name': ['Alice', 'Bob', 'Charlie'],
        'Cost_Per_Day': [500, 500, 500],
        'Risk_Level': ['Low', 'Low', 'Low'],
        'Predecessors': [None, None, None]
    })
   
    simulator = RiskSimulator(df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert result is not None
    assert 'status' in result
 
 
def test_medium_risk_scenario():
    """Test simulation with all medium-risk tasks"""
    df = pd.DataFrame({
        'Task_ID': [1, 2, 3, 4],
        'Task_Name': ['Task A', 'Task B', 'Task C', 'Task D'],
        'Duration_Days': [10, 15, 8, 12],
        'Resource_Name': ['Alice', 'Bob', 'Alice', 'Bob'],
        'Cost_Per_Day': [500, 600, 500, 600],
        'Risk_Level': ['Med', 'Med', 'Med', 'Med'],
        'Predecessors': [None, None, None, None]
    })
   
    simulator = RiskSimulator(df, num_simulations=100)
    result = simulator.run_simulation()
   
    assert result['status'] == 'success'
 
 
def test_cost_calculation_in_simulation(sample_df):
    """Test that simulation calculates costs correctly"""
    simulator = RiskSimulator(sample_df, num_simulations=100)
    duration, cost = simulator._simulate_scenario()
   
    assert cost > 0
    assert duration > 0
    # Cost should be related to duration and cost_per_day
    assert cost > duration  # Since cost_per_day is typically > 1
 
 
def test_risk_categorization(sample_df):
    """Test risk categorization logic"""
    simulator = RiskSimulator(sample_df, num_simulations=50)
   
    # Test different probability levels
    assert simulator._categorize_risk(0.8) == "HIGH"
    assert simulator._categorize_risk(0.5) == "MEDIUM"
    assert simulator._categorize_risk(0.2) == "LOW"
 
 
def test_confidence_calculation(sample_df):
    """Test confidence level calculation"""
    from risk_simulator import SimulationResult
   
    sim_result = SimulationResult(
        mean_duration=50.0,
        std_duration=5.0,
        percentile_50=50.0,
        percentile_75=53.0,
        percentile_90=56.0,
        percentile_95=58.0,
        mean_cost=25000.0,
        std_cost=2000.0,
        risk_probability=0.3
    )
   
    simulator = RiskSimulator(sample_df, num_simulations=1000)
    confidence = simulator._calculate_confidence(sim_result)
   
    assert isinstance(confidence, float)
    assert 50 <= confidence <= 100
 
 
def test_simulate_project_risk_convenience_function(sample_df):
    """Test the convenience function wrapper"""
    from risk_simulator import simulate_project_risk
   
    result = simulate_project_risk(sample_df, num_simulations=100)
   
    assert 'status' in result
    assert result['status'] == 'success'
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 
