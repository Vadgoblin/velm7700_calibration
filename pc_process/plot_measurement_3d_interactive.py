import json
import plotly.graph_objects as go

JSON_PATH = "../measurements/4.json"
with open(JSON_PATH,"r") as file:
    json_string = file.read()


def plot_plotly_3d(json_data):
    data = json.loads(json_data)

    its, gains, z_vals, hover_texts = [], [], [], []

    for key_str, metrics in data.items():
        it, gain = json.loads(key_str)
        raw = metrics["raw_avg"]

        if raw >= 65535 or raw <= 5:
            continue

        norm_raw = raw / (it * gain)
        its.append(it)
        gains.append(gain)
        z_vals.append(norm_raw)

        # Build the custom text that appears when you hover over a dot
        hover_texts.append(
            f"<b>IT:</b> {it} ms<br>"
            f"<b>Gain:</b> {gain}<br>"
            f"<b>Raw Avg:</b> {raw}<br>"
            f"<b>Norm Raw:</b> {norm_raw:.2f}"
        )

    # Calculate tight Z-axis bounds
    z_min, z_max = min(z_vals), max(z_vals)
    z_padding = (z_max - z_min) * 0.15
    z_floor = z_min - z_padding
    z_ceiling = z_max + z_padding

    # Create the 3D Scatter Plot
    fig = go.Figure(data=[go.Scatter3d(
        x=its,
        y=gains,
        z=z_vals,
        mode='markers',
        text=hover_texts,
        hoverinfo='text',
        marker=dict(
            size=10,
            color=z_vals,
            colorscale='Plasma',
            opacity=0.9,
            showscale=True,
            colorbar=dict(title="Normalized Raw", thickness=20),
            line=dict(width=1, color='DarkSlateGrey')
        ),
        # This trick uses negative error bars to drop "stems" to our custom floor
        error_z=dict(
            type='data',
            symmetric=False,
            arrayminus=[z - z_floor for z in z_vals],
            array=[0] * len(z_vals),
            color='gray',
            width=0,
            thickness=2
        )
    )])

    # Format the layout and axes
    fig.update_layout(
        title=dict(
            text="Interactive 3D Sensor Behavior (Hover over dots!)",
            font=dict(size=18),
            x=0.5
        ),
        scene=dict(
            xaxis_title='Integration Time (ms)',
            yaxis_title='Gain',
            zaxis_title='Normalized Raw',
            # Using log scales forces the grid to be evenly spaced
            xaxis=dict(type='log', tickvals=[25, 50, 100, 200, 400, 800]),
            yaxis=dict(type='log', tickvals=[0.125, 0.25, 1.0, 2.0]),
            zaxis=dict(range=[z_floor, z_ceiling])
        ),
        margin=dict(l=0, r=0, b=0, t=50)  # Remove extra whitespace
    )

    # Open the interactive graph in your default web browser
    fig.show()

    # Optional: Save it as a standalone interactive HTML file you can share!
    # fig.write_html("interactive_sensor_plot.html")


if __name__ == "__main__":
    plot_plotly_3d(json_string)