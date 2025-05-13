# Apartment Analysis Agent

This project implements an agent-based system using LangGraph to analyze apartment building data. The agent can process various queries about apartment distributions, room types, and other metrics.

## Features

- Analyze apartment types (2-room, 3-room, 4-room) per floor and in total
- Calculate number of bedrooms per floor and per apartment
- Calculate number of bathrooms per floor and per apartment
- Calculate area (BRA) per floor and per apartment
- Show apartment mix and percentage distribution of different apartment types
- Calculate percentage distribution per floor and in total

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Prepare your apartment data in a CSV file named `apartments.csv` with the following columns:
- floor
- apartment_number
- apartment_type
- bedrooms
- bathrooms
- area_bra

## Usage

Run the main script:
```bash
python apartment_analyzer.py
```

The script includes example queries that demonstrate the agent's capabilities. You can modify the queries in the `if __name__ == "__main__":` section to analyze different aspects of your apartment data.

## Example Queries

- "Find all two-room, three-room, four-room apartments per floor and in total"
- "Find the number of bedrooms per floor"
- "Find the number of bathrooms per floor"
- "Find the area (BRA) per Floor"
- "Show apartment mix, i.e. percentage distribution of two-room, three-room, four-room etc"

## Architecture

The project uses LangGraph to create a workflow that:
1. Analyzes the apartment data based on the query
2. Formats the results using an LLM for better readability

The main components are:
- `ApartmentAnalyzer`: Core class that handles data analysis
- LangGraph workflow: Manages the analysis and formatting process
- OpenAI integration: Provides natural language formatting of results 