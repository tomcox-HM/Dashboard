import pandas as pd
import math
from dash import Dash, html, dcc, Input, Output, callback_context

def calculate_grid_dimensions(total_forecast):
    aspect_ratio = 16 / 9

    # Use a square root approach to get close to the aspect ratio
    sqrt_total = math.sqrt(total_forecast)
    width = math.ceil(sqrt_total * math.sqrt(aspect_ratio))
    height = math.ceil(sqrt_total / math.sqrt(aspect_ratio))

    return width, height


# Create squares with colors
def create_square(color):
    return html.Div(
        className='square ' + ('filled' if color == 'black' else ''),
        style={
            'background-color': color,
            'border': '0.1px solid white',
        }
    )

def calculate_quadrilateral_index(index, columns, rows):
    # Calculate the aspect ratio dynamically
    aspect_ratio = columns / rows
    
    # Calculate row and column indices
    row = index // columns
    col = index % columns
    
    # Calculate the maximum row index for the current column based on aspect ratio
    max_row = int((columns - col + 1) * aspect_ratio)
    
    # Ensure the row index does not exceed the maximum allowable row
    row = min(row, max_row)
    
    # Calculate the final index from bottom left to top right
    return (rows - 1 - row) * columns + col

# Function to read and process data for the main dashboard
def update_overview():
    df = pd.read_csv("../booking_data.csv")

    total_forecast = df["Forecast"].sum()
    total_booked = df["Rooms Booked"].sum()

    columns, rows = calculate_grid_dimensions(total_forecast)

    # Assuming total_forecast, total_booked, columns, and rows are defined elsewhere
    squares = [create_square('grey') for _ in range(total_forecast)]
    filled_indices = sorted(range(total_forecast), key=lambda i: calculate_quadrilateral_index(i, columns, rows))

    # Fill squares based on the calculated order
    for i in range(min(total_booked, total_forecast)):
        squares[filled_indices[i]] = create_square('black')

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

def update_event_view():
    df = pd.read_csv("../booking_data.csv")

    # Group by event name and sum forecast and booked rooms
    event_data = df.groupby("Event Name").agg({"Forecast": "sum", "Rooms Booked": "sum"}).reset_index()

    # Initialize an empty list to hold the event views
    event_views = []

    # Display all events
    for idx in range(len(event_data)):  # Displaying all events
        event_forecast = event_data.loc[idx, "Forecast"]
        event_booked = event_data.loc[idx, "Rooms Booked"]

        # Calculate grid dimensions for the current event
        columns, rows = calculate_grid_dimensions(event_forecast)

        # Create squares for the current event
        squares = []

        for r in range(rows):
            for c in range(columns):
                if r * columns + c < event_forecast:
                    if r * columns + c < event_booked:
                        squares.append(create_square('black'))
                    else:
                        squares.append(create_square('grey'))
                else:
                    squares.append(create_square('grey'))

        # Create HTML structure for the event view
        event_view = html.Div(
            style={
                'height': f'{rows * 10}px',  # Ensure the height is proportional to the number of rows
                'width': f'{columns * 10}px',  # Ensure the width is proportional to the number of columns
                'margin': '10px',  # Add some margin between event blocks
                'padding': '0',
                'border': '1px solid blue',  # Add a colored border around each event block
            },
            children=[
                html.Div(
                    id=f'square-container-{idx}',
                    style={
                        'display': 'grid',
                        'grid-template-columns': f'repeat({columns}, 10px)',
                        'grid-template-rows': f'repeat({rows}, 10px)',
                        'width': f'{columns * 10}px',
                        'height': f'{rows * 10}px',
                    },
                    children=squares
                )
            ]
        )

        event_views.append(event_view)

    return html.Div(
        style={
            'height': '100vh', 
            'width': '100vw', 
            'margin': '0', 
            'padding': '0',
            'display': 'flex',
            'flex-wrap': 'wrap',
            'align-content': 'flex-start'
        },
        children=event_views
    )

# Initialize Dash app
app = Dash(__name__, external_stylesheets=['/assets/styles.css'])

home_page_layout = html.Div(
    style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'},
    children=[
        html.Button("Go to Dashboard", id='dashboard-button', n_clicks=0, style={'font-size': '24px', 'padding': '10px 20px', 'margin': '10px'}),
        html.Button("Go to Event View", id='event-view-button', n_clicks=0, style={'font-size': '24px', 'padding': '10px 20px', 'margin': '10px'})
    ]
)

event_view_layout = html.Div(id='event-view-content')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update the page content based on URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return html.Div([
            html.Div(id='content'),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,  # in milliseconds
                n_intervals=0
            )
        ])
    elif pathname == '/event-view':
        return event_view_layout
    else:
        return home_page_layout

# Callback to navigate to the appropriate page when the button is clicked
@app.callback(
    Output('url', 'pathname'),
    [Input('dashboard-button', 'n_clicks'), Input('event-view-button', 'n_clicks')]
)
def go_to_page(dashboard_n_clicks, event_view_n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        return '/'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'dashboard-button' and dashboard_n_clicks > 0:
        return '/dashboard'
    elif button_id == 'event-view-button' and event_view_n_clicks > 0:
        return '/event-view'
    return '/'

# Callback to update the display based on the interval
@app.callback(
    Output('content', 'children'),
    Input('interval-component', 'n_intervals')
)
def display_event(n_intervals):
    return update_overview()

# Callback to update the event view
@app.callback(
    Output('event-view-content', 'children'),
    Input('url', 'pathname')
)
def display_event_view(pathname):
    if pathname == '/event-view':
        return update_event_view()
    return ""

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
