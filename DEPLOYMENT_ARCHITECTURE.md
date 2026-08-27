# FarmGuard Animal Heat-Risk Model - Deployment Architecture

## Architecture Decision

**CRITICAL CONSTRAINT:** The Python ML model (scikit-learn/joblib) cannot run directly in Angular (TypeScript/JavaScript) or Supabase Edge Functions (Deno/TypeScript).

## Recommended Architecture for Hackathon

```
┌─────────────────┐
│  Angular UI     │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/REST API
         ↓
┌─────────────────┐
│ Supabase Edge   │  OR  ┌─────────────────┐
│ Function (TS)   │────→│ Python Backend  │
│ (Optional)      │     │ (FastAPI/Flask) │
└────────┬────────┘     └────────┬────────┘
         │                        │
         ↓                        ↓
┌─────────────────┐     ┌─────────────────┐
│ Python Inference│     │ Python Inference│
│ Service         │     │ Service         │
│ (FastAPI)       │     │ (FastAPI)       │
└────────┬────────┘     └────────┬────────┘
         │                        │
         ↓                        ↓
┌─────────────────┐     ┌─────────────────┐
│ Random Forest   │     │ Random Forest   │
│ Model (scikit-  │     │ Model (scikit-  │
│ learn)          │     │ learn)          │
└─────────────────┘     └─────────────────┘
```

## Option A: Direct Python Service (Recommended for Hackathon)

**Simplest for hackathon:**
- Angular directly calls Python FastAPI service
- Python service loads model artifacts and returns predictions
- Supabase used only for data storage (not for inference)

**Pros:**
- Simple to implement
- Fast development
- Direct control over inference logic
- Easy to debug

**Cons:**
- Two separate services to deploy
- Need to manage Python service separately

**Implementation:**
```python
# FastAPI service example
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from inference import AnimalHeatRiskPredictor

app = FastAPI()
predictor = AnimalHeatRiskPredictor()

class AnimalInput(BaseModel):
    species: str
    breed: str
    age_years: float
    weight_kg: float
    sex: str
    physiological_stage: str
    health_status: str
    latitude: float
    longitude: float
    elevation_m: float
    climate_zone: str
    temperature_c: float
    humidity_percent: float
    wind_speed_m_s: float
    solar_radiation_w_m2: float

@app.post("/predict")
async def predict_risk(input: AnimalInput):
    try:
        result = predictor.predict(input.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Option B: Supabase Edge Function + Python Service

**More integrated approach:**
- Angular calls Supabase Edge Function
- Edge Function calls Python service
- Python service returns predictions to Edge Function
- Edge Function returns to Angular

**Pros:**
- Single Supabase integration point
- Can add Supabase JWT auth at Edge Function level
- Centralized API gateway

**Cons:**
- More complex
- Additional network hop
- Edge Function limitations

**Supabase JWT Authorization Placement:**
```
Angular (with JWT)
    ↓ (JWT in Authorization header)
Supabase Edge Function (validates JWT)
    ↓ (validated request)
Python Inference Service (trusts Edge Function)
```

**Security Note:**
- Supabase JWT validation should happen at the Edge Function layer
- Python service can trust requests from Edge Function (internal network)
- Do NOT trust client-provided authorization directly

## Deployment Recommendations

### For Hackathon (Option A - Direct Python Service)

1. **Deploy Python Service:**
   - Use FastAPI for quick development
   - Deploy to Render, Railway, or similar
   - Or run locally during hackathon demo

2. **Angular Integration:**
   ```typescript
   // Angular service
   async predictRisk(input: AnimalInput): Promise<Prediction> {
     const response = await fetch('https://your-python-service.com/predict', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(input)
     });
     return response.json();
   }
   ```

3. **Supabase Integration:**
   - Use Supabase only for data storage
   - Store animal data, weather data, predictions in Supabase
   - Angular reads/writes to Supabase directly

### For Production (Option B - Edge Function + Python Service)

1. **Add Supabase Edge Function:**
   ```typescript
   // Supabase Edge Function
   import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
   
   serve(async (req) => {
     // Validate JWT
     const authHeader = req.headers.get('Authorization')
     // ... JWT validation logic
     
     // Call Python service
     const pythonResponse = await fetch('http://python-service/predict', {
       method: 'POST',
       body: await req.text()
     })
     
     return pythonResponse
   })
   ```

2. **Python Service:**
   - Same as Option A
   - Deploy to internal network or VPC
   - Only accept requests from Edge Function

## Security Considerations

1. **JWT Validation:**
   - Validate Supabase JWT at Edge Function layer
   - Python service trusts Edge Function (internal)
   - Never trust client-provided authorization directly

2. **Input Validation:**
   - Python service validates all inputs
   - Reject unsupported species
   - Validate numeric ranges
   - Check for null/missing fields

3. **Rate Limiting:**
   - Implement rate limiting at Edge Function
   - Prevent abuse of inference service

4. **Model Artifacts:**
   - Never expose model files directly
   - Keep model artifacts private
   - Use environment variables for paths

5. **Request Size:**
   - Limit batch prediction size
   - Implement reasonable input limits

## Resource Requirements

**Python Service:**
- CPU: 1-2 cores sufficient
- RAM: 512MB - 1GB (model is 16.64 MB)
- Storage: ~50MB for model artifacts
- Network: Low bandwidth per request

**FastAPI Dependencies:**
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
scikit-learn>=1.2.0
pandas>=1.5.0
numpy>=1.23.0
joblib>=1.2.0
```

## Conclusion

**For Hackathon:** Use Option A (Direct Python Service) - simpler and faster to implement.

**For Production:** Use Option B (Edge Function + Python Service) - better security and integration.

The model is deployable as a small Python HTTP service with minimal resource requirements.
