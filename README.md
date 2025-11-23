# Semiconductor Yield Prediction & Optimization Multi-Agent System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0-orange.svg)](https://www.langchain.com/)
[![Node.js](https://img.shields.io/badge/Node.js-14+-brightgreen.svg)](https://nodejs.org/)

An advanced **Multi-Agent AI System** for semiconductor yield prediction and process optimization using LangChain, LangGraph, and modern web technologies.

## 🚀 Overview

This system revolutionizes semiconductor yield optimization by leveraging multiple specialized AI agents that work together to predict yield, optimize process parameters, and provide actionable recommendations. Instead of relying on single models or manual analysis, this system uses a team of intelligent agents, each expert in their domain, collaborating to deliver comprehensive insights.

### Key Advantages

- **Intelligent Analysis**: Uses advanced AI agents that understand process relationships, not just statistical patterns
- **Proactive Optimization**: Doesn't just predict yield - it tells you how to improve it with specific recommendations
- **Complete Workflow**: Upload data, get predictions, see optimizations, review recommendations, and download reports - all in one place
- **Real-World Ready**: Handles various data formats, works with incomplete datasets, and delivers results in seconds

### Cutting-Edge Technology

- **LangChain & LangGraph**: Orchestrates multiple specialized AI agents working in harmony
- **Multi-Agent Architecture**: Five specialized agents (Data, Prediction, Optimization, Recommendation, Report) collaborating intelligently
- **HuggingFace Integration**: Leverages state-of-the-art language models when available
- **Modern Stack**: FastAPI backend, Node.js/Express frontend, responsive 3-column UI

## 📋 Features

- **Yield Prediction**: Accurate yield forecasts based on process parameters and wafer data
- **Parameter Optimization**: Discovers optimal temperature, etch time, and exposure dose settings
- **Actionable Recommendations**: Specific, implementable advice with expected improvements
- **PDF Report Generation**: Professional reports suitable for stakeholders and documentation
- **Dataset Management**: Upload, organize, and analyze multiple datasets easily
- **3-Column Interface**: Clean, intuitive layout with all features accessible side-by-side

## 🏗️ Architecture

The system uses a **Multi-Agent Architecture** with five specialized agents:

1. **Data Agent**: Processes wafer maps, metrology data, and EDA logs
2. **Prediction Agent**: Forecasts yield using LLM or rule-based algorithms
3. **Optimization Agent**: Searches parameter space to find optimal settings
4. **Recommendation Agent**: Translates findings into actionable advice
5. **Report Agent**: Generates professional PDF documentation

The **Supervisor Agent** (using LangGraph) orchestrates all agents, ensuring they work in the correct order and synthesize their outputs into comprehensive results.

## 🤖 AI Models & Algorithms

**Primary Model:**
- **Mistral-7B-Instruct** (`mistralai/Mistral-7B-Instruct-v0.1`) - Advanced 7B parameter language model via HuggingFace Inference API for intelligent yield prediction and analysis

**Fallback System:**
- **Rule-Based Algorithm** - Sophisticated heuristic-based prediction that works without API dependencies, ensuring the system is always functional

**Optimization:**
- **Grid Search Algorithm** - Systematic parameter space exploration to find optimal temperature, etch time, and exposure dose settings

**Other Components:**
- Statistical analysis for data processing
- Rule-based logic for recommendations
- Heuristic evaluation for optimization

*See [MODELS_USED.md](MODELS_USED.md) for detailed model documentation.*

## 🛠️ Tech Stack

**Backend:**
- FastAPI - High-performance Python web framework
- LangChain - Agent framework for intelligent reasoning
- LangGraph - Workflow orchestration for multi-agent systems
- HuggingFace - State-of-the-art language models (Mistral-7B-Instruct)
- ReportLab - PDF generation
- Pandas, NumPy - Data processing

**Frontend:**
- Node.js/Express - Server and API proxy
- Vanilla JavaScript - Clean, fast frontend
- Chart.js - Data visualization
- Responsive CSS - Modern 3-column layout

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Modern web browser

### Quick Start

**1. Clone the repository:**
```bash
git clone https://github.com/chakradharkalle03-arch/Semiconductor-Yield-Prediction-Optimization-Multi-Agent-System.git
cd Semiconductor-Yield-Prediction-Optimization-Multi-Agent-System
```

**2. Set up Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
source venv/bin/activate     # On Linux/Mac

pip install -r requirements.txt
```

**3. Set up Frontend:**
```bash
cd frontend
npm install
```

**4. Configure Environment (Optional):**
Create a `.env` file in the `backend` folder:
```
HUGGINGFACE_API_KEY=your_key_here
```
*Note: The system works great without it using rule-based prediction.*

**5. Run the System:**
```bash
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python start_server.py

# Terminal 2 - Frontend
cd frontend
node server.js
```

**6. Open in Browser:**
Navigate to `http://localhost:3008`

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running quickly
- **[User Manual](USER_MANUAL.md)** - Complete usage instructions
- **[Multi-Agent System Explanation](MULTI_AGENT_SYSTEM.md)** - Technical architecture details
- **[Models Used](MODELS_USED.md)** - Detailed documentation of AI models and algorithms

## 🎯 Usage

1. **Upload Dataset**: Upload JSON or CSV files with your wafer data
2. **Select Dataset**: Choose from uploaded datasets in the dropdown
3. **Review Parameters**: Form auto-populates with dataset data (editable)
4. **Analyze Yield**: Click "Analyze Yield" to run the multi-agent analysis
5. **View Results**: See predictions, optimizations, and recommendations
6. **Download PDF**: Generate professional reports for documentation

## 📊 Example Workflow

```
Upload Dataset → Select Dataset → Review Parameters → Analyze Yield
                                                          ↓
                    View Results ← Download PDF Report
```

## 🔧 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/          # Supervisor agent (LangGraph)
│   │   ├── models/          # Pydantic schemas
│   │   └── services/        # Individual agents (Data, Prediction, etc.)
│   ├── data/                # Dataset storage
│   ├── start_server.py      # Server startup script
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/              # HTML, CSS, JavaScript
│   ├── server.js           # Node.js server
│   └── package.json        # Node dependencies
├── testdata/               # Test datasets
├── QUICK_START.md          # Quick start guide
├── USER_MANUAL.md          # User manual
└── MULTI_AGENT_SYSTEM.md   # Architecture documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available for use and modification.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
- Leverages [HuggingFace](https://huggingface.co/) for advanced AI capabilities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for the semiconductor manufacturing industry**

