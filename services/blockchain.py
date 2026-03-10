import streamlit as st
import time
import json
import hashlib

def init_blockchain_state():
    if 'blockchain_logs' not in st.session_state:
        st.session_state.blockchain_logs = []

def record_to_blockchain(operator, action, details):
    """极简数据锚定上链：将关键操作生成哈希，形成不可篡改的凭证"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    raw_data = json.dumps({
        "op": operator, "act": action, "desc": details, "ts": timestamp
    }, ensure_ascii=False)

    tx_hash = "0x" + hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    log_entry = {
        "time": timestamp,
        "operator": operator,
        "action": action,
        "desc": details,
        "tx_hash": tx_hash[:24] + "..."
    }
    st.session_state.blockchain_logs.insert(0, log_entry)
    return tx_hash