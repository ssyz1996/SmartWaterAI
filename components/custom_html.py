def get_digital_human_html():
    return """<div class="ai-box">
<div class="laser-scan"></div>
<div style="color: #94a3b8; font-size: 12px; font-weight: bold; letter-spacing: 2px;">智能水宝AI助手</div>
<div class="hud-container"><div class="ring-1"></div><div class="ring-2"></div><div class="core-emoji">🤖</div></div>
<div class="status-badge">● 智能体引擎在线</div>
<div class="ai-text"><span style="color: #60a5fa; font-weight: bold;">▶ 实时状态:</span><br>正在执行多模态视觉感知<br>全域水利网络已接管。</div>
</div>"""

def get_node_html(current_blocks, new_blocks, fake_hashes):
    return f"""<div class="bc-card">
<div class="hash-bg">{fake_hashes}{fake_hashes}</div>
<div style="position: relative; z-index: 1;">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px;">
<span style="font-weight:900; color:#1e3a8a; font-size:16px;">FISCO BCOS 底层链</span>
<div style="display:flex; align-items:center; gap:6px; background:#d1fae5; color:#047857; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
<div style="width:8px; height:8px; background:#10b981; border-radius:50%; animation: pulse-green 2s infinite;"></div> 共识中</div>
</div>
<div style="margin-bottom: 20px;">
<div style="color: #64748b; font-size: 12px; font-weight: bold; margin-bottom: 2px;">📦 实时区块高度 (Block Height)</div>
<div style="font-family: 'Impact', sans-serif; font-size: 34px; color: #0f172a; text-shadow: 2px 2px 0px #e2e8f0;">#{current_blocks}</div>
<div style="color: #3b82f6; font-size: 11px; font-weight: bold; margin-top: 2px;">↑ 相比系统启动新增 <span style="color:#ef4444;">{new_blocks}</span> 个确权区块</div>
</div>
<div><div style="color: #64748b; font-size: 12px; font-weight: bold; margin-bottom: 6px;">📜 核心治理智能合约</div>
<div style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 12px; color: #1e293b; display: flex; justify-content: space-between; align-items: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
<span>0x7a2...3f9</span><span style="color:#10b981; font-size: 12px;">✓ 活跃</span></div>
</div></div></div>"""

def get_empty_ledger_html():
    return """<div class="bc-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
<div style="position: relative; width: 80px; height: 80px; margin-bottom: 20px;">
<div style="position: absolute; inset: 0; border: 3px dashed #94a3b8; border-radius: 50%; animation: spin-slow 8s linear infinite;"></div>
<div style="position: absolute; inset: 12px; border: 3px solid transparent; border-top: 3px solid #3b82f6; border-right: 3px solid #3b82f6; border-radius: 50%; animation: spin-rev 3s linear infinite;"></div>
<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 28px;">📡</div>
</div>
<div style="color: #1e293b; font-size: 18px; font-weight: 900; margin-bottom: 8px;">全网区块节点防篡改监听中...</div>
<div style="color: #64748b; font-size: 12px; line-height: 1.6;">
智能合约处于挂起状态。当系统触发 <span style="color:#ef4444; font-weight:bold;">[模拟突发污染]</span> 或公众提交举报时，<br>底层的哈希存证机制将自动触发并写入下一个安全区块。
</div></div>"""

def get_topology_html():
    return """<div class="bc-card" style="display: flex; flex-direction: column;">
<div style="font-weight:900; color:#1e3a8a; font-size:15px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px; margin-bottom: 15px; z-index: 2;">🌐 联盟链节点动态拓扑</div>
<div style="flex: 1; position: relative; display: flex; justify-content: center; align-items: center; min-height: 160px;">
<div style="position: absolute; width: 56px; height: 56px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; font-weight: 900; font-size: 11px; z-index: 10; animation: pulse-core 2s infinite; border: 2px solid #ffffff; line-height: 1.2;"><span>核心</span><span>合约</span></div>
<div style="position: absolute; width: 130px; height: 130px; border: 1px dashed #94a3b8; border-radius: 50%; z-index: 1; animation: spin-slow 15s linear infinite;"></div>
<div style="position: absolute; width: 85px; height: 85px; border: 1px solid #e2e8f0; border-radius: 50%; z-index: 1;"></div>
<div class="orbit-node" style="background: linear-gradient(135deg, #059669, #10b981); animation: orbit1 12s linear infinite;">水利局</div>
<div class="orbit-node" style="background: linear-gradient(135deg, #dc2626, #ef4444); animation: orbit2 12s linear infinite;">AI中枢</div>
<div class="orbit-node" style="background: linear-gradient(135deg, #d97706, #f59e0b); animation: orbit3 12s linear infinite;">环保局</div>
<div class="orbit-node" style="background: linear-gradient(135deg, #7c3aed, #8b5cf6); animation: orbit4 12s linear infinite;">公众端</div>
</div>
<div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #475569; margin-top: 15px; border: 1px solid #cbd5e1;">
<div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>⚡ 全网算力状态</span><span style="font-weight: bold; color: #10b981;">12.4 TH/s (健康)</span></div>
<div style="display: flex; justify-content: space-between;"><span>⏱️ 平均共识延迟</span><span style="font-weight: bold; color: #3b82f6;">12 ms</span></div>
</div></div>"""

def get_twin_html(gates_html_content):
    return f"""<div style="padding: 12px 8px; background: #f8fafc; border-radius: 8px; border: 1px solid #cbd5e1; margin-top:5px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
<div style="color: #0f172a; font-size: 14px; font-weight: 900; margin-bottom: 12px; margin-left: 5px; border-left: 4px solid #3b82f6; padding-left: 8px;">🏗️ 全流域水利枢纽孪生控制阵列</div>
<div style="display: flex; justify-content: space-between;">{gates_html_content}</div>
</div>"""

def get_logs_html(inner_html):
    return f"<div class='log-box'><div class='log-content'>{inner_html}{inner_html}</div></div>"