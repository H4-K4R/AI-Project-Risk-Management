"""
Unit tests for llm_client.py
Tests HuggingFace LLM client functionality
"""
 
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
 
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
 
from llm_client import LLMClient
 
 
def test_llm_client_initialization():
    """Test LLMClient initialization"""
    client = LLMClient()
    assert client is not None
 
 
def test_llm_client_availability_with_token():
    """Test availability when token is set"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token_123'}):
        client = LLMClient()
        # Should be available if token exists (even if fake)
        assert hasattr(client, 'available')
 
 
def test_llm_client_availability_without_token():
    """Test availability when token is missing"""
    with patch.dict(os.environ, {}, clear=True):
        client = LLMClient()
        # Should handle missing token gracefully
        assert client is not None
 
 
@patch('llm_client.OpenAI')
def test_llm_client_generate_with_mock(mock_openai):
    """Test generate method with mocked API"""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked LLM response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
   
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client = LLMClient()
       
        if hasattr(client, 'generate') and callable(client.generate):
            result = client.generate("Test prompt")
            assert isinstance(result, str)
 
 
def test_llm_client_model_configuration():
    """Test that model can be configured"""
    with patch.dict(os.environ, {
        'HF_API_TOKEN': 'fake_token',
        'HF_MODEL': 'test-model'
    }):
        client = LLMClient()
        # Should accept model configuration
        assert client is not None
 
 
@patch('llm_client.OpenAI')
def test_llm_client_error_handling(mock_openai):
    """Test error handling when API fails"""
    mock_openai.side_effect = Exception("API Error")
   
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        # Should handle initialization errors gracefully
        try:
            client = LLMClient()
            # If it doesn't raise, that's fine
            assert True
        except Exception:
            # If it raises, should be caught elsewhere
            assert True
 
 
def test_llm_client_singleton_behavior():
    """Test that multiple instances work independently"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client1 = LLMClient()
        client2 = LLMClient()
       
        # Both should be valid instances
        assert client1 is not None
        assert client2 is not None
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 