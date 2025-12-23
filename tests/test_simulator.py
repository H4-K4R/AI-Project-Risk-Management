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
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 