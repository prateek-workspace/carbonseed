import httpx
from typing import Optional
from app.config import settings


class GeminiService:
    """
    Service to interact with hosted Gemini API for ML-powered analytics.
    Used for anomaly detection, predictive maintenance, and insights.
    """
    
    def __init__(self):
        self.base_url = settings.GEMINI_API_URL
        self.timeout = 30.0
    
    async def generate_insight(self, prompt_text: str) -> Optional[str]:
        """
        Call Gemini API to generate insights from data.
        
        Args:
            prompt_text: The prompt text to send to Gemini
            
        Returns:
            Generated text response or None if error
        """
        if not self.base_url:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={"text": prompt_text}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("text") or data.get("response")
                else:
                    print(f"Gemini API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    async def analyze_anomaly(self, sensor_data: dict) -> Optional[dict]:
        """
        Analyze sensor data for anomalies using Gemini.
        
        Args:
            sensor_data: Dictionary with sensor readings
            
        Returns:
            Analysis result with anomaly detection
        """
        prompt = f"""Analyze this industrial sensor data for anomalies:

Temperature: {sensor_data.get('temperature')}°C
Gas Index: {sensor_data.get('gas_index')}
Vibration X: {sensor_data.get('vibration_x')}
Vibration Y: {sensor_data.get('vibration_y')}
Vibration Z: {sensor_data.get('vibration_z')}
Humidity: {sensor_data.get('humidity')}%
Power: {sensor_data.get('power_consumption')} kWh

Respond with JSON format:
{{
  "anomaly_detected": true/false,
  "severity": "info/warning/critical",
  "issue": "description of issue",
  "recommendation": "what to do"
}}
"""
        
        response = await self.generate_insight(prompt)
        
        if response:
            try:
                import json
                return json.loads(response)
            except:
                return {
                    "anomaly_detected": False,
                    "severity": "info",
                    "issue": "Unable to parse AI response",
                    "recommendation": response
                }
        
        return None
    
    async def predict_maintenance(self, device_history: list) -> Optional[str]:
        """
        Predict maintenance needs based on device history.
        
        Args:
            device_history: List of recent sensor readings
            
        Returns:
            Maintenance prediction text
        """
        # Format history for prompt
        history_text = "\n".join([
            f"Time: {r.get('timestamp')}, Temp: {r.get('temperature')}, Vibration: {r.get('vibration_x')}"
            for r in device_history[:10]
        ])
        
        prompt = f"""Based on this device sensor history, predict maintenance needs:

{history_text}

Provide a brief maintenance recommendation."""
        
        return await self.generate_insight(prompt)
    
    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        if not self.base_url:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False


# Singleton instance
gemini_service = GeminiService()
