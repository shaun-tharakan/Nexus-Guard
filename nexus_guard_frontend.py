import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
import time
import copy
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide", page_title="NexusGuard Pro", page_icon="🏙️")

# ======================================================================================
# GLOBAL STYLE — dark command-center theme, glow/pulse keyframes, card styling
# ======================================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: radial-gradient(circle at 20% 0%, #101827 0%, #0b0f1a 55%, #070a12 100%); }

h1, h2, h3 { letter-spacing: 0.3px; }

.ng-title {
    font-size: 2.1rem; font-weight: 800; color: #eaf2ff;
    text-shadow: 0 0 18px rgba(0, 230, 180, 0.35);
    margin-bottom: 0;
}
.ng-subtitle { color: #8fa3c2; font-size: 0.95rem; margin-top: 2px; }

.ng-card {
    background: linear-gradient(145deg, #131b2c, #0d1320);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    animation: cardPop 0.5s ease-out;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
}
@keyframes cardPop {
    0% { transform: scale(0.94); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
.ng-card-label { font-size: 0.78rem; color: #8fa3c2; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.ng-card-value { font-family: 'JetBrains Mono', monospace; font-size: 1.9rem; font-weight: 700; margin-top: 4px; }
.ng-card.red .ng-card-value { color: #ff5a5a; text-shadow: 0 0 14px rgba(255,60,60,0.45); }
.ng-card.amber .ng-card-value { color: #ffb84d; text-shadow: 0 0 14px rgba(255,184,77,0.4); }
.ng-card.green .ng-card-value { color: #4dffa6; text-shadow: 0 0 14px rgba(77,255,166,0.4); }
.ng-card.blue .ng-card-value { color: #4dc3ff; text-shadow: 0 0 14px rgba(77,195,255,0.4); }
.ng-card-bar { height: 4px; border-radius: 4px; margin-top: 10px; background: rgba(255,255,255,0.08); overflow: hidden; }
.ng-card-bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }

.ng-flash {
    padding: 10px 16px; border-radius: 10px; font-weight: 700; color: #fff;
    background: linear-gradient(90deg, #ff2d2d, #b30000, #ff2d2d);
    background-size: 200% 100%;
    animation: flash-sweep 1.4s linear infinite, flicker 0.9s ease-in-out infinite;
    margin-bottom: 10px;
}
@keyframes flash-sweep { 0% { background-position: 0% 0; } 100% { background-position: 200% 0; } }
@keyframes flicker { 0%,100% { opacity: 1; } 50% { opacity: 0.78; } }

.ng-feed-wrap { max-height: 430px; overflow-y: auto; padding-right: 6px; }
.ng-feed-item {
    border-left: 3px solid #2c3a52;
    background: rgba(255,255,255,0.03);
    padding: 8px 12px; margin-bottom: 8px; border-radius: 0 8px 8px 0;
    animation: slideIn 0.4s ease-out;
    font-size: 0.86rem; color: #d6e2f2;
}
.ng-feed-item.impact { border-left-color: #ff5a5a; }
.ng-feed-item.cascade { border-left-color: #ffb84d; }
.ng-feed-item.ai { border-left-color: #4dc3ff; }
.ng-feed-item.ok { border-left-color: #4dffa6; }
.ng-feed-time { color: #6d80a0; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-right: 6px; }
@keyframes slideIn { from { transform: translateX(24px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

.ng-legend-chip { display: inline-flex; align-items: center; gap: 6px; margin-right: 16px; font-size: 0.85rem; color: #c3d1e6; }
.ng-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ng-title">🏙️ NexusGuard Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="ng-subtitle">Urban Cascading Failure Simulator — live infrastructure health, disaster shockwaves &amp; AI mitigation</div>', unsafe_allow_html=True)
st.write("")

with st.expander("ℹ️ Welcome! How to read this dashboard", expanded=False):
    st.markdown("""
    **What is this?**
    NexusGuard Pro simulates how disasters cause "cascading failures" across connected city infrastructure.

    **How to use it:**
    1. Select a disaster and choose which human-readable city assets take the initial hit from the sidebar.
    2. Click **Run Simulation**.
    3. Watch the impact ripple outward on the geographic map *and* the live dependency network below it, follow the command metrics, and read the step-by-step incident log.
    """)

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Simulation Controls")
disaster_type = st.sidebar.selectbox("Disaster Trigger", ["flood", "earthquake", "cyber_attack"])
intensity = st.sidebar.slider("Disaster Intensity", 1.0, 10.0, 5.0)

try:
    nodes_res = requests.get(f"{API_URL}/api/nodes").json()
    node_name_to_id = {n["name"]: n["id"] for n in nodes_res}
    node_options = list(node_name_to_id.keys())
except Exception:
    node_name_to_id = {
        "Central Power Substation": "node_01",
        "North Water Treatment": "node_02",
        "City General Hospital": "node_03",
        "Main Highway Corridor": "node_04",
        "East Power Substation": "node_05"
    }
    node_options = list(node_name_to_id.keys())
    st.sidebar.warning("Backend not connected. Run FastAPI server first.")

selected_names = st.sidebar.multiselect(
    "Select Initial Failed Assets",
    node_options,
    default=["Central Power Substation"]
)
initial_failures = [node_name_to_id[name] for name in selected_names if name in node_name_to_id]

enable_ai = st.sidebar.checkbox("Enable AI Autonomous Mitigation", value=True)
animation_delay = st.sidebar.slider("Step Delay (seconds)", 1.0, 3.0, 1.5)
run_button = st.sidebar.button("🚀 Run Simulation", type="primary")

# ======================================================================================
# VISUAL HELPERS
# ======================================================================================
STATUS_COLORS = {
    "active": (0, 230, 120, 200),
    "failed": (255, 40, 40, 255),
    "mitigated": (0, 180, 255, 255),
    "warning": (255, 180, 60, 255),
}
TYPE_ICON = {"power": "⚡", "water": "💧", "hospital": "🏥", "road": "🛣️"}

# Fixed schematic layout (independent of lat/lon) so dependency direction is obvious
DIAGRAM_LAYOUT = {
    "node_01": (150, 60),
    "node_05": (450, 60),
    "node_02": (150, 175),
    "node_04": (450, 175),
    "node_03": (300, 275),
}
DIAGRAM_EDGES = [
    ("node_01", "node_02"),
    ("node_01", "node_03"),
    ("node_05", "node_04"),
    ("node_02", "node_03"),
]


def get_node_color(status):
    return list(STATUS_COLORS.get(status, STATUS_COLORS["active"]))


def get_time():
    return datetime.now().strftime('%H:%M:%S')


def generate_grid_connections(nodes):
    node_dict = {n['id']: n for n in nodes}
    arcs = []
    for src_id, tgt_id in DIAGRAM_EDGES:
        if src_id in node_dict and tgt_id in node_dict:
            source, target = node_dict[src_id], node_dict[tgt_id]
            if source['status'] == 'failed' or target['status'] == 'failed':
                color = [255, 50, 50, 255]
            elif source['status'] == 'mitigated' or target['status'] == 'mitigated':
                color = [0, 180, 255, 255]
            else:
                color = [0, 230, 120, 150]
            arcs.append({
                "from_lon": source['lon'], "from_lat": source['lat'],
                "to_lon": target['lon'], "to_lat": target['lat'],
                "color": color
            })
    return arcs


def create_deck(nodes_list, pulse_ids=None, pulse_scale=1.0):
    pulse_ids = pulse_ids or set()
    for n in nodes_list:
        n["color"] = get_node_color(n["status"])
        base_radius = n["capacity"] * 4
        n["radius"] = base_radius * pulse_scale if n["id"] in pulse_ids else base_radius

    df_nodes = pd.DataFrame(nodes_list)
    arcs_data = generate_grid_connections(nodes_list)

    view_state = pdk.ViewState(
        latitude=df_nodes['lat'].mean(), longitude=df_nodes['lon'].mean(),
        zoom=12.2, pitch=45, bearing=-15
    )
    scatter_layer = pdk.Layer(
        "ScatterplotLayer", data=df_nodes,
        get_position='[lon, lat]', get_fill_color='color', get_radius='radius',
        pickable=True, auto_highlight=True, stroked=True,
        get_line_color=[255, 255, 255, 90], line_width_min_pixels=1,
    )
    arc_layer = pdk.Layer(
        "ArcLayer", data=arcs_data,
        get_source_position='[from_lon, from_lat]', get_target_position='[to_lon, to_lat]',
        get_source_color='color', get_target_color='color', get_width=5,
    )
    return pdk.Deck(
        map_provider="carto", map_style="dark", initial_view_state=view_state,
        layers=[arc_layer, scatter_layer],
        tooltip={"text": "🏥 {name}\nType: {type}\nStatus: {status}\nLoad: {current_load} MW"}
    )


def render_metric_cards(container, metrics, elapsed_label="LIVE"):
    stability = metrics.get("grid_stability", max(0, 100 - metrics.get("severity_index", 0)))
    stab_color = "green" if stability >= 70 else ("amber" if stability >= 35 else "red")
    html = f"""
    <div style="display:flex; gap:14px; flex-wrap:wrap;">
      <div class="ng-card red" style="flex:1; min-width:170px;">
        <div class="ng-card-label">🔴 Critical Failures</div>
        <div class="ng-card-value">{metrics['failed_assets']}</div>
        <div class="ng-card-bar"><div class="ng-card-bar-fill" style="width:{min(100, metrics['failed_assets']*20)}%; background:#ff5a5a;"></div></div>
      </div>
      <div class="ng-card amber" style="flex:1; min-width:170px;">
        <div class="ng-card-label">👥 Impacted Citizens</div>
        <div class="ng-card-value">{metrics['affected_citizens']:,}</div>
        <div class="ng-card-bar"><div class="ng-card-bar-fill" style="width:{min(100, metrics['affected_citizens']/1000)}%; background:#ffb84d;"></div></div>
      </div>
      <div class="ng-card blue" style="flex:1; min-width:170px;">
        <div class="ng-card-label">💸 Economic Burn Rate</div>
        <div class="ng-card-value">₹{metrics['economic_loss']:,}/hr</div>
        <div class="ng-card-bar"><div class="ng-card-bar-fill" style="width:{min(100, metrics['economic_loss']/2000)}%; background:#4dc3ff;"></div></div>
      </div>
      <div class="ng-card {stab_color}" style="flex:1; min-width:170px;">
        <div class="ng-card-label">🛡️ Grid Stability · {elapsed_label}</div>
        <div class="ng-card-value">{stability}%</div>
        <div class="ng-card-bar"><div class="ng-card-bar-fill" style="width:{stability}%; background:{'#4dffa6' if stab_color=='green' else ('#ffb84d' if stab_color=='amber' else '#ff5a5a')};"></div></div>
      </div>
    </div>
    """
    container.markdown(html, unsafe_allow_html=True)


def render_stability_gauge(container, stability):
    color = "#4dffa6" if stability >= 70 else ("#ffb84d" if stability >= 35 else "#ff5a5a")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=stability,
        number={"suffix": "%", "font": {"color": color, "size": 34}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#8fa3c2"},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "rgba(255,90,90,0.18)"},
                {"range": [35, 70], "color": "rgba(255,184,77,0.16)"},
                {"range": [70, 100], "color": "rgba(77,255,166,0.16)"},
            ],
        },
        title={"text": "Grid Stability Index", "font": {"color": "#8fa3c2", "size": 13}},
    ))
    fig.update_layout(
        height=210, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#eaf2ff"},
    )
    container.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _node_pulse_css(status):
    if status == "failed":
        return "fill:#ff2828; filter:url(#glow-red); animation: pulseRed 1.1s ease-in-out infinite;"
    if status == "mitigated":
        return "fill:#20a8ff; filter:url(#glow-blue); animation: pulseBlue 1.6s ease-in-out infinite;"
    if status == "warning":
        return "fill:#ffb84d; filter:url(#glow-amber); animation: pulseAmber 0.7s ease-in-out infinite;"
    return "fill:#22c976; filter:url(#glow-green); animation: pulseGreen 3s ease-in-out infinite;"


def build_network_diagram(nodes_list, height=340):
    """Schematic dependency diagram (independent of the geo map) with animated
    power-flow dots and pulsing node glow — makes *why* a cascade happens legible."""
    node_map = {n['id']: n for n in nodes_list}
    svg_nodes, svg_edges, svg_flows = [], [], []

    for src, tgt in DIAGRAM_EDGES:
        if src not in node_map or tgt not in node_map or src not in DIAGRAM_LAYOUT or tgt not in DIAGRAM_LAYOUT:
            continue
        x1, y1 = DIAGRAM_LAYOUT[src]
        x2, y2 = DIAGRAM_LAYOUT[tgt]
        s_status, t_status = node_map[src]['status'], node_map[tgt]['status']
        if s_status == 'failed' or t_status == 'failed':
            line_color, flow_color, dur = "#7a1414", "#ff4d4d", "0.9s"
        elif s_status == 'mitigated' or t_status == 'mitigated':
            line_color, flow_color, dur = "#164a66", "#3fc3ff", "1.6s"
        else:
            line_color, flow_color, dur = "#1c3350", "#38e0a0", "2.6s"
        pid = f"path-{src}-{tgt}"
        svg_edges.append(f'<path id="{pid}" d="M{x1},{y1} L{x2},{y2}" stroke="{line_color}" stroke-width="3" fill="none"/>')
        svg_flows.append(
            f'<circle r="4.5" fill="{flow_color}" style="filter:drop-shadow(0 0 4px {flow_color})">'
            f'<animateMotion dur="{dur}" repeatCount="indefinite">'
            f'<mpath href="#{pid}"/></animateMotion></circle>'
        )

    for nid, (x, y) in DIAGRAM_LAYOUT.items():
        if nid not in node_map:
            continue
        n = node_map[nid]
        style = _node_pulse_css(n['status'])
        icon = TYPE_ICON.get(n['type'], "◆")
        svg_nodes.append(f"""
        <g>
          <circle cx="{x}" cy="{y}" r="30" style="{style}" stroke="rgba(255,255,255,0.35)" stroke-width="1.5"/>
          <text x="{x}" y="{y+7}" text-anchor="middle" font-size="20">{icon}</text>
          <text x="{x}" y="{y+52}" text-anchor="middle" font-size="12" fill="#c3d1e6" font-family="Inter, sans-serif">{n['name']}</text>
          <text x="{x}" y="{y+68}" text-anchor="middle" font-size="10" letter-spacing="1" fill="#6d80a0" font-family="JetBrains Mono, monospace">{n['status'].upper()}</text>
        </g>
        """)

    html = f"""
    <div style="background:linear-gradient(160deg,#0d1320,#080b13); border-radius:14px; border:1px solid rgba(255,255,255,0.06); padding:6px;">
    <svg viewBox="0 0 600 330" width="100%" height="{height}">
      <defs>
        <filter id="glow-red" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-blue" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-green" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-amber" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <style>
        @keyframes pulseRed {{ 0%,100% {{ r:30; opacity:1; }} 50% {{ r:34; opacity:0.75; }} }}
        @keyframes pulseAmber {{ 0%,100% {{ r:30; opacity:1; }} 50% {{ r:36; opacity:0.6; }} }}
        @keyframes pulseBlue {{ 0%,100% {{ r:30; opacity:1; }} 50% {{ r:32; opacity:0.85; }} }}
        @keyframes pulseGreen {{ 0%,100% {{ r:30; }} 50% {{ r:31; }} }}
        circle {{ transform-box: fill-box; transform-origin: center; transition: fill 0.4s ease; }}
      </style>
      {''.join(svg_edges)}
      {''.join(svg_flows)}
      {''.join(svg_nodes)}
    </svg>
    </div>
    """
    components.html(html, height=height + 20)


def render_feed(container, entries):
    items = ""
    for ts, kind, text in entries:
        items += f'<div class="ng-feed-item {kind}"><span class="ng-feed-time">{ts}</span>{text}</div>'
    html = f'<div class="ng-feed-wrap">{items}</div>'
    container.markdown(html, unsafe_allow_html=True)


def render_legend(container):
    html = """
    <span class="ng-legend-chip"><span class="ng-dot" style="background:#22c976; box-shadow:0 0 8px #22c976;"></span>Active</span>
    <span class="ng-legend-chip"><span class="ng-dot" style="background:#ff2828; box-shadow:0 0 8px #ff2828;"></span>Failed</span>
    <span class="ng-legend-chip"><span class="ng-dot" style="background:#20a8ff; box-shadow:0 0 8px #20a8ff;"></span>Mitigated</span>
    <span class="ng-legend-chip"><span class="ng-dot" style="background:#ffb84d; box-shadow:0 0 8px #ffb84d;"></span>At Risk</span>
    """
    container.markdown(html, unsafe_allow_html=True)


# ======================================================================================
# SIMULATION EXECUTION
# ======================================================================================
if run_button:
    if not initial_failures:
        st.error("Please select at least one initial failed asset.")
        st.stop()

    payload = {
        "disaster_type": disaster_type, "intensity": intensity,
        "initial_failures": initial_failures, "enable_ai": enable_ai
    }

    try:
        res = requests.post(f"{API_URL}/api/simulate", json=payload)
        res.raise_for_status()
        data = res.json()
        metrics = data["metrics"]
        final_nodes = data["updated_nodes"]
        node_names = {n['id']: n.get('name', n['id']) for n in final_nodes}

        initial_set = set(initial_failures)
        cascade_targets = [n['id'] for n in final_nodes if (n['status'] in ['failed', 'mitigated']) and (n['id'] not in initial_set)]
        mitigated_targets = [n['id'] for n in final_nodes if n['status'] == 'mitigated']

        # --- Top command bar: flash banner + animated metric cards + gauge ---
        flash_container = st.empty()
        top_left, top_right = st.columns([3, 1])
        with top_left:
            metrics_container = st.empty()
        with top_right:
            gauge_container = st.empty()
        st.divider()

        col_map, col_feed = st.columns([2, 1])
        with col_map:
            st.subheader("🗺️ Live City Infrastructure Grid")
            legend_container = st.empty()
            render_legend(legend_container)
            map_container = st.empty()
        with col_feed:
            st.subheader("📡 Live Incident Feed")
            feed_container = st.empty()

        st.divider()
        st.subheader("🕸️ Dependency Cascade — Live Network View")
        st.caption("This schematic ignores geography and shows *why* failures spread: power feeds water & the hospital, water feeds the hospital, and the east substation feeds the highway corridor.")
        diagram_container = st.empty()

        feed_entries = []
        current_state = copy.deepcopy(final_nodes)
        for n in current_state:
            n['status'] = 'active'

        def snapshot(pulse_ids=None, pulse_scale=1.0):
            map_container.pydeck_chart(create_deck(copy.deepcopy(current_state), pulse_ids, pulse_scale))
            with diagram_container:
                build_network_diagram(current_state)

        # Initial calm state
        snapshot()

        # ---- STEP 1: Initial impact ----
        initial_names = [node_names[nid] for nid in initial_failures]
        flash_container.markdown(
            f'<div class="ng-flash">⚠️ {disaster_type.replace("_", " ").title()} STRIKING — INTENSITY {intensity:.1f}</div>',
            unsafe_allow_html=True
        )
        feed_entries.append((get_time(), "impact", f"⚠️ <b>IMPACT:</b> {disaster_type.replace('_', ' ').title()} struck <b>{', '.join(initial_names)}</b>."))
        render_feed(feed_container, feed_entries)

        # brief pre-failure warning pulse, then commit to failed
        for _ in range(2):
            snapshot(pulse_ids=initial_set, pulse_scale=1.4)
            time.sleep(0.25)
            snapshot(pulse_ids=initial_set, pulse_scale=1.0)
            time.sleep(0.25)
        for n in current_state:
            if n['id'] in initial_set:
                n['status'] = 'failed'
        snapshot()
        render_metric_cards(metrics_container, {
            "failed_assets": len(initial_set), "affected_citizens": 0,
            "economic_loss": 0, "severity_index": 25, "grid_stability": 75
        }, elapsed_label="STEP 1")
        render_stability_gauge(gauge_container, 75)
        time.sleep(animation_delay)

        # ---- STEP 2: Cascade ----
        running_failed = len(initial_set)
        if cascade_targets:
            for target_id in cascade_targets:
                target_name = node_names[target_id]
                feed_entries.append((get_time(), "cascade", f"⚡ Surge traveling down network lines toward <b>{target_name}</b>..."))
                render_feed(feed_container, feed_entries)
                for n in current_state:
                    if n['id'] == target_id:
                        n['status'] = 'warning'
                snapshot(pulse_ids={target_id}, pulse_scale=1.3)
                time.sleep(1.0)

                feed_entries.append((get_time(), "cascade", f"🚨 <b>CASCADE FAILURE:</b> <b>{target_name}</b> has overloaded and gone offline!"))
                render_feed(feed_container, feed_entries)
                for n in current_state:
                    if n['id'] == target_id:
                        n['status'] = 'failed'
                snapshot()
                running_failed += 1
                render_metric_cards(metrics_container, {
                    "failed_assets": running_failed,
                    "affected_citizens": int(metrics['affected_citizens'] * running_failed / max(1, metrics['failed_assets'])),
                    "economic_loss": int(metrics['economic_loss'] * running_failed / max(1, metrics['failed_assets'])),
                    "severity_index": 100 - max(20, 75 - running_failed * 15),
                    "grid_stability": max(20, 75 - running_failed * 15)
                }, elapsed_label="CASCADING")
                render_stability_gauge(gauge_container, max(20, 75 - running_failed * 15))
                time.sleep(animation_delay)
        else:
            feed_entries.append((get_time(), "ok", "⚡ No cascading failures detected — the grid absorbed the shock."))
            render_feed(feed_container, feed_entries)
            time.sleep(animation_delay)

        # ---- STEP 3: AI mitigation ----
        if enable_ai and mitigated_targets:
            for target_id in mitigated_targets:
                target_name = node_names[target_id]
                feed_entries.append((get_time(), "ai", f"🛡️ <b>AI INTERVENTION:</b> Rerouting backup units to secure <b>{target_name}</b>..."))
                render_feed(feed_container, feed_entries)
                for n in current_state:
                    if n['id'] == target_id:
                        n['status'] = 'mitigated'
                snapshot(pulse_ids={target_id}, pulse_scale=1.2)
                time.sleep(animation_delay)
            feed_entries.append((get_time(), "ok", "✅ <b>STATUS:</b> AI has stabilized the grid."))
        elif enable_ai:
            feed_entries.append((get_time(), "ok", "✅ <b>STATUS:</b> Grid stable. No AI intervention required."))
        else:
            feed_entries.append((get_time(), "impact", "❌ <b>STATUS:</b> Grid unstable. AI Mitigation Offline."))
        render_feed(feed_container, feed_entries)

        # Final settle
        flash_container.empty()
        render_metric_cards(metrics_container, metrics, elapsed_label="FINAL")
        render_stability_gauge(gauge_container, metrics.get("grid_stability", 100))
        snapshot()

        st.divider()

        # --- Asset Health Dashboard Table ---
        st.subheader("📊 Asset Health Dashboard")
        df_display = pd.DataFrame(final_nodes)[['id', 'name', 'type', 'status', 'current_load', 'capacity']]

        def style_status(val):
            colors = {"failed": "background-color:#3a1010;color:#ff8080;", "mitigated": "background-color:#0f2b3a;color:#7fd6ff;",
                      "active": "background-color:#0f3a24;color:#7fffb0;"}
            return colors.get(val, "")

        styled = df_display.style.map(style_status, subset=["status"])
        st.dataframe(styled, use_container_width=True)

    except Exception as e:
        st.error(f"Backend Error. Details: {e}")
else:
    st.info("👈 Configure a scenario in the sidebar and click **Run Simulation** to watch the cascade unfold.")