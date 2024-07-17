import pandas as pd
import math
from dash import Dash, html, dcc, Input, Output, callback_context

data_file = "../booking_data_sep_dec.csv"
data_file_label = "September 2024 - December 2024"

def calculate_grid_dimensions(total_forecast):
    aspect_ratio = 16 / 9
    sqrt_total = math.sqrt(total_forecast)
    width = math.ceil(sqrt_total * math.sqrt(aspect_ratio))
    height = math.ceil(sqrt_total / math.sqrt(aspect_ratio))
    return width, height

def create_square(color):
    return html.Div(
        className='square ' + ('filled' if color == 'black' else ''),
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

def fill_squares(forecast, booked, columns, rows):
    if forecast > 25000:
        multiplier = 1
    else:
        total_squares = columns * rows
        multiplier = (total_squares // forecast) + 1
    
    forecast = forecast * multiplier
    booked = booked * multiplier
    squares = [create_square('grey') for _ in range(forecast)]
    filled_indices = sorted(range(forecast), key=lambda i: calculate_quadrilateral_index(i, columns, rows))

    for i in range(min(booked, forecast)):
        squares[filled_indices[i]] = create_square('black')

    return squares

def update_overview(data_file):
    df = pd.read_csv(data_file)
    total_forecast = df["Forecast"].sum()
    total_booked = df["Rooms Booked"].sum()
    columns, rows = calculate_grid_dimensions(total_forecast)
    squares = fill_squares(total_forecast, total_booked, columns, rows)

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
            )
        ]
    )

def update_event_view(data_file):
    df = pd.read_csv(data_file)
    event_data = df.groupby("Event Name").agg({"Forecast": "sum", "Rooms Booked": "sum"}).reset_index()
    event_views = []

    for idx in range(len(event_data)):
        event_forecast = event_data.loc[idx, "Forecast"]
        event_booked = event_data.loc[idx, "Rooms Booked"]
        columns, rows = calculate_grid_dimensions(event_forecast)
        squares = fill_squares(event_forecast, event_booked, columns, rows)

        event_view_style = {
            'margin': '0.1px',
            'padding': '0',
            'border': '2px solid rgb(91, 169, 223)',
            'display': 'grid',
            'grid-template-columns': f'repeat({columns}, 10px)',
            'grid-template-rows': f'repeat({rows}, 10px)',
            'width': f'{columns * 10}px',
            'height': f'{rows * 10}px',
        }

        event_view = html.Div(
            style=event_view_style,
            children=squares
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

app = Dash(__name__, external_stylesheets=['/assets/styles.css'])

home_page_layout = html.Div(
    style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'},
    children=[
        html.Button("Go to Overview", id='dashboard-button', n_clicks=0, style={'font-size': '24px', 'padding': '10px 20px', 'margin': '10px', 'color': 'white', 'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
        html.Button("Go to Event View", id='event-view-button', n_clicks=0, style={'font-size': '24px', 'padding': '10px 20px', 'margin': '10px', 'color': 'white', 'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
        html.Img(src="assets/target.png", id='target-view-button', n_clicks=0, style={"height": "50px"}),
        html.H3(id='data-file-label', style={"color": "white"})
    ]
)

event_view_layout = html.Div(id='event-view-content')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return html.Div([
            update_overview(data_file),
            dcc.Interval(
                id='interval-component',
                interval=60 * 1000,
                n_intervals=0
            )
        ])
    elif pathname == '/event-view':
        return event_view_layout
    else:
        return home_page_layout

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

@app.callback(
    Output('data-file-label', 'children'),
    Input('target-view-button', 'n_clicks')
)
def update_data_file(n_clicks):
    global data_file, data_file_label
    if n_clicks is None:
        return data_file_label
    elif n_clicks % 2 != 0:
        data_file = "../booking_data_jan_apr.csv"
        data_file_label = "January 2025 - April 2025"
    else:
        data_file = "../booking_data_sep_dec.csv"
        data_file_label = "September 2024 - December 2024"
    return data_file_label

@app.callback(
    Output('event-view-content', 'children'),
    Input('url', 'pathname')
)
def display_event_view(pathname):
    if pathname == '/event-view':
        return update_event_view(data_file)
    return ""

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
