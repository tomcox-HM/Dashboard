import pandas as pd
from dash import Dash, html, dcc, Input, Output
import math


# Function to read and process data
def update_data_and_layout(selected_event=None):
    df = pd.read_csv("../booking_data.csv")

    if selected_event and selected_event != "Overview":
        df = df[df["Event Name"] == selected_event]

    total_forecast = df["Forecast"].sum()
    total_booked = df["Rooms Booked"].sum()

    def calculate_grid_dimensions(total_forecast):
        aspect_ratio = 16 / 9

        # Use a square root approach to get close to the aspect ratio
        sqrt_total = math.sqrt(total_forecast)
        width = math.ceil(sqrt_total * math.sqrt(aspect_ratio))
        height = math.ceil(sqrt_total / math.sqrt(aspect_ratio))

        return width, height
    
    columns, rows = calculate_grid_dimensions(total_forecast)

    # Create squares with colors
    def create_square(color, animation_delay):
        return html.Div(
            className='square ' + ('filled' if color == 'black' else ''),
            style={
                'background-color': color,
                'border': '0.1px solid white',
                'animation-delay': f'{animation_delay}s'
            }
        )

    # Calculate diagonal index for filling squares
    def calculate_diagonal_index(index, columns, rows):
        row = index // columns
        col = index % columns
        return (rows - row) + col

    # Fill the squares diagonally from bottom left to top right based on current data
    squares = [create_square('grey', 0) for _ in range(total_forecast)]
    filled_indices = sorted(range(total_forecast), key=lambda i: calculate_diagonal_index(i, columns, rows))
    for i in range(min(total_booked, total_forecast)):
        delay = i * 0.01
        squares[filled_indices[i]] = create_square('black', delay)

    return html.Div(
        style={'height': '100vh', 'width': '100vw', 'margin': '0', 'padding': '0'},
        children=[
            html.Div(
                id='square-container',
                style={
                    'display': 'grid',
                    'grid-template-columns': f'repeat({columns}, 1fr)',
                    'grid-template-rows': f'repeat({rows}, 1fr)',
                    'width': '100%',
                    'height': '100%'
                },
                children=squares
            )
        ]
    )

# Initialize Dash app
app = Dash(__name__, external_stylesheets=['/assets/styles.css'])

# Read data to populate the dropdown
df = pd.read_csv("../booking_data.csv")
event_names = df["Event Name"].unique()
dropdown_options = [{'label': 'Overview', 'value': 'Overview'}] + [{'label': name, 'value': name} for name in event_names]

# App layout with a floating dropdown for event selection and initial data display
app.layout = html.Div([
    dcc.Dropdown(
        id='event-dropdown',
        options=dropdown_options,
        placeholder="Select an Event",
        style={'width': '50%', 'position': 'absolute', 'top': '10px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': 1000}
    ),
    html.Div(id='content'),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update the display based on the selected event
@app.callback(
    Output('content', 'children'),
    [Input('event-dropdown', 'value'), Input('interval-component', 'n_intervals')]
)
def display_event(selected_event, n_intervals):
    if selected_event:
        return update_data_and_layout(selected_event)
    return update_data_and_layout()

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
