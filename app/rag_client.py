import logging
import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)

class RAGClientError(Exception):
    """Base exception for RAG client errors"""
    pass

class RAGServiceUnavailableError(RAGClientError):
    """Raised when RAG service is not available"""
    pass

class RAGTimeoutError(RAGClientError):
    """Raised when RAG service times out"""
    pass

def query_rag(
    message: str,
    top_k: int = 5,
    use_reranking: bool = True,
    rag_service_url: str = "http://localhost:8000",
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Query the RAG service via HTTP.
    
    Args:
        message: The user's query message
        top_k: Number of top results to return
        use_reranking: Whether to use reranking
        rag_service_url: Base URL of the RAG service
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'reply' and 'sources' keys
        
    Raises:
        RAGServiceUnavailableError: If the service is not available
        RAGTimeoutError: If the request times out
        RAGClientError: For other client errors
    """
    url = f"{rag_service_url}/ask"
    
    payload = {
        "query": message,
        "top_k": top_k,
        "use_reranking": use_reranking
    }
    
    try:
        logger.info(f"Querying RAG service at {url} with message: {message[:50]}...")
        response = requests.post(
            url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Map RAG service response format to Flask API format
        return {
            "reply": result.get("response", ""),
            "sources": result.get("sources", [])
        }
        
    except ConnectionError as e:
        logger.error(f"Failed to connect to RAG service at {rag_service_url}: {str(e)}")
        raise RAGServiceUnavailableError(f"RAG service is not available at {rag_service_url}") from e
    
    except Timeout as e:
        logger.error(f"RAG service timeout after {timeout}s: {str(e)}")
        raise RAGTimeoutError(f"RAG service timeout after {timeout}s") from e
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"RAG service HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 503:
            raise RAGServiceUnavailableError(f"RAG service returned 503: {e.response.text}") from e
        raise RAGClientError(f"RAG service HTTP error: {e.response.status_code}") from e
    
    except RequestException as e:
        logger.error(f"RAG service request error: {str(e)}")
        raise RAGClientError(f"RAG service request error: {str(e)}") from e
    
    except Exception as e:
        logger.error(f"Unexpected error querying RAG service: {str(e)}")
        raise RAGClientError(f"Unexpected error: {str(e)}") from e


def check_rag_health(
    rag_service_url: str = "http://localhost:8000",
    timeout: int = 5
) -> Dict[str, Any]:
    """
    Check the health of the RAG service.
    
    Args:
        rag_service_url: Base URL of the RAG service
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with health status information
    """
    url = f"{rag_service_url}/health"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return {
            "status": "healthy",
            "rag_service": response.json()
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

