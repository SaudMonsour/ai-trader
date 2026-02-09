
import streamlit as st
import json
import pandas as pd
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="TradingAgent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BACKGROUND BOT THREAD ---
import threading
from src.main import TradingBot

@st.cache_resource
def get_bot():
    """Starts the bot in a background thread and returns the bot instance."""
    bot = TradingBot()
    thread = threading.Thread(target=bot.run, daemon=True)
    thread.start()
    return bot, thread

bot_instance, bot_thread = get_bot()

# Text-Only / Monochromatic Styling
# Using default Streamlit theme for cleaner UI
st.markdown("", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

from src.utils.state_manager import get_state_manager

def load_state():
    try:
        sm = get_state_manager()
        sm.load_state() # Ensure we have latest from disk
        return sm.state
    except Exception as e:
        st.error(f"Error loading state: {e}")
        return {}

def load_logs(lines=100):
    try:
        if not os.path.exists("logs/trading.log"):
            return ["No logs found."]
        with open("logs/trading.log", "r") as f:
            # Read all lines and take last N
            all_lines = f.readlines()
            return all_lines[-lines:][::-1] # Reverse order
    except Exception as e:
        return [f"Error reading logs: {e}"]

def load_config_file():
    try:
        with open("config/config.yaml", "r", encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "# Config not found"

# --- SIDEBAR ---
st.sidebar.title("TRADING AGENT")
st.sidebar.markdown("---")

# Engine Status indicator
is_alive = bot_thread.is_alive()
status_color = "green" if is_alive else "red"
status_text = "ENGINE ONLINE" if is_alive else "ENGINE OFFLINE"
st.sidebar.markdown(f":{status_color}[● {status_text}]")

page = st.sidebar.radio("NAVIGATION", ["DASHBOARD", "SIGNALS", "ORDERS", "LOGS", "SETTINGS"])
st.sidebar.markdown("---")

# --- REFRESH LOGIC ---
@st.fragment(run_every=30)
def auto_refresh():
    """Triggers a rerun of the entire app every 30 seconds."""
    st.rerun()

auto_refresh()

# --- PAGES ---

state = load_state()
portfolio = state.get("portfolio", {})
health = state.get("health", {}) # Assuming we might save health to state, or infer it
orders_history = state.get("order_history", [])
signals_history = state.get("signals", []) # If we saved signals to state.json

# If signals are not in state.json (they might not be persisted there fully in MVP), 
# we might need to rely on what's available. 
# For this MVP migration, let's assume they are in state or just show placeholder if missing.

if page == "DASHBOARD":
    st.title("SYSTEM DASHBOARD")
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    cash = portfolio.get("cash", 0.0)
    pos_count = len(portfolio.get("positions", {}))
    
    with col1:
        st.metric("TOTAL CASH", f"${cash:,.2f}")
    with col2:
        st.metric("OPEN POSITIONS", str(pos_count))
    with col3:
        emergency = state.get("emergency_stop", False)
        status = "STOPPED" if emergency else "RUNNING"
        st.metric("SYSTEM STATUS", status)
    with col4:
        mode = "PAPER" # Default
        st.metric("MODE", mode)

    st.markdown("---")
    
    # Active Positions
    st.subheader("ACTIVE POSITIONS")
    positions = portfolio.get("positions", {})
    if positions:
        # Convert to DF for nice table
        pos_data = []
        for ticker, qty in positions.items():
            pos_data.append({
                "TICKER": ticker,
                "QTY": f"{qty:.4f}", # Handle float quantity
                "AVG PRICE": "---", 
                "CURRENT VALUE": "---" 
            })
        st.dataframe(pd.DataFrame(pos_data), use_container_width=False)
    else:
        st.info("NO ACTIVE POSITIONS")

    st.markdown("---")
    
    # Recent Activity
    st.subheader("RECENT ORDERS")
    if orders_history:
        # Show last 5
        recent_orders = orders_history[-5:][::-1]
        df_orders = pd.DataFrame(recent_orders)
        # Select/Rename cols if needed
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
    else:
        st.info("NO RECENT ORDERS")

elif page == "SIGNALS":
    st.title("TRADING SIGNALS")
    st.markdown("Recent generated signals waiting for review or executed.")
    
    # Just mocking list if not in state, or fetching from state
    # In the React app we fetched from /api/signals. 
    # Here we are reading state.json. existing state.json schema might not have all signals history.
    # We will display what we have or a note.
    
    # NOTE: To make this robust, state.json should eventually persist signals. 
    # For now, we will check if 'signals' key exists in state.
    
    signals = state.get("signals", [])
    if signals:
        df_sigs = pd.DataFrame(signals)
        st.dataframe(df_sigs, use_container_width=True)
    else:
        st.warning("No signal history found in local state.")

elif page == "ORDERS":
    st.title("ORDER HISTORY")
    if orders_history:
        df_orders = pd.DataFrame(orders_history[::-1]) # Newest first
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
    else:
        st.info("No orders found.")

elif page == "LOGS":
    st.title("SYSTEM LOGS")
    
    # Search
    search_term = st.text_input("SEARCH LOGS", "")
    
    log_lines = load_logs(200)
    
    # Filter
    if search_term:
        log_lines = [l for l in log_lines if search_term.lower() in l.lower()]
    
    # Display as code block for monospaced look
    log_content = "".join(log_lines)
    st.code(log_content, language="text")

elif page == "SETTINGS":
    st.title("CONFIGURATION & CONTROLS")
    
    # Emergency Stop
    st.subheader("EMERGENCY CONTROLS")
    
    is_emergency = state.get("emergency_stop", False)
    
    col_em, _ = st.columns([1, 2])
    with col_em:
        if is_emergency:
            st.error("[LOCKED] EMERGENCY STOP IS ACTIVE")
            st.markdown("The agent is halted. No new orders will be placed.")
            st.markdown("**To Resume**: You must manually edit `data/state.json` or use CLI.")
        else:
            st.success("SYSTEM IS ARMED AND ACTIVE")
            if st.button("TRIGGER EMERGENCY STOP"):
                try:
                    sm = get_state_manager()
                    sm.set_emergency_stop(True)
                    st.success("Emergency stop triggered!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update state: {e}")

    st.markdown("---")
    
    # Config Viewer
    st.subheader("CURRENT CONFIGURATION")
    config_content = load_config_file()
    st.code(config_content, language="yaml")

# Auto-refresh logic automated (occurs every 30s)
