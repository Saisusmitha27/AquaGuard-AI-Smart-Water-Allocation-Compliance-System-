import streamlit as st
import os
import sys

# Add error handling for imports
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    st.error("Please install required packages: pip install langchain-community sentence-transformers")
    st.stop()

from models import WaterAllocation
from database import KnowledgeBase
from analytics import Analytics
from visualizations import Dashboard
from alerts import AlertSystem
from reports import ReportGenerator
from simulation import ScenarioSimulator
from chatbot import ChatBot

st.set_page_config(
    page_title="AquaGuard - Smart Water Management",
    page_icon="💧",
    layout="wide"
)

st.title("💧 AquaGuard – Smart Water Allocation & Compliance System")

@st.cache_resource
def load_embeddings():
    try:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"⚠️ Embeddings failed to load: {e}")
        st.info("The app will run with limited functionality (no document search)")
        return None

def initialize_session_state():
    if "water_alloc" not in st.session_state:
        st.session_state.water_alloc = WaterAllocation()
        st.session_state.water_alloc.messages = []
    if "drought_mode" not in st.session_state:
        st.session_state.drought_mode = False

def check_ollama():
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    initialize_session_state()
    
    # Check Ollama status
    ollama_available = check_ollama()
    if not ollama_available:
        st.sidebar.warning("⚠️ Ollama not detected. LLM features will be limited.")
    
    embeddings = load_embeddings()
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.session_state.drought_mode = st.toggle("Drought Mode", st.session_state.drought_mode)
        st.divider()
        
        # Initialize KB with error handling
        kb = KnowledgeBase(embeddings)
        with st.spinner("Loading Knowledge Base..."):
            try:
                kb_db = kb.build_kb_vector_db()
                if kb_db:
                    st.success("✅ Knowledge Base loaded")
                else:
                    st.info("ℹ️ No PDFs found in kb_pdfs folder")
            except Exception as e:
                st.error(f"Error loading KB: {e}")
                kb_db = None
        
        st.divider()
        
        # File uploader with better error handling
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file is not None:
            with st.spinner("Processing PDF..."):
                try:
                    result = kb.process_uploaded_file(uploaded_file)
                    if result:
                        st.success(f"✅ {uploaded_file.name} uploaded successfully")
                    else:
                        st.error("Failed to process PDF")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        
        # Alert system
        alert_system = AlertSystem(st.session_state.water_alloc)
        alert_system.render_sidebar()
        
        # Reset button
        if st.button("🔄 Reset System", use_container_width=True):
            st.session_state.water_alloc = WaterAllocation()
            st.session_state.water_alloc.messages = []
            st.rerun()
    
    # Initialize components
    analytics = Analytics(st.session_state.water_alloc)
    dashboard = Dashboard(analytics, st.session_state.water_alloc)
    simulator = ScenarioSimulator(st.session_state.water_alloc)
    reports = ReportGenerator(st.session_state.water_alloc)
    
    # Create tabs
    main_tab, dash_tab, sim_tab, report_tab, audit_tab = st.tabs([
        "💬 Chat Assistant", "📊 Dashboard", "🎯 Simulation", 
        "📋 Reports", "🔗 Audit Trail"
    ])
    
    with main_tab:
        chatbot = ChatBot(
            kb.kb_db,  # Use kb.kb_db directly
            kb.user_db,
            st.session_state.water_alloc,
            st.session_state.drought_mode,
            ollama_available  # Pass Ollama status
        )
        chatbot.render_chat()
    
    with dash_tab:
        dashboard.render(st.session_state.drought_mode)
    
    with sim_tab:
        simulator.render()
    
    with report_tab:
        reports.render()
    
    with audit_tab:
        st.subheader("🔗 Blockchain Audit Trail")
        audit_data = st.session_state.water_alloc.audit.get_audit_report()
        if audit_data:
            import pandas as pd
            df = pd.DataFrame(audit_data)
            st.dataframe(df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify Blockchain", use_container_width=True):
                    if st.session_state.water_alloc.audit.verify_chain():
                        st.success("✅ Blockchain verified - Chain is intact")
                    else:
                        st.error("❌ Blockchain corrupted!")
            with col2:
                st.metric("Total Blocks", len(audit_data))
        else:
            st.info("No audit data available yet")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.exception(e)