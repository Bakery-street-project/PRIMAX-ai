# ==============================================================================
# PRIMSX CODEX - CHART_SCRIPT.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import plotly.graph_objects as go
import math

# Define nodes with better positioning to group by type and minimize crossings
nodes = {
    'Blueprint JSON\n20 Tasks, 5 Phases': {'pos': (0, 0), 'color': '#3498db', 'type': 'Data'},
    'Discord Bot\nAuto-Checker': {'pos': (-1, 1.5), 'color': '#7289da', 'type': 'Communication'},
    'Google Sheets\nProgress Tracker': {'pos': (1, 1.5), 'color': '#0f9d58', 'type': 'Data'},
    'Gmail Reminder\nSystem': {'pos': (2.5, 1), 'color': '#ea4335', 'type': 'Communication'},
    'Content Pipeline\nSuper Prompts': {'pos': (-2.5, 0), 'color': '#f4b400', 'type': 'Automation'},
    'GitHub Actions\nCI/CD Pipeline': {'pos': (0, -1.5), 'color': '#2088ff', 'type': 'Automation'},
    'VaultOps Token\nRotation': {'pos': (2.5, -1), 'color': '#000000', 'type': 'Security'},
    'OpenAI GPT-4\nPrompt Generator': {'pos': (-4, 0), 'color': '#10a37f', 'type': 'AI'},
    'Team Members\n& Users': {'pos': (4, 0), 'color': '#95a5a6', 'type': 'Users'}
}

# Define connections with shorter labels to fit better
connections = [
    ('Blueprint JSON\n20 Tasks, 5 Phases', 'Discord Bot\nAuto-Checker', 'Task Status'),
    ('Blueprint JSON\n20 Tasks, 5 Phases', 'Google Sheets\nProgress Tracker', 'Initialize'),
    ('Discord Bot\nAuto-Checker', 'Google Sheets\nProgress Tracker', 'Progress Update'),
    ('Google Sheets\nProgress Tracker', 'Gmail Reminder\nSystem', 'Daily Digest'),
    ('Gmail Reminder\nSystem', 'Team Members\n& Users', 'Email Alerts'),
    ('Discord Bot\nAuto-Checker', 'Team Members\n& Users', 'Notifications'),
    ('Content Pipeline\nSuper Prompts', 'OpenAI GPT-4\nPrompt Generator', 'Prompt Request'),
    ('OpenAI GPT-4\nPrompt Generator', 'Content Pipeline\nSuper Prompts', 'AI Response'),
    ('Content Pipeline\nSuper Prompts', 'Google Sheets\nProgress Tracker', 'Log Data'),
    ('GitHub Actions\nCI/CD Pipeline', 'Blueprint JSON\n20 Tasks, 5 Phases', 'Task Verify'),
    ('GitHub Actions\nCI/CD Pipeline', 'VaultOps Token\nRotation', 'Token Rotate'),
    ('VaultOps Token\nRotation', 'Discord Bot\nAuto-Checker', 'Secrets'),
    ('VaultOps Token\nRotation', 'Gmail Reminder\nSystem', 'API Keys'),
    ('Team Members\n& Users', 'Discord Bot\nAuto-Checker', 'Commands'),
    ('Team Members\n& Users', 'Content Pipeline\nSuper Prompts', 'Create Content'),
    ('GitHub Actions\nCI/CD Pipeline', 'Discord Bot\nAuto-Checker', 'Build Status')
]

# Create the figure
fig = go.Figure()

# Add edges with labels
for source, target, label in connections:
    x0, y0 = nodes[source]['pos']
    x1, y1 = nodes[target]['pos']
    
    # Calculate midpoint for label placement
    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2
    
    # Add arrow line
    fig.add_trace(go.Scatter(
        x=[x0, x1],
        y=[y0, y1],
        mode='lines',
        line=dict(color='#555555', width=2),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # Add arrowhead
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx**2 + dy**2)
    if length > 0:
        # Normalize direction
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Arrow position (0.4 units from target)
        arrow_x = x1 - dx_norm * 0.4
        arrow_y = y1 - dy_norm * 0.4
        
        # Arrow head points
        arrow_size = 0.15
        perp_x = -dy_norm * arrow_size
        perp_y = dx_norm * arrow_size
        
        fig.add_trace(go.Scatter(
            x=[arrow_x - dx_norm * arrow_size + perp_x, 
               arrow_x, 
               arrow_x - dx_norm * arrow_size - perp_x],
            y=[arrow_y - dy_norm * arrow_size + perp_y, 
               arrow_y, 
               arrow_y - dy_norm * arrow_size - perp_y],
            mode='lines',
            line=dict(color='#555555', width=2),
            fill='toself',
            fillcolor='#555555',
            showlegend=False,
            hoverinfo='none'
        ))
    
    # Add edge label with better positioning
    # Offset label slightly to avoid overlapping with line
    offset_x = -dy_norm * 0.15 if length > 0 else 0
    offset_y = dx_norm * 0.15 if length > 0 else 0
    
    fig.add_annotation(
        x=mid_x + offset_x,
        y=mid_y + offset_y,
        text=label,
        showarrow=False,
        font=dict(size=9, color='#333333'),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='rgba(0,0,0,0.1)',
        borderwidth=1
    )

# Add nodes with better styling
node_names = list(nodes.keys())
node_x = [nodes[name]['pos'][0] for name in node_names]
node_y = [nodes[name]['pos'][1] for name in node_names]
node_colors = [nodes[name]['color'] for name in node_names]

fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    marker=dict(
        size=60,
        color=node_colors,
        line=dict(width=3, color='white'),
        sizemode='diameter'
    ),
    text=node_names,
    textposition='middle center',
    textfont=dict(size=9, color='white', family='Arial Black'),
    showlegend=False,
    hoverinfo='skip'
))

# Add component type legend
component_types = {
    'Data': '#3498db',
    'Communication': '#7289da', 
    'Automation': '#2088ff',
    'Security': '#000000',
    'AI': '#10a37f',
    'Users': '#95a5a6'
}

legend_x = -5.5
legend_y = 2
for i, (comp_type, color) in enumerate(component_types.items()):
    fig.add_trace(go.Scatter(
        x=[legend_x],
        y=[legend_y - i*0.3],
        mode='markers+text',
        marker=dict(size=15, color=color, line=dict(width=1, color='white')),
        text=comp_type,
        textposition='middle right',
        textfont=dict(size=10, color='#333333'),
        showlegend=False,
        hoverinfo='skip'
    ))

# Update layout
fig.update_layout(
    title="Codex SuperLab Automated Blueprint System",
    showlegend=False,
    xaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,
        range=[-6, 5]
    ),
    yaxis=dict(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,
        range=[-2.5, 2.5]
    ),
    plot_bgcolor='rgba(248,248,248,1)',
    annotations=[
        dict(
            text="Component Types:",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=12, color="#333333", family="Arial Bold")
        )
    ]
)

# Save the chart
fig.write_image('codex_system_architecture.png')
fig.write_image('codex_system_architecture.svg', format='svg')

print("Enhanced system architecture diagram created!")
print("- Improved layout with grouped components")
print("- Added data flow labels on all arrows") 
print("- Better text visibility with bold fonts")
print("- Component type legend added")
print("- Minimized line crossings")