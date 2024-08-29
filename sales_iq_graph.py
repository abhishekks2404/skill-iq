import plotly.graph_objects as go
import numpy as np
from plotly.offline import plot

def generate_spider_chart(score_dict, file_name="competency_performance_vs_ideal.html"):
    # Define the ideal values
    categories = list(score_dict.keys())
    current_values = list(score_dict.values())
    current_values =  [x-1 for x in current_values ]

    ideal_values = [3] * len(categories)

    # Create the figure
    fig = go.Figure()

    # Add ideal values trace
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=categories,
        fill='toself',
        name='Ideal Performance',
        line=dict(color='rgba(144, 238, 144, 0.8)'),  # Light green with some transparency
        fillcolor='rgba(144, 238, 144, 0.3)'  # Very light green fill with more transparency
    ))

    # Add current values trace
    fig.add_trace(go.Scatterpolar(
        r=current_values,
        theta=categories,
        fill='toself',
        name='Current Performance',
        line=dict(color='rgba(100, 149, 237, 0.8)'),  # Cornflower blue with some transparency
        fillcolor='rgba(100, 149, 237, 0.5)'  # Cornflower blue fill with more transparency
    ))

    # Add inner circles
    for r in [0.5, 1, 1.5, 2, 2.5]:
        theta = np.linspace(0, 2*np.pi, 100)
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
        # Polar axis settings
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3],
                showline=False,
                color='rgba(0,0,0,0.1)',
                tickfont=dict(size=8, color='rgba(0,0,0,0.5)'),
                tickvals=[0.5, 1, 1.5, 2, 2.5, 3]  # Show ticks for inner circles
            ),
            angularaxis=dict(
                linecolor='rgba(0,0,0,0.5)',  # Darker color for the outer circle
                linewidth=2,  # Make the outer circle thicker
                gridcolor='rgba(0,0,0,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'  # Transparent background
        ),
        # Legend settings
        showlegend=True,
        legend=dict(
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            orientation="h"
        ),
        # Title settings
        title=dict(
            text="Competency Performance vs. Ideal Navigator Level",
            font=dict(size=16)
        ),
        # Background settings
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
        plot_bgcolor='rgba(0,0,0,0)',    # Transparent plot background
        # Ensure the aspect ratio is equal to make perfect circles
        xaxis=dict(scaleanchor="y",visible=False),
        yaxis=dict(scaleanchor="x",visible=False)
    )

    # Save the plot as an HTML file
    fig.write_html(file_name)

    # Return the path to the HTML file
    return fig


def create_advancement_chart(score_dict, output_file='advancement_chart.html'):
    # Define the threshold scores and labels

    adjusted_current_score = sum(score_dict.values()) * 4
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

# categories = list(score_dict.keys())
# current_values = list(score_dict.values())

# file_path = generate_spider_chart(categories, current_values)
# print(f"Chart saved to: {file_path}")

####################################################################################



############### EXAMPLE USE FOR BAR CHART ############################
# adjusted_current_score = 66
# file_path = create_advancement_chart(adjusted_current_score)

################################################################