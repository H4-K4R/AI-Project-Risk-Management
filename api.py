"""
FastAPI Backend for Project Risk & Resource Management
Provides RESTful API for programmatic access to analysis engine
 
# Aligns with AI4SE Phase 21: CI/CD Integration
# Enables automated project analysis in development pipelines
"""
 
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import tempfile
import os
import json
from datetime import datetime
 
# Import analysis modules
from agents_simple import analyze_project, calculate_project_metrics
from resource_optimizer import optimize_resources
from risk_simulator import simulate_project_risk
 
 
def convert_to_serializable(obj):
    """Convert numpy/pandas types to JSON-serializable Python types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    else:
        return obj
 
 
app = FastAPI(
    title="AI Project Risk & Resource Management API",
    description="RESTful API for project analysis, optimization, and risk simulation",
    version="1.0.0"
)
 
# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
class AnalysisRequest(BaseModel):
    """Request model for project analysis."""
    use_llm: bool = True
    use_autogen: bool = True
    enable_optimization: bool = False
    enable_simulation: bool = False
    num_simulations: int = 1000
 
 
class AnalysisResponse(BaseModel):
    """Response model for project analysis."""
    status: str
    timestamp: str
    analysis_results: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    optimization: Optional[Dict[str, Any]] = None
    simulation: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
 
 
@app.get("/")
async def root():
    """API root endpoint with documentation."""
    return {
        "message": "AI Project Risk & Resource Management API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Upload CSV and run full project analysis",
            "/optimize": "POST - Run resource optimization only",
            "/simulate": "POST - Run Monte Carlo risk simulation only",
            "/health": "GET - API health check"
        },
        "documentation": "/docs"
    }
 
 
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
 
 
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_project_endpoint(
    file: UploadFile = File(...),
    use_llm: bool = True,
    use_autogen: bool = True,
    enable_optimization: bool = False,
    enable_simulation: bool = False,
    num_simulations: int = 1000
):
    """
    Comprehensive project analysis endpoint.
   
    Upload a project CSV file and get:
    - AI-powered analysis (with AutoGen multi-agent system)
    - Optional: Resource optimization recommendations
    - Optional: Monte Carlo risk simulation
   
    Args:
        file: CSV file with project data
        use_llm: Enable LLM analysis
        use_autogen: Enable AutoGen multi-agent system
        enable_optimization: Run resource optimization
        enable_simulation: Run Monte Carlo simulation
        num_simulations: Number of Monte Carlo iterations
       
    Returns:
        Comprehensive analysis results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
       
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
       
        try:
            # Run main analysis
            analysis_result = analyze_project(
                tmp_path,
                use_llm=use_llm,
                use_autogen=use_autogen
            )
           
            # Load DataFrame for optional analyses
            df = pd.read_csv(tmp_path)
           
            # Optional: Resource optimization
            optimization_result = None
            if enable_optimization:
                optimization_result = optimize_resources(df)
                optimization_result = convert_to_serializable(optimization_result)
           
            # Optional: Monte Carlo simulation
            simulation_result = None
            if enable_simulation:
                simulation_result = simulate_project_risk(df, num_simulations)
                simulation_result = convert_to_serializable(simulation_result)
           
            # Convert all results to JSON-serializable format
            metrics = convert_to_serializable(analysis_result.get('metrics'))
           
            return AnalysisResponse(
                status=analysis_result['status'],
                timestamp=analysis_result['timestamp'],
                analysis_results=analysis_result.get('analysis_results'),
                metrics=metrics,
                optimization=optimization_result,
                simulation=simulation_result
            )
           
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
 
 
@app.post("/optimize")
async def optimize_endpoint(file: UploadFile = File(...)):
    """
    Resource optimization endpoint.
   
    Upload a project CSV and get optimized resource allocation using Linear Programming.
   
    Args:
        file: CSV file with project data
       
    Returns:
        Optimization results with recommendations
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
       
        # Save and process file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
       
        try:
            df = pd.read_csv(tmp_path)
            result = optimize_resources(df)
            result = convert_to_serializable(result)
            return JSONResponse(content=result)
        finally:
            os.unlink(tmp_path)
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
 
 
@app.post("/simulate")
async def simulate_endpoint(
    file: UploadFile = File(...),
    num_simulations: int = 1000
):
    """
    Monte Carlo risk simulation endpoint.
   
    Upload a project CSV and run risk simulation.
   
    Args:
        file: CSV file with project data
        num_simulations: Number of Monte Carlo iterations (default: 1000)
       
    Returns:
        Simulation results with risk assessment
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
       
        if num_simulations < 100 or num_simulations > 100000:
            raise HTTPException(
                status_code=400,
                detail="num_simulations must be between 100 and 100,000"
            )
       
        # Save and process file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
       
        try:
            df = pd.read_csv(tmp_path)
            result = simulate_project_risk(df, num_simulations)
            result = convert_to_serializable(result)
            return JSONResponse(content=result)
        finally:
            os.unlink(tmp_path)
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
 
 
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 API Root: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
 
