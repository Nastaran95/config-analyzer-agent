import streamlit as st
import pandas as pd
from apartment_analyzer import ApartmentAnalyzer
from apartment_agent import ApartmentExpertAgent 
import plotly.express as px
import plotly.graph_objects as go

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

# Custom CSS for better dark mode support
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    /* User message styling */
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: rgba(0, 120, 212, 0.1);
        border: 1px solid rgba(0, 120, 212, 0.2);
    }
    /* Assistant message styling */
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon"]) {
        background-color: rgba(0, 150, 136, 0.1);
        border: 1px solid rgba(0, 150, 136, 0.2);
    }
    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    /* Input box styling */
    .stChatInput {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 0.5rem;
    }
    /* Text color for better visibility */
    .stMarkdown, .stText {
        color: rgba(255, 255, 255, 0.9);
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
                response = st.session_state.agent.process_query(query, analysis_results)
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
                

                print(prompt)
                print(st.session_state.chat_history)
                print(analysis_results)
                print("hereeee")
                print("--------------------------------")

                # Get agent response
                response = st.session_state.agent.process_query(prompt, analysis_results)
                print("RESPONSE:")
                print(response)
                print("--------------------------------")

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