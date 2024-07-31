import pandas as pd
import math
from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc

dataset_colors = {
    'sep-dec': 'rgb(91, 169, 223)',
    'jan-apr': 'rgb(233, 169, 91)'
}

def calculate_grid_dimensions(total_forecast):
    aspect_ratio = 16 / 9
    sqrt_total = math.sqrt(total_forecast)
    width = math.ceil(sqrt_total * math.sqrt(aspect_ratio))
    height = math.ceil(sqrt_total / math.sqrt(aspect_ratio))
    return width, height

def create_square(color):
    return html.Div(
        className='square filled' if color == 'black' else 'square',
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

def fill_squares(forecast, booked, columns, rows, dataset):
    color = dataset_colors.get(dataset, 'grey')
    if forecast > 25000:
        multiplier = 1
    else:
        total_squares = columns * rows
        multiplier = (total_squares // forecast) + 1
    forecast *= multiplier
    booked *= multiplier
    squares = [create_square('rgb(191, 191, 191)') for _ in range(forecast)]
    filled_indices = sorted(range(forecast), key=lambda i: calculate_quadrilateral_index(i, columns, rows))
    
    for i in range(min(booked, forecast)):
        squares[filled_indices[i]] = create_square(color)
    
    return squares

def create_banner(title, date_range, color):
    banner_text = f"{title}: {date_range}"
    return html.Div(
        children=banner_text,
        style={
            'background-color': 'white',
            'color': color,
            'text-align': 'right',
            'padding': '5px',
            'font-size': '25px',
            'font-weight': 'bold',
            'width': '100%',
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'box-shadow': f'0 5px 5px {color}',
            'z-index': '2'
        }
    )

def update_overview(data_file, dataset):
    df = pd.read_csv(data_file)
    total_forecast = df["Forecast"].sum()
    total_booked = df["Rooms Booked"].sum()
    columns, rows = calculate_grid_dimensions(total_forecast)
    squares = fill_squares(total_forecast, total_booked, columns, rows, dataset)

    date_range = {
        'sep-dec': 'September - December 2024',
        'jan-apr': 'January - April 2025'
    }.get(dataset, 'Unknown Period')

    booked_percentage = total_booked / total_forecast
    booked_width = math.sqrt(booked_percentage * columns * rows * (16 / 9))
    booked_height = booked_width * (9 / 16)
    booked_top = (rows - booked_height) * 1.05
    booked_right = (columns - booked_width) * 1.05

    booked_position_style = {
        'position': 'absolute',
        'top': f'{booked_top * 100 / rows + 4}%',
        'right': f'{booked_right * 100 / columns - 1}%',
        'color': 'white',
        'font-size': '25px',
    }

    forecast_text = html.Div(
        children=f"{total_forecast:,}",
        style={'position': 'absolute', 'top': '50px', 'right': '10px', 'color': 'white', 'font-size': '25px', 'z-index': '1001'}
    )

    booked_text = html.Div(
        id='booked-text',
        children=f"{total_booked:,}",
        style=booked_position_style
    )

    banner_color = dataset_colors.get(dataset, 'grey')

    return html.Div(
        style={'position': 'relative', 'height': '100vh', 'overflow': 'hidden'},
        children=[
            create_banner("Overview", date_range, banner_color),
            html.Div(
                style={'position': 'absolute', 'bottom': '20px', 'left': '10px', 'z-index': '1001'},
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
                    'height': 'calc(100vh - 60px)',  # Adjust height to account for the banner
                    'position': 'absolute',
                    'top': '50px',  # Position below the banner
                    'left': '0'
                },
                children=squares
            ),
            booked_text,  
            forecast_text  
        ]
    )

def update_event_view(data_file, dataset):
    df = pd.read_csv(data_file)
    event_data = df.groupby("Event Name").agg({"Forecast": "sum", "Rooms Booked": "sum"}).reset_index()
    total_events = len(event_data)

    max_rows = 10
    max_columns = int(total_events / max_rows)
    event_views = []

    date_range = {
        'sep-dec': 'September - December 2024',
        'jan-apr': 'January - April 2025'
    }.get(dataset, 'Unknown Period')

    banner_color = dataset_colors.get(dataset, 'grey')
    pop_up_border_color = banner_color

    for idx in range(total_events):
        event_name = event_data.loc[idx, "Event Name"]
        event_forecast = event_data.loc[idx, "Forecast"]
        event_booked = event_data.loc[idx, "Rooms Booked"]
        columns, rows = calculate_grid_dimensions(event_forecast)
        squares = fill_squares(event_forecast, event_booked, columns, rows, dataset)

        event_view = html.Div(
            id='event-box',
            style={
                'border': '2px solid white',
                'display': 'grid',
                'grid-template-columns': f'repeat({columns}, 1fr)',
                'grid-template-rows': f'repeat({rows}, 1fr)',
                'width': '100%',
                'height': '100%',
                'position': 'relative',
            },
            children=[
                *squares,
                html.Div(
                    className='pop-up',
                    style={
                        'border': f'3px solid {pop_up_border_color}'
                    },
                    children=[
                        html.H4(event_name),
                        html.P(f"Forecast: {event_forecast}"),
                        html.P(f"Booked: {event_booked}")
                    ]
                )
            ]
        )

        event_views.append(event_view)

    return html.Div(
        style={
            'height': '100vh',
            'width': '100%',
            'position': 'relative',
            'overflow': 'hidden',
            'display': 'grid',
            'grid-template-columns': f'repeat({max_columns}, 1fr)',
            'grid-template-rows': f'repeat({max_rows}, 1fr)',
            'gap': '0px',  # Add some spacing between event views
            'padding-top': '50px'  # Space for the banner
        },
        children=[
            create_banner("Event View", date_range, banner_color),
            html.Div(
                style={'position': 'absolute', 'bottom': '10px', 'left': '10px'},
                children=[
                    dcc.Link(html.Img(src="/assets/home.png", id='home-button'), href='/')
                ]
            ),
            *event_views
        ]
    )

app = Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap',
    '/assets/styles.css',
    dbc.themes.BOOTSTRAP
])

home_page_layout = html.Div(
    style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'},
    children=[
        html.Div(
            style={'position': 'absolute', 'top': '10px', 'left': '10px'},
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
                html.Button("OVERVIEW SEP-DEC", id='sep-dec-overview-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
                html.Button("EVENT VIEW SEP-DEC", id='sep-dec-event-view-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(91, 169, 223)', 'border': 'none', 'border-radius': '25px'}),
                html.Button("OVERVIEW JAN-APR", id='jan-apr-overview-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(233, 169, 91)', 'border': 'none', 'border-radius': '25px'}),
                html.Button("EVENT VIEW JAN-APR", id='jan-apr-event-view-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'rgb(233, 169, 91)', 'border': 'none', 'border-radius': '25px'}),
            ]
        ),
        html.Div(
            style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Button("CYCLE VIEWS", id='cycle-button', n_clicks=0, 
                            style={'font-size': '20px', 'padding': '15px 25px', 'margin': '10px', 'color': 'white', 
                                   'background-color': 'green', 'border': 'none', 'border-radius': '25px'})
            ]
        ),
    ]
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current-dataset', data=''),  # Store to keep track of the current dataset
    dcc.Store(id='current-page-index', data=0),  # Store to keep track of the current page index
    dcc.Store(id='cycle-started', data=False),  # Store to track if cycling has started
    html.Div(id='page-content', className='fade-in'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
])

@app.callback(
    Output('page-content', 'children', allow_duplicate=True),
    Output('page-content', 'className', allow_duplicate=True),
    Output('current-dataset', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate'
)
def display_page(pathname):
    if pathname == '/':
        return home_page_layout, 'fade-in', ''

    elif pathname == '/sep-dec-overview':
        return update_overview("../booking_data_sep_dec.csv", 'sep-dec'), 'fade-in', '../booking_data_sep_dec.csv'
    elif pathname == '/sep-dec-event-view':
        return update_event_view("../booking_data_sep_dec.csv", 'sep-dec'), 'fade-in', '../booking_data_sep_dec.csv'
    elif pathname == '/jan-apr-overview':
        return update_overview("../booking_data_jan_apr.csv", 'jan-apr'), 'fade-in', '../booking_data_jan_apr.csv'
    elif pathname == '/jan-apr-event-view':
        return update_event_view("../booking_data_jan_apr.csv", 'jan-apr'), 'fade-in', '../booking_data_jan_apr.csv'
    else:
        return home_page_layout, 'fade-in', ''
    
@app.callback(
    Output('booked-text', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('current-dataset', 'data')
)
def update_booked_value(n, data_file):
    df = pd.read_csv(data_file)
    total_booked = df["Rooms Booked"].sum()
    return f"{total_booked:,}"

@app.callback(
    Output('url', 'pathname'),
    [Input('sep-dec-overview-button', 'n_clicks'),
     Input('sep-dec-event-view-button', 'n_clicks'),
     Input('jan-apr-overview-button', 'n_clicks'),
     Input('jan-apr-event-view-button', 'n_clicks')]
)
def go_to_page(sep_dec_overview_n_clicks, sep_dec_event_view_n_clicks, jan_apr_overview_n_clicks, jan_apr_event_view_n_clicks):
    ctx = callback_context

    if not ctx.triggered:
        return '/'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'sep-dec-overview-button' and sep_dec_overview_n_clicks > 0:
        return '/sep-dec-overview'
    elif button_id == 'sep-dec-event-view-button' and sep_dec_event_view_n_clicks > 0:
        return '/sep-dec-event-view'
    elif button_id == 'jan-apr-overview-button' and jan_apr_overview_n_clicks > 0:
        return '/jan-apr-overview'
    elif button_id == 'jan-apr-event-view-button' and jan_apr_event_view_n_clicks > 0:
        return '/jan-apr-event-view'
    return '/'

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('current-page-index', 'data', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    Input('current-page-index', 'data'),
    Input('cycle-started', 'data'),
    prevent_initial_call='initial_duplicate'
)
def cycle_pages(n_intervals, current_page_index, cycle_started):
    if not cycle_started:
        return Dash.no_update, Dash.no_update

    pages = [
        '/sep-dec-overview',
        '/sep-dec-event-view',
        '/jan-apr-overview',
        '/jan-apr-event-view'
    ]

    next_page_index = (current_page_index + 1) % len(pages)
    next_page = pages[next_page_index]

    return next_page, next_page_index

@app.callback(
    Output('cycle-started', 'data'),
    Input('cycle-button', 'n_clicks')
)
def start_cycle(n_clicks):
    if n_clicks > 0:
        return True
    return False

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, host='0.0.0.0', port=8050)
