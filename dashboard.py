import pandas as pd
from dash import Dash, html, dcc, Input, Output
import math


def update_data_and_layout():
    df = pd.read_csv("../booking_data.csv")

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

app.layout = update_data_and_layout()

app.callback(
    Output('square-container', 'children'),
    [Input('interval-component', 'n_intervals')]
)(lambda _: update_data_and_layout())

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.Div(id='square-container')
])

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
