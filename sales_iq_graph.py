import plotly.graph_objects as go
import numpy as np
from plotly.offline import plot
import collections

def grade_wise_data_for_spider(json_data):
    # Define the keys we are interested in
    keys = ['Decision Criteria', 'Economic Buyer', 'Metrics', 'Competition', 'Champion', 'Identify Pain', 'Decision Process']
 
    progress_data = {}
    for i, (transcript_key, transcript_values) in enumerate(json_data.items(), start=1):
        # Map the values directly from the transcript to the progress data
        progress_data[transcript_key] = {key: int(transcript_values[key]) for key in keys}
        progress_data[transcript_key]["stage"] = str(transcript_values["deal_stage_level"])



    # Dictionary to accumulate sums and counts for each stage
    stage_data = collections.defaultdict(lambda: {
        'Decision Criteria': 0,
        'Economic Buyer': 0,
        'Metrics': 0,
        'Competition': 0,
        'Champion': 0,
        'Identify Pain': 0,
        'Decision Process': 0,
        'count': 0
    })
    
    # Accumulate the sums and counts
    for transcript_values in progress_data.values():
        stage = transcript_values['stage']
        for key in ['Decision Criteria', 'Economic Buyer', 'Metrics', 'Competition', 'Champion', 'Identify Pain', 'Decision Process']:
            stage_data[stage][key] += transcript_values[key]
        stage_data[stage]['count'] += 1
    
    # Calculate the averages
    final_data = {}
    for stage, values in stage_data.items():
        final_data[stage] = {key: values[key] / values['count'] for key in values if key != 'count'}
    
    # Output the final JSON
    return final_data
def create_spider_chart(progress_dict,graph_title):
    categories = list(next(iter(progress_dict.values())).keys())

    # Create the figure
    fig = go.Figure()

    # Color palette for progress traces
    colors = ['rgba(255, 0, 0, {})', 'rgba(0, 255, 0, {})', 'rgba(0, 0, 255, {})',
              'rgba(255, 255, 0, {})', 'rgba(255, 0, 255, {})']

    # Add traces for each progress
    for i, (progress_name, scores) in enumerate(progress_dict.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=categories,
            fill='toself',
            name=progress_name,
            line=dict(color=color.format(0.8)),
            fillcolor=color.format(0.3)
        ))

    # Add ideal values trace if there's only one progress
    if len(progress_dict) == 1:
        ideal_values = [3] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=ideal_values,
            theta=categories,
            fill='toself',
            name='Expected Performance',
            line=dict(color='rgba(144, 238, 144, 0.8)'),
            fillcolor='rgba(144, 238, 144, 0.3)'
        ))

    # Add inner circles
    for r in [0.5, 1, 1.5, 2, 2.5]:
        theta = np.linspace(0, 2 * np.pi, 100)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line=dict(color='rgba(0,0,0,0.1)', width=0.5),
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3],
                showline=False,
                color='rgba(0,0,0,0.1)',
                tickfont=dict(size=8, color='rgba(0,0,0,0.5)'),
                tickvals=[0.5, 1, 1.5, 2, 2.5, 3]
            ),
            angularaxis=dict(
                linecolor='rgba(0,0,0,0.5)',
                linewidth=2,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        legend=dict(
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            orientation="h"
        ),
        title=dict(
            text=f"{graph_title}",
            font=dict(size=16)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(scaleanchor="y", visible=False),
        yaxis=dict(scaleanchor="x", visible=False)
    )
    fig.write_html("competency_performance_vs_ideal.html")
    return fig

def create_advancement_chart(adjusted_current_score, output_file='advancement_chart.html'):
    # Define the threshold scores and labels
    adjusted_current_score = sum(adjusted_current_score.values()) * 4
    thresholds = [20, 40, 60, 80, 100, 100]
    labels = ['Rookie', 'Navigator', 'Specialist', 'Analyst', 'Innovator', 'Sales Sage']

    # Create the bar chart
    fig = go.Figure()

    # Add bars for threshold scores
    fig.add_trace(go.Bar(
        x=labels,
        y=thresholds,
        name='Threshold Scores',
        marker_color='lightblue'
    ))

    # Add a line for the adjusted current score
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=adjusted_current_score,
        x1=len(labels) - 0.5,
        y1=adjusted_current_score,
        line=dict(color="red", width=2, dash="dash"),
    )

    # Add an annotation for the adjusted current score
    fig.add_annotation(
        x=0,  # Changed from len(labels) - 1 to 0
        y=adjusted_current_score,
        text=f"Adjusted Current Score: {adjusted_current_score}",
        showarrow=False,
        xanchor='left',  # Added to ensure left alignment
        yshift=10,
        xshift=0,  # Added a small horizontal shift for better visibility
        font=dict(color="red")
    )

    # Customize the layout
    fig.update_layout(
        title='Current Score vs. Advancement Thresholds',
        xaxis_title='',
        yaxis_title='Score',
        yaxis_range=[0, 110],
        plot_bgcolor='white',
        xaxis=dict(
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=False,
            ticks='outside',
            tickwidth=2,
            tickcolor='black',
            ticklen=10
        ),
        yaxis=dict(
            showline=True,
            linewidth=2,
            linecolor='black',
            mirror=False,
            ticks='outside',
            tickwidth=2,
            tickcolor='black',
            ticklen=10
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Save the plot as an HTML file
    # plot(fig, filename=output_file, auto_open=False)
    # print(f"Chart saved as {output_file}")

    return fig


############### EXAMPLE USE FOR SPIDER CHART ############################
# score_dict = {
#     'Decision Criteria': 1,
#     'Economic Buyer': 2,
#     'Metrics': 3,
#     'Competition': 2,
#     'Champion': 3,
#     'Identify Pain': 1,
#     'Decision Process': 0
# }
# progress_dict= {'Progress 1': {'Decision Criteria': 1.5,
#   'Economic Buyer': 2,
#   'Metrics': 3,
#   'Competition': 2.5,
#   'Champion': 3,
#   'Identify Pain': 1,
#   'Decision Process': 0},
#  'Progress 2': {'Decision Criteria': 3,
#   'Economic Buyer': 0,
#   'Metrics': 3,
#   'Competition': 2,
#   'Champion': 2,
#   'Identify Pain': 1,
#   'Decision Process': 1},
#  'Progress 3': {'Decision Criteria': 2,
#   'Economic Buyer': 1,
#   'Metrics': 0,
#   'Competition': 0,
#   'Champion': 3,
#   'Identify Pain': 3,
#   'Decision Process': 3},
#  'Progress 4': {'Decision Criteria': 3,
#   'Economic Buyer': 3,
#   'Metrics': 1,
#   'Competition': 1,
#   'Champion': 2,
#   'Identify Pain': 1,
#   'Decision Process': 2},
#  'Progress 5': {'Decision Criteria': 0,
#   'Economic Buyer': 2,
#   'Metrics': 0,
#   'Competition': 3,
#   'Champion': 1,
#   'Identify Pain': 2,
#   'Decision Process': 1}}



# file_path = create_spider_chart(progress_dict)
# print(f"Chart saved to: {file_path}")

####################################################################################



############### EXAMPLE USE FOR BAR CHART ############################
# adjusted_current_score = 66
# file_path = create_advancement_chart(adjusted_current_score)

################################################################