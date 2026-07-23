"""
Gemini AI Integration for Agricultural Decision Support
Uses Google's Gemini AI for intelligent crop recommendations
"""

import httpx
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class GeminiAI:
    """
    Google Gemini AI client for agricultural intelligence
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini AI client
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
    
    async def generate_crop_recommendation(
        self,
        soil_data: Dict,
        weather_data: Optional[Dict] = None,
        field_data: Optional[Dict] = None,
        current_crop: Optional[str] = None
    ) -> Dict:
        """
        Generate AI-powered crop recommendations
        
        Args:
            soil_data: Soil analysis data (pH, moisture, fertility, etc.)
            weather_data: Weather forecast data
            field_data: Field information (location, size, history)
            current_crop: Currently planted crop (if any)
        
        Returns:
            AI-generated recommendations with reasoning
        """
        
        # Build comprehensive prompt
        prompt = self._build_crop_recommendation_prompt(
            soil_data, weather_data, field_data, current_crop
        )
        
        try:
            response = await self._call_gemini(prompt)
            return {
                'recommendation': response,
                'source': 'Google Gemini AI',
                'confidence': 'high',
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Gemini AI error: {e}")
            raise
    
    async def analyze_field_health(
        self,
        ndvi_data: Dict,
        soil_data: Dict,
        weather_data: Optional[Dict] = None
    ) -> Dict:
        """
        AI analysis of field health and issues
        
        Args:
            ndvi_data: NDVI satellite data
            soil_data: Soil properties
            weather_data: Recent weather conditions
        
        Returns:
            Health analysis with potential issues and solutions
        """
        
        prompt = self._build_health_analysis_prompt(ndvi_data, soil_data, weather_data)
        
        try:
            response = await self._call_gemini(prompt)
            return {
                'analysis': response,
                'source': 'Google Gemini AI',
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Gemini AI health analysis error: {e}")
            raise
    
    async def suggest_crop_rotation(
        self,
        field_history: List[Dict],
        soil_data: Dict,
        climate_zone: str
    ) -> Dict:
        """
        Suggest optimal crop rotation strategy
        
        Args:
            field_history: Previous crops and yields
            soil_data: Current soil conditions
            climate_zone: Climate classification
        
        Returns:
            Crop rotation recommendations
        """
        
        prompt = self._build_rotation_prompt(field_history, soil_data, climate_zone)
        
        try:
            response = await self._call_gemini(prompt)
            return {
                'rotation_plan': response,
                'source': 'Google Gemini AI',
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Gemini AI rotation suggestion error: {e}")
            raise
    
    async def optimize_fertilizer_plan(
        self,
        soil_data: Dict,
        crop_type: str,
        target_yield: Optional[float] = None
    ) -> Dict:
        """
        Generate optimal fertilizer application plan
        
        Args:
            soil_data: Soil nutrient levels
            crop_type: Crop being grown
            target_yield: Desired yield (optional)
        
        Returns:
            Fertilizer recommendations with timing and amounts
        """
        
        prompt = self._build_fertilizer_prompt(soil_data, crop_type, target_yield)
        
        try:
            response = await self._call_gemini(prompt)
            return {
                'fertilizer_plan': response,
                'source': 'Google Gemini AI',
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            logger.error(f"Gemini AI fertilizer optimization error: {e}")
            raise
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini AI API"""
        url = f"{self.BASE_URL}?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']
            
            raise ValueError("No response generated from Gemini AI")
    
    def _build_crop_recommendation_prompt(
        self,
        soil_data: Dict,
        weather_data: Optional[Dict],
        field_data: Optional[Dict],
        current_crop: Optional[str]
    ) -> str:
        """Build prompt for crop recommendations"""
        
        prompt = """You are an expert agricultural advisor with deep knowledge of precision farming, soil science, and crop management. 

Analyze the following data and provide detailed crop recommendations:

SOIL CONDITIONS:
"""
        # Add soil data
        if 'soil_properties' in soil_data:
            props = soil_data['soil_properties']
            prompt += f"- pH: {props.get('ph', 'N/A')}\n"
            prompt += f"- Organic Carbon: {props.get('organic_carbon', 'N/A')} g/kg\n"
            prompt += f"- Nitrogen: {props.get('nitrogen', 'N/A')} g/kg\n"
            prompt += f"- Texture: {props.get('texture', 'N/A')}\n"
            prompt += f"- Clay: {props.get('clay_content', 'N/A')}%\n"
            prompt += f"- Sand: {props.get('sand_content', 'N/A')}%\n"
        
        if 'soil_moisture' in soil_data:
            moisture = soil_data['soil_moisture']
            prompt += f"- Soil Moisture: {moisture.get('soil_moisture_0_5cm', 'N/A')} m³/m³\n"
        
        if 'fertility_index' in soil_data:
            prompt += f"- Fertility Index: {soil_data['fertility_index']:.2f} (0-1 scale)\n"
        
        prompt += "\n"
        
        # Add weather data if available
        if weather_data:
            prompt += "WEATHER CONDITIONS:\n"
            if 'temperature' in weather_data:
                prompt += f"- Temperature: {weather_data['temperature']}°C\n"
            if 'precipitation' in weather_data:
                prompt += f"- Precipitation: {weather_data['precipitation']}mm\n"
            prompt += "\n"
        
        # Add field data if available
        if field_data:
            prompt += "FIELD INFORMATION:\n"
            if 'location' in field_data:
                loc = field_data['location']
                prompt += f"- Location: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}\n"
            if 'area' in field_data:
                prompt += f"- Area: {field_data['area']} hectares\n"
            if current_crop:
                prompt += f"- Current Crop: {current_crop}\n"
            prompt += "\n"
        
        # Add crop suitability if available
        if 'suitability' in soil_data:
            prompt += "CROP SUITABILITY ANALYSIS:\n"
            for crop, suitability in soil_data['suitability'].items():
                prompt += f"- {crop}: {suitability}\n"
            prompt += "\n"
        
        prompt += """
Based on this comprehensive data, please provide:

1. TOP 3 RECOMMENDED CROPS (with detailed reasoning for each)
2. SPECIFIC MANAGEMENT PRACTICES for each recommended crop
3. POTENTIAL CHALLENGES and how to address them
4. EXPECTED YIELD ESTIMATES (if possible)
5. CROP ROTATION suggestions for long-term soil health
6. FERTILIZER REQUIREMENTS for optimal growth
7. IRRIGATION RECOMMENDATIONS based on soil moisture

Format your response clearly with headers and bullet points. Be specific and actionable.
"""
        
        return prompt
    
    def _build_health_analysis_prompt(
        self,
        ndvi_data: Dict,
        soil_data: Dict,
        weather_data: Optional[Dict]
    ) -> str:
        """Build prompt for health analysis"""
        
        prompt = """You are an expert agronomist analyzing crop health using satellite data and environmental factors.

SATELLITE DATA (NDVI):
"""
        prompt += f"- Current NDVI: {ndvi_data.get('estimated_ndvi', 'N/A')}\n"
        prompt += f"- Health Status: {ndvi_data.get('health_status', 'N/A')}\n"
        prompt += f"- Scenes Analyzed: {ndvi_data.get('scenes_found', 'N/A')}\n"
        prompt += f"- Cloud Coverage: {ndvi_data.get('latest_cloud_cover', 'N/A')}%\n\n"
        
        prompt += "SOIL CONDITIONS:\n"
        if 'soil_properties' in soil_data:
            props = soil_data['soil_properties']
            prompt += f"- pH: {props.get('ph', 'N/A')}\n"
            prompt += f"- Organic Matter: {props.get('organic_carbon', 'N/A')} g/kg\n"
            prompt += f"- Texture: {props.get('texture', 'N/A')}\n"
        
        if 'soil_moisture' in soil_data:
            moisture = soil_data['soil_moisture']
            prompt += f"- Soil Moisture: {moisture.get('soil_moisture_0_5cm', 'N/A')} m³/m³\n"
        
        prompt += "\n"
        
        if weather_data:
            prompt += "RECENT WEATHER:\n"
            prompt += f"- Temperature: {weather_data.get('temperature', 'N/A')}°C\n"
            prompt += f"- Precipitation: {weather_data.get('precipitation', 'N/A')}mm\n\n"
        
        prompt += """
Provide a detailed health analysis including:

1. OVERALL FIELD HEALTH ASSESSMENT
2. POTENTIAL ISSUES (stress, disease, nutrient deficiency, etc.)
3. ROOT CAUSE ANALYSIS (why these issues are occurring)
4. IMMEDIATE ACTIONS NEEDED (priority order)
5. LONG-TERM MANAGEMENT STRATEGIES
6. MONITORING RECOMMENDATIONS (what to watch for)

Be specific and provide actionable recommendations.
"""
        
        return prompt
    
    def _build_rotation_prompt(
        self,
        field_history: List[Dict],
        soil_data: Dict,
        climate_zone: str
    ) -> str:
        """Build prompt for crop rotation suggestions"""
        
        prompt = """You are an expert in sustainable agriculture and crop rotation strategies.

FIELD HISTORY:
"""
        for i, record in enumerate(field_history, 1):
            prompt += f"Year {i}: {record.get('crop', 'N/A')} - Yield: {record.get('yield', 'N/A')}\n"
        
        prompt += f"\nCLIMATE ZONE: {climate_zone}\n\n"
        
        prompt += "CURRENT SOIL STATUS:\n"
        if 'soil_properties' in soil_data:
            props = soil_data['soil_properties']
            prompt += f"- pH: {props.get('ph', 'N/A')}\n"
            prompt += f"- Organic Carbon: {props.get('organic_carbon', 'N/A')} g/kg\n"
            prompt += f"- Nitrogen: {props.get('nitrogen', 'N/A')} g/kg\n"
        
        prompt += """
Design an optimal 4-year crop rotation plan that:

1. IMPROVES SOIL HEALTH over time
2. BREAKS PEST AND DISEASE CYCLES
3. BALANCES NUTRIENT REQUIREMENTS
4. MAXIMIZES ECONOMIC RETURNS
5. INCLUDES COVER CROPS where appropriate

For each year, specify:
- Main crop and variety recommendations
- Expected benefits to soil and pest management
- Fertilizer and amendment needs
- Estimated returns

Explain the reasoning behind the rotation sequence.
"""
        
        return prompt
    
    def _build_fertilizer_prompt(
        self,
        soil_data: Dict,
        crop_type: str,
        target_yield: Optional[float]
    ) -> str:
        """Build prompt for fertilizer optimization"""
        
        prompt = f"""You are an expert in soil fertility and nutrient management.

CROP: {crop_type}
"""
        if target_yield:
            prompt += f"TARGET YIELD: {target_yield} tons/hectare\n"
        
        prompt += "\nSOIL NUTRIENT STATUS:\n"
        if 'soil_properties' in soil_data:
            props = soil_data['soil_properties']
            prompt += f"- pH: {props.get('ph', 'N/A')}\n"
            prompt += f"- Organic Carbon: {props.get('organic_carbon', 'N/A')} g/kg\n"
            prompt += f"- Nitrogen: {props.get('nitrogen', 'N/A')} g/kg\n"
            prompt += f"- CEC: {props.get('cation_exchange', 'N/A')} cmol/kg\n"
        
        prompt += """
Develop a precise fertilizer application plan including:

1. NPK REQUIREMENTS
   - Total nitrogen needed (kg/ha)
   - Phosphorus requirements (kg/ha)
   - Potassium requirements (kg/ha)

2. APPLICATION TIMING
   - Pre-plant applications
   - Side-dress timing and amounts
   - Foliar applications if needed

3. FERTILIZER PRODUCTS
   - Specific product recommendations
   - Application rates and methods

4. MICRONUTRIENTS
   - Deficiency risk assessment
   - Micronutrient recommendations

5. ORGANIC AMENDMENTS
   - Compost or manure recommendations
   - Expected long-term benefits

6. COST ESTIMATES and return on investment

Provide specific, actionable recommendations with quantities and timing.
"""
        
        return prompt
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Convenience functions
async def get_ai_crop_recommendation(
    api_key: str,
    soil_data: Dict,
    weather_data: Optional[Dict] = None,
    field_data: Optional[Dict] = None,
    current_crop: Optional[str] = None
) -> Dict:
    """Get AI-powered crop recommendations"""
    ai = GeminiAI(api_key)
    return await ai.generate_crop_recommendation(
        soil_data, weather_data, field_data, current_crop
    )


async def get_ai_field_analysis(
    api_key: str,
    ndvi_data: Dict,
    soil_data: Dict,
    weather_data: Optional[Dict] = None
) -> Dict:
    """Get AI-powered field health analysis"""
    ai = GeminiAI(api_key)
    return await ai.analyze_field_health(ndvi_data, soil_data, weather_data)


async def get_ai_rotation_plan(
    api_key: str,
    field_history: List[Dict],
    soil_data: Dict,
    climate_zone: str
) -> Dict:
    """Get AI-powered crop rotation plan"""
    ai = GeminiAI(api_key)
    return await ai.suggest_crop_rotation(field_history, soil_data, climate_zone)


async def get_ai_fertilizer_plan(
    api_key: str,
    soil_data: Dict,
    crop_type: str,
    target_yield: Optional[float] = None
) -> Dict:
    """Get AI-powered fertilizer plan"""
    ai = GeminiAI(api_key)
    return await ai.optimize_fertilizer_plan(soil_data, crop_type, target_yield)
