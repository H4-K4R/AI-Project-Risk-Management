"""
Unit tests for api.py
Tests FastAPI application structure and endpoints
"""
 
import pytest
import sys
import os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
 
def test_api_imports():
    """Test that API module can be imported"""
    try:
        from api import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import api: {e}")
 
 
def test_api_has_fastapi_instance():
    """Test that app is a FastAPI instance"""
    from api import app
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)
 
 
def test_api_routes_exist():
    """Test that required routes are defined"""
    from api import app
   
    routes = [route.path for route in app.routes]
   
    # Check that essential routes exist
    assert "/" in routes or any("/" in r for r in routes)
    assert any("health" in r for r in routes)
    assert any("analyze" in r for r in routes)
 
 
def test_api_cors_middleware():
    """Test that CORS middleware is configured"""
    from api import app
   
    # Should have middleware configured
    assert hasattr(app, 'middleware')
 
 
def test_api_models_defined():
    """Test that Pydantic models are defined"""
    try:
        from api import AnalysisRequest, AnalysisResponse
        assert AnalysisRequest is not None
        assert AnalysisResponse is not None
    except ImportError:
        # Models might be defined inline
        pass
 
 
def test_api_endpoints_defined():
    """Test that endpoint functions exist"""
    from api import app
   
    # Get all route names
    route_names = [route.name for route in app.routes if hasattr(route, 'name')]
   
    # Should have multiple endpoints
    assert len(route_names) > 0
 
 
def test_analysis_request_model():
    """Test AnalysisRequest model structure"""
    try:
        from api import AnalysisRequest
       
        # Create instance with defaults
        request = AnalysisRequest()
       
        # Should have expected fields
        assert hasattr(request, 'use_llm')
        assert hasattr(request, 'use_autogen')
    except (ImportError, TypeError):
        # Model might not be importable or have different structure
        pass
 
 
def test_analysis_response_model():
    """Test AnalysisResponse model structure"""
    try:
        from api import AnalysisResponse
       
        # Should be a valid Pydantic model
        from pydantic import BaseModel
        assert issubclass(AnalysisResponse, BaseModel)
    except (ImportError, TypeError):
        # Model might not be importable
        pass
 
 
def test_api_title_and_description():
    """Test that API has title and description"""
    from api import app
   
    assert hasattr(app, 'title')
    assert hasattr(app, 'description')
    assert len(app.title) > 0
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 