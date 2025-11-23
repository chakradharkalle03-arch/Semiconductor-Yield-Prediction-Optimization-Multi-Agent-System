# Quick Start Guide

## Welcome to Semiconductor Yield Prediction & Optimization System

If you're working in semiconductor manufacturing, you know how critical yield optimization is. Every percentage point of yield improvement can translate to millions in revenue. But optimizing process parameters manually? That's time-consuming, error-prone, and frankly, not scalable.

That's where this system comes in. We've built something pretty special here - a multi-agent AI system that doesn't just predict yield, but actually helps you optimize it. Think of it as having a team of expert engineers working 24/7, analyzing your data and giving you actionable recommendations.

## Why This System is a Game Changer

Let me tell you what makes this different from other yield prediction tools out there:

**First, it's intelligent, not just statistical.** While traditional tools rely on historical averages and simple regression models, this system uses advanced AI agents that understand the relationships between process parameters, wafer characteristics, and yield outcomes. It's like the difference between reading a recipe and having a master chef guide you.

**Second, it's proactive, not reactive.** Instead of just telling you "your yield is 85%," it tells you "your yield is 85%, but if you adjust the exposure dose by 4%, you can get to 92%." And it explains why. That's the kind of insight that saves time and money.

**Third, it's a complete workflow, not just a prediction engine.** Upload your data, get predictions, see optimizations, review recommendations, and download professional PDF reports - all in one place. No switching between tools, no manual data transfer, no context switching.

**Finally, it's built for the real world.** We know your data comes in different formats. We know you might not have perfect datasets. We know you need results fast. That's why the system handles JSON, CSV, various data structures, and gives you results in seconds, not hours.

## The Cutting-Edge Technology Behind It

This isn't just another machine learning project. We're using some seriously advanced tech here:

**LangChain & LangGraph** - These aren't just buzzwords. LangChain gives us the ability to create intelligent agents that can reason about your data. LangGraph orchestrates multiple agents working together - like a conductor leading an orchestra, but each musician is an AI expert in their domain.

**Multi-Agent Architecture** - Instead of one monolithic model trying to do everything, we have specialized agents:
- A Data Agent that understands wafer maps and metrology data
- A Prediction Agent that forecasts yield using **Mistral-7B-Instruct LLM** (or rule-based fallback)
- An Optimization Agent that uses **grid search algorithms** to find the best parameters
- A Recommendation Agent that translates findings into actionable steps
- A Report Agent that generates professional documentation

Each agent is an expert in its field, and they collaborate to give you comprehensive insights. The Prediction Agent uses advanced AI when available, but always has a reliable fallback, so the system works whether you have an API key or not.

**HuggingFace Integration** - We leverage state-of-the-art language models for intelligent analysis. The system uses **Mistral-7B-Instruct** (7 billion parameters) via HuggingFace Inference API for advanced yield prediction. This model understands complex relationships between process parameters and yield outcomes. When the API isn't available, the system gracefully falls back to sophisticated rule-based algorithms that are still highly effective.

**Modern Web Architecture** - FastAPI backend for lightning-fast responses, Node.js frontend for smooth user experience, and a clean 3-column interface that puts everything you need right in front of you.

## What You Can Do With This System

- **Predict Yield** - Get accurate yield forecasts based on your process parameters and wafer data
- **Optimize Parameters** - Discover the best temperature, etch time, and exposure dose settings
- **Get Recommendations** - Receive specific, actionable advice on how to improve your yield
- **Generate Reports** - Create professional PDF reports for stakeholders and documentation
- **Manage Datasets** - Upload, organize, and analyze multiple datasets easily

## Getting Started

### Prerequisites

You'll need:
- Python 3.8 or higher
- Node.js 14 or higher
- A modern web browser

That's it. No complex setup, no obscure dependencies.

### Installation Steps

**1. Clone or download the project**

If you have the project files, you're good to go. If not, get them from your repository.

**2. Set up the Backend**

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
source venv/bin/activate     # On Linux/Mac

pip install -r requirements.txt
```

**3. Set up the Frontend**

```bash
cd frontend
npm install
```

**4. Configure Environment (Optional)**

If you have a HuggingFace API key, create a `.env` file in the `backend` folder:

```
HUGGINGFACE_API_KEY=your_key_here
```

Don't have one? No problem. The system works great without it using rule-based prediction.

### Running the System

**Start the Backend:**

```bash
cd backend
.\venv\Scripts\Activate.ps1
python start_server.py
```

You should see:
```
🚀 Starting Semiconductor Yield Prediction API Server...
📍 Server will be available at http://127.0.0.1:8006
📖 API docs at http://127.0.0.1:8006/docs
```

**Start the Frontend:**

Open a new terminal:

```bash
cd frontend
node server.js
```

You should see:
```
✅ Frontend server running on http://127.0.0.1:3008
```

**Open in Browser:**

Navigate to `http://localhost:3008` and you're ready to go!

## Your First Analysis

1. **Upload a Dataset** - In the left column, upload a JSON or CSV file with your wafer data
2. **Select the Dataset** - Choose it from the dropdown in the middle column
3. **Review Parameters** - The form will auto-populate with data from your dataset
4. **Click "Analyze Yield"** - Watch the magic happen
5. **View Results** - See predictions, optimizations, and recommendations in the right column
6. **Download PDF** - Get a professional report for your records

## Need Help?

Check out the **User Manual** for detailed instructions on using all features, or the **Multi-Agent System Explanation** if you want to understand how the AI agents work under the hood.

Welcome aboard! You're about to see yield optimization in a whole new way.

