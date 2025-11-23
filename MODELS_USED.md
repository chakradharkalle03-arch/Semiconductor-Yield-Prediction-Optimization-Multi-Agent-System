# Models Used in the System

This document explains the AI/ML models and algorithms used in the Semiconductor Yield Prediction & Optimization Multi-Agent System.

## 🤖 Primary Model: Mistral-7B-Instruct

### Model Details
- **Model Name**: `mistralai/Mistral-7B-Instruct-v0.1`
- **Provider**: HuggingFace Inference API
- **Type**: Large Language Model (LLM)
- **Parameters**: 7 Billion
- **Purpose**: Yield prediction and analysis

### How It's Used
The **Prediction Agent** uses this model to:
1. Analyze wafer map data, metrology measurements, and EDA logs
2. Consider process parameters (temperature, etch time, exposure dose)
3. Predict die yield percentage with confidence scores
4. Identify key factors affecting yield

### Model Configuration
```python
HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.1",
    temperature=0.3,        # Low temperature for consistent predictions
    max_new_tokens=512,     # Sufficient for detailed analysis
    timeout=30              # API timeout
)
```

### Model Prompt Structure
The model receives structured prompts with:
- **System Prompt**: Defines the agent as an expert semiconductor yield prediction system
- **Human Prompt**: Contains actual data (wafer maps, metrology, process parameters)
- **Expected Output**: JSON with predicted_yield, confidence, and factors

## 🔄 Fallback Model: Rule-Based Algorithm

### When It's Used
The system automatically falls back to a rule-based prediction algorithm when:
- HuggingFace API key is not configured
- API connection fails
- Model initialization fails
- LLM response parsing fails

### Algorithm Details
The rule-based system uses:
1. **Base Yield**: Starts at 90%
2. **Quality Score Adjustment**: Multiplies base yield by quality score
3. **Parameter Deviation Penalties**:
   - Temperature deviation from optimal (200°C)
   - Etch time deviation from optimal (45s)
   - Exposure dose deviation from optimal (50 mJ/cm²)
4. **EDA Error Penalties**: Reduces yield based on error count
5. **Defect Density Penalties**: Adjusts yield based on wafer defect density

### Formula (Simplified)
```
predicted_yield = base_yield * quality_score 
                - temperature_penalty 
                - etch_penalty 
                - dose_penalty 
                - eda_error_penalty 
                - defect_penalty
```

## 🧠 Optimization Algorithm

### Method: Grid Search with Heuristic Optimization

The **Optimization Agent** uses:
- **Grid Search**: Tests parameter combinations within defined ranges
- **Heuristic Evaluation**: Estimates yield for each combination
- **Best Selection**: Chooses parameters with highest predicted yield

### Optimization Parameters
- **Temperature Range**: 195-205°C (increments of 0.5°C)
- **Etch Time Range**: 40-50s (increments of 0.2s)
- **Exposure Dose Range**: 45-55 mJ/cm² (increments of 0.3 mJ/cm²)

### Evaluation Function
Uses the same yield prediction logic (LLM or rule-based) to evaluate each parameter combination.

## 📊 Data Processing Models

### Data Agent Processing
- **Statistical Analysis**: Mean, standard deviation, uniformity calculations
- **Quality Scoring**: Composite score based on multiple factors
- **Data Normalization**: Prepares data for model consumption

### No Machine Learning Models Used For:
- Data preprocessing (uses statistical methods)
- Optimization (uses grid search)
- Recommendations (uses rule-based logic)

## 🔧 Technology Stack for Models

### LangChain Integration
- **HuggingFaceEndpoint**: Wrapper for HuggingFace Inference API
- **ChatPromptTemplate**: Structured prompt management
- **LLMChain**: Chains prompts with model calls

### Model Access
- **API-Based**: Uses HuggingFace Inference API (no local model loading)
- **On-Demand**: Model is called only when prediction is needed
- **Stateless**: No model state is maintained between requests

## 📈 Model Performance

### LLM Mode (Mistral-7B-Instruct)
- **Advantages**:
  - Understands complex relationships
  - Can reason about multiple factors simultaneously
  - Provides natural language explanations
- **Limitations**:
  - Requires API key
  - Network dependency
  - Response parsing complexity

### Rule-Based Mode
- **Advantages**:
  - Always available (no API dependency)
  - Fast and deterministic
  - No external dependencies
- **Limitations**:
  - Less sophisticated reasoning
  - Fixed rules may not capture all scenarios
  - Limited adaptability

## 🔐 Model Security & Privacy

- **API Keys**: Stored in environment variables (not in code)
- **Data Privacy**: Data sent to HuggingFace API (check their privacy policy)
- **Fallback**: System works without API key using rule-based method
- **No Local Models**: No model files stored locally

## 🚀 Future Model Enhancements

Potential improvements:
1. **Fine-Tuned Models**: Train on semiconductor-specific data
2. **Ensemble Methods**: Combine multiple models for better accuracy
3. **Local Models**: Use smaller models that can run locally
4. **Structured Output**: Use model features for JSON-structured responses
5. **Custom Models**: Train domain-specific models on historical yield data

## 📝 Summary

| Component | Model/Algorithm | Type |
|-----------|----------------|------|
| **Prediction** | Mistral-7B-Instruct (via HuggingFace) | LLM |
| **Prediction (Fallback)** | Rule-based algorithm | Heuristic |
| **Optimization** | Grid search + heuristic evaluation | Search algorithm |
| **Recommendation** | Rule-based logic | Heuristic |
| **Data Processing** | Statistical methods | Traditional |

---

**Note**: The system is designed to work with or without the LLM. The rule-based fallback ensures the system is always functional, making it production-ready regardless of API availability.

