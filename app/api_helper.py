import os
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image
import io

# Load environment variables
load_dotenv(dotenv_path="config/.env")

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_plant(image_bytes, max_retries=3):
    """
    Send leaf image to Gemini and get plant + disease analysis.
    Auto-retries if server is busy (503).
    """
    
    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    You are a plant disease expert. Analyze this leaf image carefully.
    
    Provide your response in this EXACT format:
    
    CROP: [plant name — use common local names like Brinjal, Lady Finger, Capsicum, Coriander if applicable, otherwise standard English name]
    DISEASE: [disease name or "Healthy" or "Unknown"]
    CONFIDENCE: [0-100]%
    TREATMENT: [brief treatment recommendation, max 2 sentences]
    
    Rules:
    - If the plant is healthy, say "Healthy" and give care tips.
    - If you cannot identify the plant, say "Unknown".
    - For CROP, prefer the name most commonly used in India/South Asia if it differs from English.
    - Keep TREATMENT short, practical, and farmer-friendly.
    
    Example response:
    CROP: Brinjal
    DISEASE: Healthy
    CONFIDENCE: 95%
    TREATMENT: No treatment needed. Continue regular watering and sunlight.
    """
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, image]
            )
            
            # Parse response
            text = response.text
            result = parse_response(text)
            return result
            
        except Exception as e:
            last_error = str(e)
            
            # If it's a 503 (server busy), wait and retry
            if "503" in last_error or "UNAVAILABLE" in last_error.upper():
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Wait 5s, 10s, 15s
                    continue
                else:
                    return {
                        "crop": "Server Busy",
                        "disease": "Please try again in a moment",
                        "confidence": 0,
                        "treatment": "Google's AI server is experiencing high demand. Wait 1-2 minutes and click 'Diagnose Plant' again."
                    }
            
            # If it's a 429 (rate limit), give specific message
            elif "429" in last_error or "RESOURCE_EXHAUSTED" in last_error.upper():
                return {
                    "crop": "Daily Limit Reached",
                    "disease": "You've used all free requests for today",
                    "confidence": 0,
                    "treatment": "Gemini free tier resets at midnight Pacific Time. Try again tomorrow or upgrade to a paid API key."
                }
            
            # Other errors
            else:
                return {
                    "crop": "Error",
                    "disease": "Something went wrong",
                    "confidence": 0,
                    "treatment": f"Details: {last_error[:200]}. Please try again."
                }
    
    # Fallback (shouldn't reach here)
    return {
        "crop": "Unknown",
        "disease": "Unknown",
        "confidence": 0,
        "treatment": "Please try again."
    }


def parse_response(text):
    """
    Parse Gemini's response into structured dict.
    """
    result = {
        "crop": "Unknown",
        "disease": "Unknown",
        "confidence": 0,
        "treatment": "No treatment info available."
    }
    
    lines = text.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith("CROP:"):
            result["crop"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DISEASE:"):
            result["disease"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("CONFIDENCE:"):
            conf_str = line.split(":", 1)[1].strip().replace("%", "")
            try:
                result["confidence"] = int(conf_str)
            except:
                result["confidence"] = 0
        elif line.upper().startswith("TREATMENT:"):
            result["treatment"] = line.split(":", 1)[1].strip()
    
    # If treatment spans multiple lines, get rest
    if "TREATMENT:" in text.upper():
        treatment_part = text.upper().split("TREATMENT:")[1]
        remaining = treatment_part.split("CONFIDENCE")[0] if "CONFIDENCE" in treatment_part else treatment_part
        result["treatment"] = remaining.strip().replace("\n", " ")
    
    return result


def check_api_status():
    """
    Quick test to check if API key works.
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="Say 'OK' if you can read this."
        )
        return True, response.text
    except Exception as e:
        return False, str(e)