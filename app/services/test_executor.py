import json
import time
import httpx

async def execute_test(test_case):
    """
    Execute a test case synchronously
    Returns: {
        'status': 'success'|'failed'|'error',
        'actual_status': int,
        'actual_body': str,
        'error_message': str,
        'duration_ms': int
    }
    """
    try:
        # Parse headers and body
        headers = {}
        if test_case.headers:
            headers = json.loads(test_case.headers)

        # Prepare request
        request_kwargs = {
            'method': test_case.method,
            'url': test_case.url,
            'headers': headers,
            'timeout': 30.0
        }

        # Add body for methods that typically have body
        if test_case.body and test_case.method.upper() in ['POST', 'PUT', 'PATCH']:
            try:
                # Try to parse as JSON first
                body_data = json.loads(test_case.body)
                request_kwargs['json'] = body_data
            except json.JSONDecodeError:
                # Fall back to raw text
                request_kwargs['content'] = test_case.body

        # Execute request
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.request(**request_kwargs)

        duration_ms = int((time.time() - start_time) * 1000)

        # Determine result
        success = (
            response.status_code == test_case.expected_status and
            test_case.expected_body is None
        )

        # Also check body if expected is provided
        if test_case.expected_body is not None:
            try:
                expected_json = json.loads(test_case.expected_body)
                actual_json = response.json()
                success = success and actual_json == expected_json
            except (json.JSONDecodeError, Exception):
                # If JSON parsing fails, compare as strings
                success = success and response.text == test_case.expected_body

        return {
            'status': 'success' if success else 'failed',
            'actual_status': response.status_code,
            'actual_body': response.text,
            'error_message': None,
            'duration_ms': duration_ms
        }

    except Exception as e:
        return {
            'status': 'error',
            'actual_status': None,
            'actual_body': None,
            'error_message': str(e),
            'duration_ms': int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        }