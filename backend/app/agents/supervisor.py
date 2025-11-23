"""
Supervisor Agent using LangGraph to coordinate sub-agents
"""
from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from app.services.data_service import DataAgent
from app.services.prediction_service import PredictionAgent
from app.services.optimization_service import OptimizationAgent
from app.services.recommendation_service import RecommendationAgent
from app.services.report_service import ReportAgent
from app.models.schemas import (
    WaferData, ProcessParameters, AnalysisResponse,
    YieldPrediction, OptimizationResult, Recommendation
)


class AgentState(TypedDict):
    """State for the supervisor agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    wafer_data: WaferData
    current_parameters: ProcessParameters
    data_summary: dict
    prediction: Optional[YieldPrediction]
    optimization: Optional[OptimizationResult]
    recommendations: list[Recommendation]
    final_response: Optional[AnalysisResponse]


class SupervisorAgent:
    """Supervisor agent that coordinates all sub-agents"""
    
    def __init__(self, hf_api_key: str):
        self.data_agent = DataAgent()
        self.prediction_agent = PredictionAgent(hf_api_key)
        self.optimization_agent = OptimizationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.report_agent = ReportAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (using different names to avoid conflicts with state keys)
        workflow.add_node("data_processing", self._process_data)
        workflow.add_node("predict_yield", self._predict_yield)
        workflow.add_node("optimize_params", self._optimize_parameters)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("finalize_response", self._finalize_response)
        
        # Define edges
        workflow.set_entry_point("data_processing")
        workflow.add_edge("data_processing", "predict_yield")
        workflow.add_edge("predict_yield", "optimize_params")
        workflow.add_edge("optimize_params", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "finalize_response")
        workflow.add_edge("finalize_response", END)
        
        return workflow.compile()
    
    def _process_data(self, state: AgentState) -> AgentState:
        """Process wafer data using Data Agent"""
        data_summary = self.data_agent.process_wafer_data(state["wafer_data"])
        state["data_summary"] = data_summary
        state["messages"].append(
            AIMessage(content=f"Data processed: {data_summary.get('quality_score', 0):.2%} quality score")
        )
        return state
    
    def _predict_yield(self, state: AgentState) -> AgentState:
        """Predict yield using Prediction Agent"""
        prediction = self.prediction_agent.predict_yield(
            state["data_summary"],
            state["current_parameters"]
        )
        state["prediction"] = prediction
        state["messages"].append(
            AIMessage(content=f"Predicted yield: {prediction.predicted_yield:.2f}% (confidence: {prediction.confidence:.2%})")
        )
        return state
    
    def _optimize_parameters(self, state: AgentState) -> AgentState:
        """Optimize parameters using Optimization Agent"""
        optimization = self.optimization_agent.optimize_parameters(
            state["current_parameters"],
            state["prediction"].predicted_yield,
            state["data_summary"]
        )
        state["optimization"] = optimization
        state["messages"].append(
            AIMessage(content=f"Optimization complete: {optimization.improvement_percentage:.2f}% improvement potential")
        )
        return state
    
    def _generate_recommendations(self, state: AgentState) -> AgentState:
        """Generate recommendations using Recommendation Agent"""
        recommendations = self.recommendation_agent.generate_recommendations(
            state["current_parameters"],
            state["optimization"],
            state["prediction"]
        )
        state["recommendations"] = recommendations
        state["messages"].append(
            AIMessage(content=f"Generated {len(recommendations)} recommendations")
        )
        return state
    
    def _finalize_response(self, state: AgentState) -> AgentState:
        """Create final analysis response"""
        from datetime import datetime
        
        response = AnalysisResponse(
            prediction=state["prediction"],
            optimization=state["optimization"],
            recommendations=state["recommendations"],
            current_parameters=state["current_parameters"],
            timestamp=datetime.now()
        )
        state["final_response"] = response
        return state
    
    def analyze(self, wafer_data: WaferData, current_parameters: ProcessParameters) -> AnalysisResponse:
        """Main method to run the complete analysis workflow"""
        initial_state = AgentState(
            messages=[HumanMessage(content="Starting yield analysis and optimization")],
            wafer_data=wafer_data,
            current_parameters=current_parameters,
            data_summary={},
            prediction=None,
            optimization=None,
            recommendations=[],
            final_response=None
        )
        
        result = self.graph.invoke(initial_state)
        return result["final_response"]

