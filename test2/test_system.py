"""
Test Suite for AI Project Risk & Resource Management Agent
Run this to verify all components are working correctly
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_test(message, status):
    """Print formatted test result"""
    symbol = "✓" if status else "✗"
    color = "GREEN" if status else "RED"
    print(f"[{symbol}] {message}")

def test_imports():
    """Test all required imports"""
    print("\n=== Testing Imports ===")
    
    tests = [
        ("pandas", "import pandas as pd"),
        ("streamlit", "import streamlit as st"),
        ("plotly", "import plotly.express as px"),
        ("crewai", "from crewai import Agent, Task, Crew"),
        ("crewai_tools", "from crewai_tools import tool"),
        ("pulp", "import pulp"),
        ("langchain", "from langchain import OpenAI"),
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print_test(f"{name} imported successfully", True)
            results.append(True)
        except ImportError as e:
            print_test(f"{name} import failed: {e}", False)
            results.append(False)
    
    return all(results)

def test_files():
    """Test required files exist"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        "agents.py",
        "app.py",
        "requirements.txt",
        "../dummy_data.csv",
        "README.md",
        ".env.example"
    ]
    
    results = []
    for file in required_files:
        exists = os.path.exists(file)
        print_test(f"{file} exists", exists)
        results.append(exists)
    
    return all(results)

def test_csv_format():
    """Test CSV data format"""
    print("\n=== Testing CSV Data Format ===")
    
    try:
        import pandas as pd
        df = pd.read_csv("../dummy_data.csv")
        
        required_columns = [
            'Task_ID', 'Task_Name', 'Duration_Days', 
            'Resource_Name', 'Cost_Per_Day', 'Predecessors', 'Risk_Level'
        ]
        
        results = []
        for col in required_columns:
            exists = col in df.columns
            print_test(f"Column '{col}' present", exists)
            results.append(exists)
        
        # Test data validity
        row_count = len(df) > 0
        print_test(f"CSV contains data ({len(df)} rows)", row_count)
        results.append(row_count)
        
        # Test risk levels
        valid_risks = df['Risk_Level'].isin(['Low', 'Med', 'High']).all()
        print_test("All risk levels are valid (Low/Med/High)", valid_risks)
        results.append(valid_risks)
        
        return all(results)
    except Exception as e:
        print_test(f"CSV validation failed: {e}", False)
        return False

def test_env_setup():
    """Test environment configuration"""
    print("\n=== Testing Environment Setup ===")
    
    results = []
    
    # Check for .env file
    env_exists = os.path.exists(".env")
    print_test(".env file exists", env_exists)
    results.append(env_exists)
    
    if env_exists:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            has_key = api_key is not None and api_key != "your_openai_api_key_here"
            print_test("OPENAI_API_KEY is configured", has_key)
            results.append(has_key)
            
            if not has_key:
                print("  ⚠ Warning: Add your actual OpenAI API key to .env file")
        except ImportError:
            print_test("python-dotenv not installed (optional)", True)
    else:
        print("  ⚠ Warning: Copy .env.example to .env and add your API key")
        results.append(False)
    
    return all(results)

def test_agents_module():
    """Test agents.py module"""
    print("\n=== Testing Agents Module ===")
    
    try:
        from agents import (
            analyze_csv_data, 
            calculate_risk_metrics,
            analyze_resource_allocation,
            ProjectManagementCrew,
            analyze_project
        )
        
        print_test("All agent functions imported", True)
        
        # Test CSV analyzer tool
        try:
            result = analyze_csv_data.run("../dummy_data.csv")
            has_content = len(result) > 0
            print_test("CSV analyzer tool works", has_content)
        except Exception as e:
            print_test(f"CSV analyzer tool failed: {e}", False)
            return False
        
        # Test risk calculator tool
        try:
            result = calculate_risk_metrics.run("../dummy_data.csv")
            has_content = len(result) > 0
            print_test("Risk calculator tool works", has_content)
        except Exception as e:
            print_test(f"Risk calculator tool failed: {e}", False)
            return False
        
        # Test resource analyzer tool
        try:
            result = analyze_resource_allocation.run("../dummy_data.csv")
            has_content = len(result) > 0
            print_test("Resource analyzer tool works", has_content)
        except Exception as e:
            print_test(f"Resource analyzer tool failed: {e}", False)
            return False
        
        # Test crew initialization
        try:
            crew = ProjectManagementCrew("../dummy_data.csv")
            print_test("ProjectManagementCrew initializes", True)
        except Exception as e:
            print_test(f"Crew initialization failed: {e}", False)
            return False
        
        return True
        
    except Exception as e:
        print_test(f"Agents module test failed: {e}", False)
        return False

def test_app_module():
    """Test app.py module"""
    print("\n=== Testing App Module ===")
    
    try:
        # Check if app.py can be imported (syntax check)
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()
            compile(code, "app.py", "exec")
        
        print_test("app.py syntax is valid", True)
        
        # Check for key functions
        key_functions = [
            "calculate_gantt_dates",
            "create_gantt_chart",
            "create_resource_chart",
            "create_risk_distribution_chart",
            "display_project_metrics",
            "main"
        ]
        
        for func in key_functions:
            exists = f"def {func}" in code
            print_test(f"Function '{func}' defined", exists)
        
        return True
        
    except Exception as e:
        print_test(f"App module test failed: {e}", False)
        return False

def run_all_tests():
    """Run all tests and print summary"""
    print("\n" + "="*50)
    print("  AI PROJECT MANAGEMENT SYSTEM - TEST SUITE")
    print("="*50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Imports": test_imports(),
        "File Structure": test_files(),
        "CSV Format": test_csv_format(),
        "Environment": test_env_setup(),
        "Agents Module": test_agents_module(),
        "App Module": test_app_module()
    }
    
    print("\n" + "="*50)
    print("  TEST SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("\n" + "-"*50)
    print(f"Total: {total_passed}/{total_tests} test suites passed")
    print("-"*50)
    
    if all(results.values()):
        print("\n🎉 All tests passed! Your system is ready to use.")
        print("   Run: streamlit run app.py")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        print("   Check README.md for troubleshooting steps.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
