from api_helper import check_api_status

status, message = check_api_status()
print(f"Status: {status}")
print(f"Message: {message}")