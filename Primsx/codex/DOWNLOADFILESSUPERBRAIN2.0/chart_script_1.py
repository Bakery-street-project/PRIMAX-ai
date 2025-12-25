# ==============================================================================
# PRIMSX CODEX - CHART_SCRIPT_1.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Create the data
data = {
    "categories": ["Blueprint Tasks", "Implementation Phases", "Python Scripts", "CI/CD Workflows", "Configuration Files", "Discord Commands", "Cron Jobs", "GitHub Actions", "Content Stages", "API Integrations", "API Endpoints"],
    "values": [20, 5, 3, 1, 5, 4, 3, 3, 8, 7, 15],
    "groups": ["Components", "Components", "Components", "Components", "Components", "Automation", "Automation", "Automation", "Automation", "Automation", "Metrics"]
}

# Create DataFrame
df = pd.DataFrame(data)

# Abbreviate category names to meet 15 character limit
df['categories_short'] = df['categories'].replace({
    'Implementation Phases': 'Impl Phases',
    'CI/CD Workflows': 'CI/CD Flows', 
    'Configuration Files': 'Config Files',
    'Discord Commands': 'Discord Cmds',
    'API Integrations': 'API Intgrtns'
})

# Define colors for each group using brand colors
color_map = {
    'Components': '#1FB8CD',
    'Automation': '#DB4545', 
    'Metrics': '#2E8B57'
}

# Create the horizontal bar chart
fig = go.Figure()

# Add bars for each group
for group in df['groups'].unique():
    group_data = df[df['groups'] == group]
    fig.add_trace(go.Bar(
        y=group_data['categories_short'],
        x=group_data['values'],
        name=group,
        orientation='h',
        marker_color=color_map[group]
    ))

# Update layout
fig.update_layout(
    title='Codex SuperLab Implementation Stats',
    xaxis_title='Count',
    yaxis_title='Categories',
    barmode='group',
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5)
)

# Update traces
fig.update_traces(cliponaxis=False)

# Save as both PNG and SVG
fig.write_image("codex_superlab_chart.png")
fig.write_image("codex_superlab_chart.svg", format="svg")

# Show the chart
fig.show()