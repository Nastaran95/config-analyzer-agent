# Apartment Analysis Expert

A web application that helps you analyze apartment layouts and get expert insights about construction, design, and optimization.

## What You Can Do

- Upload your apartment layout data in CSV format
- Ask questions about your apartment design
- Get instant analysis and visualizations
- View apartment type distributions
- See area usage per floor
- Get expert insights about construction and design

## How to Use

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the web application:
```bash
streamlit run app.py
```

4. Upload your apartment layout CSV file and start asking questions!

## Example Questions You Can Ask

- "What is the distribution of apartment types across floors?"
- "How efficient is the area utilization in this building?"
- "What are the key design features of this layout?"
- "How does this layout compare to standard construction practices?"
- "What are potential improvements for energy efficiency?"

## Required CSV Format

Your apartment layout CSV should include:
- floor
- apartment_number
- apartment_type
- bedrooms
- bathrooms
- area_bra

## Features

- Interactive web interface
- Real-time data analysis
- Visual charts and graphs
- Expert insights powered by AI
- Chat-based interaction
- Dark mode support 