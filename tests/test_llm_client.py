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
 
 
def test_llm_client_initialization_with_token():
    """Test LLMClient initialization with token"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token_123'}, clear=True):
        with patch('llm_client.load_dotenv'):
            client = LLMClient()
            assert client is not None
            # Model can be from env or default
            assert client.model is not None
            assert client.timeout == 60
 
 
def test_llm_client_initialization_without_token():
    """Test LLMClient initialization without token"""
    with patch.dict(os.environ, {}, clear=True):
        with patch('llm_client.load_dotenv'):
            client = LLMClient()
            assert client is not None
            assert client.client is None
 
 
def test_llm_client_custom_model():
    """Test LLMClient with custom model"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client = LLMClient(model="custom-model", timeout=120)
        assert client.model == "custom-model"
        assert client.timeout == 120
 
 
def test_llm_client_model_from_env():
    """Test LLMClient uses HF_MODEL env variable"""
    with patch.dict(os.environ, {
        'HF_API_TOKEN': 'fake_token',
        'HF_MODEL': 'env-model'
    }):
        client = LLMClient()
        assert client.model == "env-model"
 
 
def test_llm_client_availability_with_token():
    """Test availability when token is set"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token_123'}):
        client = LLMClient()
        assert client.available() is True
 
 
def test_llm_client_availability_without_token():
    """Test availability when token is missing"""
    with patch.dict(os.environ, {}, clear=True):
        with patch('llm_client.load_dotenv'):
            client = LLMClient()
            assert client.available() is False
 
 
@patch('llm_client.OpenAI')
def test_llm_client_generate_success(mock_openai):
    """Test generate method with successful response"""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked LLM response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
   
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client = LLMClient()
        result = client.generate("Test prompt")
       
        assert result == "Mocked LLM response"
        mock_client.chat.completions.create.assert_called_once()
 
 
@patch('llm_client.OpenAI')
def test_llm_client_generate_with_params(mock_openai):
    """Test generate method with custom parameters"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
   
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client = LLMClient()
        result = client.generate("Test prompt", max_tokens=1000, temperature=0.5)
       
        assert result == "Response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['max_tokens'] == 1000
        assert call_args[1]['temperature'] == 0.5
 
 
def test_llm_client_generate_without_token():
    """Test generate returns None without token"""
    with patch.dict(os.environ, {}, clear=True):
        with patch('llm_client.load_dotenv'):
            client = LLMClient()
            result = client.generate("Test prompt")
            assert result is None
 
 
@patch('llm_client.OpenAI')
def test_llm_client_generate_exception_handling(mock_openai):
    """Test generate handles exceptions gracefully"""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
   
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}):
        client = LLMClient()
        result = client.generate("Test prompt")
        assert result is None
 
 
def test_llm_client_default_values():
    """Test default model and timeout values"""
    with patch.dict(os.environ, {'HF_API_TOKEN': 'fake_token'}, clear=True):
        with patch('llm_client.load_dotenv'):
            client = LLMClient()
            # Model can be from env (HF_MODEL) or default
            assert client.model is not None
            assert isinstance(client.model, str)
            assert client.timeout == 60
 
 
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
 
 
