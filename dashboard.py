import pandas as pd
import math
from dash import Dash, html, dcc, Input, Output, callback_context

# Define the colors for each combination of dataset and page index
dataset_colors = {
    ('sep-dec'): 'rgb(91, 169, 223)',
    ('jan-apr'): 'rgb(233, 169, 91)'
}

# Global variables
data_file = "../booking_data_sep_dec.csv"
data_file_label = "September 2024 - December 2024"
dataset = 'sep-dec'

def calculate_grid_dimensions(total_forecast):
    aspect_ratio = 16 / 9
    sqrt_total = math.sqrt(total_forecast)
    width = math.ceil(sqrt_total * math.sqrt(aspect_ratio))
    height = math.ceil(sqrt_total / math.sqrt(aspect_ratio))
    return width, height

def create_square(color, is_booked=False):
    classes = 'square ' + ('filled' if color == 'black' else '')
    return html.Div(
        className=classes,
        style={
            'background-color': color,
            'border': '0',
        }
    )

def calculate_quadrilateral_index(index, columns, rows):
    aspect_ratio = 3/5
    row = index // columns
    col = index % columns
    max_row = int((columns - col + 1) * aspect_ratio)
    row = min(row, max_row)
    return (rows - 1 - row) * columns + col

def fill_squares(forecast, booked, columns, rows, dataset, page):
    # Determine color based on dataset and page
    color = dataset_colors.get((dataset), 'grey')  # Default to grey if not found
    if forecast > 25000:
        multiplier = 1
    else:
        total_squares = columns * rows
        multiplier = (total_squares // forecast) + 1
    forecast = forecast * multiplier
    booked = booked * multiplier
    squares = [create_square('rgb(191, 191, 191)') for _ in range(forecast)]
    filled_indices = sorted(range(forecast), key=lambda i: calculate_quadrilateral_index(i, columns, rows))
    
    for i in range(min(booked, forecast)):
        if i < min(booked, forecast):
            squares[filled_indices[i]] = create_square(color, is_booked=True)
        else:
            squares[filled_indices[i]] = create_square(color)
    
    return squares

def update_overview(data_file, dataset):
    df = pd.read_csv(data_file)
    total_forecast = df["Forecast"].sum()
    total_booked = df["Rooms Booked"].sum()
    columns, rows = calculate_grid_dimensions(total_forecast)
    squares = fill_squares(total_forecast, total_booked, columns, rows, dataset, 'overview')

    # Calculate the percentage of rooms booked
    booked_percentage = total_booked / total_forecast

    # Calculate the dimensions of the booked area
    booked_width = math.sqrt(booked_percentage * columns * rows * (16 / 9))
    booked_height = booked_width * (9 / 16)

    # Calculate the top-right position
    booked_top = (rows - booked_height) * 1.05
    booked_right = (columns - booked_width) * 1.05

    # Convert to percentages
    booked_top_percent = booked_top * 100 / rows + 1
    booked_right_percent = booked_right * 100 / columns

    booked_position_style = {
        'position': 'absolute',
        'top': f'{booked_top_percent}%',
        'right': f'{booked_right_percent}%',
        'color': 'white',
        'font-size': '25px',
    }

    forecast_text = html.Div(
        children=f"{total_forecast:,}",
        style={'position': 'absolute', 'top': '10px', 'right': '10px', 'color': 'white', 'font-size': '25px'}
    )

    booked_text = html.Div(
        children=f"{total_booked:,}",
        style=booked_position_style
    )

    return html.Div(
        style={'height': '100vh', 'width': '100vw', 'margin': '0', 'padding': '0'},
        children=[
            html.Div(
                style={'position': 'absolute', 'bottom': '10px', 'left': '10px'},
                children=[
                    dcc.Link(html.Img(src="/assets/home.png", id='home-button', style={'cursor': 'pointer', 'height': '40px'}), href='/')
                ]
            ),
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
            ),
            booked_text,  # Add the booked text to the layout
            forecast_text  # Add the forecast text to the layout
        ]
    )

def update_event_view(data_file, dataset):
    df = pd.read_csv(data_file)
    event_data = df.groupby("Event Name").agg({"Forecast": "sum", "Rooms Booked": "sum"}).reset_index()
    total_events = len(event_data)

    max_rows = 10
    max_columns = int(total_events / max_rows)
    event_views = []

    for idx in range(total_events):
        event_forecast = event_data.loc[idx, "Forecast"]
        event_booked = event_data.loc[idx, "Rooms Booked"]
        columns, rows = calculate_grid_dimensions(event_forecast)
        squares = fill_squares(event_forecast, event_booked, columns, rows, dataset, 'event-view')

        event_view_style = {
            'border': '2px solid white',
            'display': 'grid',
            'grid-template-columns': f'repeat({columns}, 1fr)',
            'grid-template-rows': f'repeat({rows}, 1fr)',
            'width': f'100vw/15',   # Adjust width based on number of columns
            'height': f'100vh/10'    # Adjust height based on number of rows
        }

        event_view = html.Div(
            style=event_view_style,
            children=squares
        )

        event_views.append(event_view)

    return html.Div(
        style={
            'height': '100vh',  # Ensure full viewport height
            'width': '100vw',   # Ensure full viewport width
            'margin': '0',
            'padding': '0',
            'display': 'grid',  # Use grid display for event views
            'grid-template-columns': f'repeat({max_columns}, 1fr)',  # Set exactly 13 columns
            'grid-template-rows': f'repeat({max_rows}, 1fr)'         # Set exactly 12 rows
        },
        children=[
            html.Div(
                style={'position': 'absolute', 'bottom': '10px', 'left': '10px'},
                children=[
                    dcc.Link(html.Img(src="/assets/home.png", id='home-button', style={'cursor': 'pointer', 'height': '40px'}), href='/')
                ]
            ),
            *event_views
        ]
    )

app = Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap',
    '/assets/styles.css'
])

home_page_layout = html.Div(
    style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'},
    children=[
        html.Div(
            style={'position': 'absolute', 'top': '10px', 'left': '10px'},  # Adjusted position to top right corner
            children=[
                html.Img(src="/assets/HotelMap-Logo-White.png", style={'height': '20px'})
            ]
        ),
        html.Div(
            style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Img(src="/assets/vroom.png", style={'height': '120px', 'margin-bottom': '40px'}),
            ]
        ),
        html.Div(
            style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Button("OVERVIEW", id='overview-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
                html.Button("EVENT VIEW", id='event-view-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
            ]
        ),
        html.Div(
            style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center', 'margin-top': '20px'},
            children=[
                html.Img(src="assets/calendar.png", id='calendar-view-button', n_clicks=0, style={"height": "50px", "margin-right": "10px"}),
                html.H3(id='data-file-label', style={"color": "white", "margin": "0"})
            ]
        ),
    ]
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/overview':
        return update_overview(data_file, dataset)
    elif pathname == '/event-view':
        return update_event_view(data_file, dataset)
    else:
        return home_page_layout

@app.callback(
    Output('url', 'pathname'),
    [Input('overview-button', 'n_clicks'),
     Input('event-view-button', 'n_clicks')]
)
def go_to_page(overview_n_clicks, event_view_n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        return '/'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'overview-button' and overview_n_clicks > 0:
        return '/overview'
    elif button_id == 'event-view-button' and event_view_n_clicks > 0:
        return '/event-view'
    return '/'

@app.callback(
    Output('data-file-label', 'children'),
    Input('calendar-view-button', 'n_clicks')
)
def update_data_file(n_clicks):
    global data_file, data_file_label, dataset
    if n_clicks is None:
        return data_file_label
    elif n_clicks % 2 != 0:
        data_file = "../booking_data_jan_apr.csv"
        data_file_label = "January 2025 - April 2025"
        dataset = 'jan-apr'
    else:
        data_file = "../booking_data_sep_dec.csv"
        data_file_label = "September 2024 - December 2024"
        dataset = 'sep-dec'
    
    # Refresh the current page to reflect updated data
    return data_file_label

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, host='0.0.0.0', port=8050)
