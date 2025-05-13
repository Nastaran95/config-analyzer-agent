import os
from typing import Dict, List, Tuple, Any, TypedDict, Annotated
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()

# Define the state type
class AgentState(TypedDict):
    query: str
    apartment_data: Dict[str, Any]
    context: str
    response: str
    final_response: str

class ApartmentExpertAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
            # model_kwargs={"allow_reuse": True}
        )
        
        # Initialize the system prompt
        self.system_prompt = """You are an expert in apartment construction and design calculation. 
        Your role is to analyze apartment layouts and provide detailed insights about:
        - Room distribution and types
        - Area calculations and efficiency
        - Design optimization
        - Construction feasibility
        - Market value estimation
        - Energy efficiency considerations
        
        Always provide professional, accurate, and detailed responses based on the data provided.
        Format your responses in a clear, structured way using markdown when appropriate."""
        
        # Initialize the graph
        self.workflow = self._create_workflow()
        self.chat_history = []
        
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        # Define the nodes
        def format_context(state: AgentState) -> AgentState:
            """Format the apartment data and query into context."""
            apartment_data = state["apartment_data"]
            query = state["query"]
            formatted_data = self._format_apartment_data(apartment_data)
            
            context = f"""
            Apartment Analysis Context:
            {formatted_data}
            
            User Query: {query}
            """
            return {"context": context}
        
        def generate_response(state: AgentState) -> AgentState:
            """Generate response using the LLM."""
            context = state["context"]
            messages = [
                SystemMessage(content=self.system_prompt),
                *self.chat_history,
                HumanMessage(content=context)
            ]
            
            response = self.llm.invoke(messages)
            return {"response": response.content}
        
        def update_history(state: AgentState) -> AgentState:
            """Update chat history with the new interaction."""
            query = state["query"]
            response = state["response"]
            
            self.chat_history.extend([
                HumanMessage(content=query),
                AIMessage(content=response)
            ])
            
            return {"final_response": response}
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("format_context", format_context)
        workflow.add_node("generate_response", generate_response)
        workflow.add_node("update_history", update_history)
        
        # Add edges
        workflow.add_edge(START, "format_context")
        workflow.add_edge("format_context", "generate_response")
        workflow.add_edge("generate_response", "update_history")
        workflow.add_edge("update_history", END)
        
        # Compile the graph
        return workflow.compile()
        
    def process_query(self, query: str, apartment_data: Dict[str, Any]) -> str:
        """Process a query about apartments with context."""
        # Create initial state
        initial_state = {
            "query": query,
            "apartment_data": apartment_data,
            "context": "",
            "response": "",
            "final_response": ""
        }
        
        # Invoke the workflow with initial state
        result = self.workflow.invoke(initial_state)
        
        return result["final_response"]
    
    def _format_apartment_data(self, data: Dict[str, Any]) -> str:
        """Format apartment data for better context."""
        formatted = []
        
        # Add room type distribution
        if 'room_types' in data:
            formatted.append("Room Type Distribution:")
            for floor, counts in data['room_types'].items():
                if floor != 'total':
                    formatted.append(f"  Floor {floor.split('_')[1]}:")
                    for room_type, count in counts.items():
                        formatted.append(f"    - {room_type}: {count} apartments")
            
            formatted.append("\nTotal Building:")
            for room_type, count in data['room_types']['total'].items():
                formatted.append(f"  - {room_type}: {count} apartments")
        
        # Add area information
        if 'area' in data:
            formatted.append("\nArea Analysis:")
            for floor, info in data['area'].items():
                if floor != 'total_area':
                    formatted.append(f"  Floor {floor.split('_')[1]}:")
                    formatted.append(f"    - Total area: {info['total_area']:.2f} m²")
                    formatted.append("    - Apartments:")
                    for apt in info['apartments']:
                        formatted.append(f"      * {apt['apartment_number']}: {apt['area_bra']:.2f} m²")
            
            formatted.append(f"\nTotal Building Area: {data['area']['total_area']:.2f} m²")
        
        # Add distribution analysis
        if 'distribution' in data:
            formatted.append("\nApartment Type Distribution:")
            for floor, dist in data['distribution'].items():
                if floor != 'total_distribution':
                    formatted.append(f"  Floor {floor.split('_')[1]}:")
                    for room_type, percentage in dist.items():
                        formatted.append(f"    - {room_type}: {percentage:.1f}%")
            
            formatted.append("\nTotal Building Distribution:")
            for room_type, percentage in data['distribution']['total_distribution'].items():
                formatted.append(f"  - {room_type}: {percentage:.1f}%")
        
        return "\n".join(formatted)
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = [] 