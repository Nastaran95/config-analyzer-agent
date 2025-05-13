import os
from typing import Dict, List, Tuple, Any
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

class ApartmentAnalyzer:
    def __init__(self, apartment_types_csv: str, layout_data: pd.DataFrame):
        # Load apartment types information
        self.apartment_types_df = pd.read_csv(apartment_types_csv)
        
        # Use provided layout data
        self.layout_df = layout_data
        
        # Create a combined dataframe for analysis
        self.df = self._create_combined_dataframe()
        
    def _create_combined_dataframe(self) -> pd.DataFrame:
        """Create a combined dataframe from apartment types and layout."""
        # Merge layout with apartment types information
        merged_df = pd.merge(
            self.layout_df,
            self.apartment_types_df,
            left_on='apartment_type',
            right_on='Apartment type',
            how='left'
        )
        
        # Create apartment numbers
        merged_df['apartment_number'] = merged_df.apply(
            lambda row: f"{row['floor']}{row.name % 100:02d}", 
            axis=1
        )
        
        # Rename columns for consistency
        merged_df = merged_df.rename(columns={
            'Number of rooms': 'bedrooms',
            'Area (m2)': 'area_bra',
            'bathrooms': 'bathrooms'
        })
        
        return merged_df
        
    def analyze_apartments(self, query: str) -> Dict[str, Any]:
        """Analyze apartment data based on the query."""
        # Perform all analyses and combine results
        results = {
            'room_types': self._analyze_room_types(),
            'bedrooms': self._analyze_bedrooms(),
            'bathrooms': self._analyze_bathrooms(),
            'area': self._analyze_area(),
            'distribution': self._analyze_distribution(),
            'raw_data': self.df.to_dict('records')
        }
        
        return results

    def _analyze_room_types(self) -> Dict[str, Any]:
        """Analyze room types per floor and total."""
        result = {}
        for floor in self.df['floor'].unique():
            floor_data = self.df[self.df['floor'] == floor]
            result[f'floor_{floor}'] = {
                '2-room': len(floor_data[floor_data['bedrooms'] == 2]),
                '3-room': len(floor_data[floor_data['bedrooms'] == 3]),
                '4-room': len(floor_data[floor_data['bedrooms'] == 4])
            }
        
        # Total counts
        result['total'] = {
            '2-room': len(self.df[self.df['bedrooms'] == 2]),
            '3-room': len(self.df[self.df['bedrooms'] == 3]),
            '4-room': len(self.df[self.df['bedrooms'] == 4])
        }
        return result

    def _analyze_bedrooms(self) -> Dict[str, Any]:
        """Analyze bedrooms per floor and per apartment."""
        result = {}
        for floor in self.df['floor'].unique():
            floor_data = self.df[self.df['floor'] == floor]
            result[f'floor_{floor}'] = {
                'total_bedrooms': floor_data['bedrooms'].sum(),
                'apartments': floor_data[['apartment_number', 'bedrooms']].to_dict('records')
            }
        
        result['total_bedrooms'] = self.df['bedrooms'].sum()
        return result

    def _analyze_bathrooms(self) -> Dict[str, Any]:
        """Analyze bathrooms per floor and per apartment."""
        result = {}
        for floor in self.df['floor'].unique():
            floor_data = self.df[self.df['floor'] == floor]
            result[f'floor_{floor}'] = {
                'total_bathrooms': floor_data['bathrooms'].sum(),
                'apartments': floor_data[['apartment_number', 'bathrooms']].to_dict('records')
            }
        
        result['total_bathrooms'] = self.df['bathrooms'].sum()
        return result

    def _analyze_area(self) -> Dict[str, Any]:
        """Analyze area (BRA) per floor and per apartment."""
        result = {}
        for floor in self.df['floor'].unique():
            floor_data = self.df[self.df['floor'] == floor]
            result[f'floor_{floor}'] = {
                'total_area': floor_data['area_bra'].sum(),
                'apartments': floor_data[['apartment_number', 'area_bra']].to_dict('records')
            }
        
        result['total_area'] = self.df['area_bra'].sum()
        return result

    def _analyze_distribution(self) -> Dict[str, Any]:
        """Calculate percentage distribution of apartment types."""
        total_apartments = len(self.df)
        result = {}
        
        # Overall distribution
        room_types = self.df['bedrooms'].value_counts()
        result['total_distribution'] = {
            f'{room_type}-room': (count / total_apartments) * 100 
            for room_type, count in room_types.items()
        }
        
        # Per floor distribution
        for floor in self.df['floor'].unique():
            floor_data = self.df[self.df['floor'] == floor]
            floor_total = len(floor_data)
            floor_distribution = floor_data['bedrooms'].value_counts()
            result[f'floor_{floor}_distribution'] = {
                f'{room_type}-room': (count / floor_total) * 100 
                for room_type, count in floor_distribution.items()
            }
        
        return result

def create_markdown_report(results: Dict[str, Any]) -> str:
    """Create a beautiful markdown report from the analysis results."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Apartment Building Analysis Report
Generated on: {now}

## Overview
This report provides a comprehensive analysis of the apartment building, including room types, bedrooms, bathrooms, and area distribution.

## Room Type Distribution

### Per Floor
"""
    
    # Add room type distribution per floor
    for floor in sorted([k for k in results.keys() if k.startswith('floor_') and not k.endswith('_distribution')]):
        floor_num = floor.split('_')[1]
        report += f"\n#### Floor {floor_num}\n"
        for room_type, count in results[floor].items():
            report += f"- {room_type}: {count} apartments\n"
    
    # Add total room type distribution
    report += "\n### Total Building\n"
    for room_type, count in results['total'].items():
        report += f"- {room_type}: {count} apartments\n"
    
    # Add bedroom analysis
    report += "\n## Bedroom Analysis\n"
    for floor in sorted([k for k in results.keys() if k.startswith('floor_') and not k.endswith('_distribution')]):
        floor_num = floor.split('_')[1]
        report += f"\n### Floor {floor_num}\n"
        report += f"- Total bedrooms: {results[floor]['total_bedrooms']}\n"
        report += "- Apartments:\n"
        for apt in results[floor]['apartments']:
            report += f"  - {apt['apartment_number']}: {apt['bedrooms']} bedrooms\n"
    
    report += f"\n### Total Building\n"
    report += f"- Total bedrooms: {results['total_bedrooms']}\n"
    
    # Add bathroom analysis
    report += "\n## Bathroom Analysis\n"
    for floor in sorted([k for k in results.keys() if k.startswith('floor_') and not k.endswith('_distribution')]):
        floor_num = floor.split('_')[1]
        report += f"\n### Floor {floor_num}\n"
        report += f"- Total bathrooms: {results[floor]['total_bathrooms']}\n"
        report += "- Apartments:\n"
        for apt in results[floor]['apartments']:
            report += f"  - {apt['apartment_number']}: {apt['bathrooms']} bathrooms\n"
    
    report += f"\n### Total Building\n"
    report += f"- Total bathrooms: {results['total_bathrooms']}\n"
    
    # Add area analysis
    report += "\n## Area (BRA) Analysis\n"
    for floor in sorted([k for k in results.keys() if k.startswith('floor_') and not k.endswith('_distribution')]):
        floor_num = floor.split('_')[1]
        report += f"\n### Floor {floor_num}\n"
        report += f"- Total area: {results[floor]['total_area']} m²\n"
        report += "- Apartments:\n"
        for apt in results[floor]['apartments']:
            report += f"  - {apt['apartment_number']}: {apt['area_bra']} m²\n"
    
    report += f"\n### Total Building\n"
    report += f"- Total area: {results['total_area']} m²\n"
    
    # Add distribution analysis
    report += "\n## Apartment Type Distribution\n"
    for floor in sorted([k for k in results.keys() if k.endswith('_distribution')]):
        floor_num = floor.split('_')[1]
        report += f"\n### Floor {floor_num}\n"
        for room_type, percentage in results[floor].items():
            report += f"- {room_type}: {percentage:.1f}%\n"
    
    report += "\n### Total Building\n"
    for room_type, percentage in results['total_distribution'].items():
        report += f"- {room_type}: {percentage:.1f}%\n"
    
    return report

# Define the state type
State = Dict[str, Any]

# Define the nodes
def analyze_apartments(state: State) -> State:
    """Node for analyzing apartments."""
    analyzer = ApartmentAnalyzer('apartment_types.csv', 'apartment_layout.csv')
    query = state['query']
    result = analyzer.analyze_apartments(query)
    return {"result": result}

def format_response(state: State) -> State:
    """Node for formatting the response."""
    result = state['result']
    report = create_markdown_report(result)
    
    # Save the report to a file
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return {"response": report}

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("analyze", analyze_apartments)
workflow.add_node("format", format_response)

# Add edges
workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "format")
workflow.add_edge("format", END)

# Compile the graph
app = workflow.compile()

def process_query(query: str) -> str:
    """Process a query about apartments."""
    result = app.invoke({"query": query})
    return result["response"]

if __name__ == "__main__":
    # Example usage with all queries combined
    combined_query = """
    Please analyze the following aspects of the apartment building:
    1. Find all two-room, three-room, four-room apartments per floor and in total
    2. Find the number of bedrooms per floor and per apartment
    3. Find the number of bathrooms per floor and per apartment
    4. Find the area (BRA) per Floor and per apartment
    5. Show apartment mix and calculate the percentage distribution of different room types per floor and in total
    """
    
    print("\nAnalyzing apartment building...")
    report = process_query(combined_query)
    print("\nReport has been generated and saved to 'result.txt'") 