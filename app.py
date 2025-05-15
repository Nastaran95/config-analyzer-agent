import streamlit as st
import pandas as pd
from apartment_analyzer import ApartmentAnalyzer
from apartment_agent import ApartmentExpertAgent 
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

# Set page config
st.set_page_config(
    page_title="Apartment Analysis Expert",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = ApartmentExpertAgent()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

# Custom CSS for better dark/light mode support
st.markdown("""
<style>
    /* Base styles */
    .main {
        padding: 2rem;
    }
    
    /* Theme-aware colors */
    :root {
        --bg-color: var(--background-color);
        --text-color: var(--text-color);
        --border-color: var(--border-color);
        --primary-color: #0078D4;
        --primary-hover: #106EBE;
        --secondary-color: #009688;
        --secondary-hover: #00796B;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: color-mix(in srgb, var(--bg-color) 95%, var(--text-color));
        border: 1px solid color-mix(in srgb, var(--bg-color) 80%, var(--text-color));
    }
    
    /* User message styling */
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: color-mix(in srgb, var(--primary-color) 10%, var(--bg-color));
        border: 1px solid color-mix(in srgb, var(--primary-color) 20%, var(--bg-color));
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon"]) {
        background-color: color-mix(in srgb, var(--secondary-color) 10%, var(--bg-color));
        border: 1px solid color-mix(in srgb, var(--secondary-color) 20%, var(--bg-color));
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: color-mix(in srgb, var(--bg-color) 90%, var(--text-color));
        border: 1px solid color-mix(in srgb, var(--bg-color) 80%, var(--text-color));
        color: var(--text-color);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: color-mix(in srgb, var(--bg-color) 80%, var(--text-color));
        border: 1px solid color-mix(in srgb, var(--bg-color) 70%, var(--text-color));
    }
    
    /* Input box styling */
    .stChatInput {
        background-color: color-mix(in srgb, var(--bg-color) 90%, var(--text-color));
        border: 1px solid color-mix(in srgb, var(--bg-color) 80%, var(--text-color));
        border-radius: 0.5rem;
    }
    
    /* Text color for better visibility */
    .stMarkdown, .stText {
        color: var(--text-color);
    }
    
    /* Plot styling */
    .js-plotly-plot {
        background-color: var(--bg-color) !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: var(--bg-color);
    }
    
    /* Info box styling */
    .stAlert {
        background-color: color-mix(in srgb, var(--bg-color) 95%, var(--text-color));
        border: 1px solid color-mix(in srgb, var(--bg-color) 80%, var(--text-color));
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏢 Apartment Analysis Expert")
st.markdown("""
This application helps you analyze apartment layouts and get expert insights about construction, design, and optimization.
Upload your apartment layout CSV file and ask questions about the design!
""")

# Sidebar for file upload and example queries
with st.sidebar:
    st.header("📁 Upload Layout")
    uploaded_file = st.file_uploader("Upload Apartment Layout CSV", type=['csv'])
    
    st.header("💡 Example Queries")
    example_queries = [
        "Summary report",
        "What is the distribution of apartment types across floors?",
        "How efficient is the area utilization in this building?",
        "What are the key design features of this layout?",
        "How does this layout compare to standard construction practices?",
        "What are potential improvements for energy efficiency?"
    ]
    for query in example_queries:
        if st.button(query, key=query):
            st.session_state.chat_history.append({"role": "user", "content": query})
            if st.session_state.analyzer:
                analysis_results = st.session_state.analyzer.analyze_apartments(query)

                print("Buttom:")
                print(query)
                print("--------------------------------" , dt.datetime.now())

                response = st.session_state.agent.process_query(query, analysis_results)
                print("RESPONSE:")
                print(response)
                print("--------------------------------" , dt.datetime.now())

                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

# Main content area
if uploaded_file is not None:
    try:
        # Read the uploaded file
        layout_df = pd.read_csv(uploaded_file)
        
        # Initialize analyzer with static apartment types
        st.session_state.analyzer = ApartmentAnalyzer('apartment_types.csv', layout_df)
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display the layout data
            st.subheader("📊 Apartment Layout Data")
            st.dataframe(layout_df, use_container_width=True)
            
            # Chat interface
            st.subheader("💬 Ask Questions About the Layout")
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask about the apartment layout..."):
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Get analysis results
                analysis_results = st.session_state.analyzer.analyze_apartments(prompt)
                

                print("PROMPT:")
                print(prompt)
                print("--------------------------------" , dt.datetime.now())

                # Get agent response
                response = st.session_state.agent.process_query(prompt, analysis_results)
                print("RESPONSE:")
                print(response)
                print("--------------------------------" , dt.datetime.now())

                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.write(response)
        
        with col2:
            # Visualizations
            st.subheader("📈 Quick Insights")
            
            # Room type distribution
            room_types = st.session_state.analyzer._analyze_room_types()
            total_rooms = room_types['total']
            
            fig = go.Figure(data=[
                go.Pie(labels=list(total_rooms.keys()),
                      values=list(total_rooms.values()),
                      hole=.3)
            ])
            fig.update_layout(title="Apartment Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            # Area distribution
            area_data = st.session_state.analyzer._analyze_area()
            floor_areas = {floor: info['total_area'] 
                         for floor, info in area_data.items() 
                         if floor != 'total_area'}
            
            fig2 = px.bar(x=list(floor_areas.keys()),
                         y=list(floor_areas.values()),
                         title="Total Area per Floor")
            fig2.update_layout(xaxis_title="Floor",
                             yaxis_title="Area (m²)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.agent.clear_history()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error processing : {str(e)}")
else:
    st.info("Please upload an apartment layout CSV file to begin analysis.") 