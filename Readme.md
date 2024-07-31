# HotelMap Forecast Dashboard

## Overview
The Dashboard is a web-based application developed using Dash and Python. It provides visualizations and insights into hotel booking data, allowing users to view both an overview of bookings and detailed event views. It displays Rooms Booked as a growing quadrilateral inside an area representing the Forecast.

## Features
**Overview View:** Displays a grid representing the forecast and booked rooms, with different colors indicating booking status.
**Event View:** Provides detailed information on individual events, with each event represented as a grid.
**Cycle Views:** Start a cycle that automatically switches between different views.

## Installation

- Prerequisites
    Python 3.6 or higher
    Pip (Python package installer)

- Clone the Repository
    `git clone <repository-url>`
    `cd <repository-directory>`

- Create a virtual environment (recommended):
    `python -m venv venv`
    `source venv/bin/activate`

- Install the required packages:
    `pip install dash`
    `pip install pandas`

- Run the Application
    `python app.py`
    Visit http://localhost:8050 in your web browser to view the dashboard.

## Navigation
**Home Page:** The landing page of the dashboard with buttons to navigate to different views.
**Overview SEP-DEC:** View the booking overview for September to December 2024.
**Event View SEP-DEC:** View detailed event data for September to December 2024.
**Overview JAN-APR:** View the booking overview for January to April 2025.
**Event View JAN-APR:** View detailed event data for January to April 2025.
**Cycle Views:** Start a cycle that automatically switches between different views.

## Screen Orientation
The dashboard automatically detects if the device is in portrait or landscape mode and adjusts the layout accordingly for the overview page. The event view page needs manually changing, change the `max_rows` value to `15` for portrait and `10` for landscape screens, this can be found on line 145 of `dashboard.py`.

## Data Files
The data files (*booking_data_sep_dec.csv* and *booking_data_jan_apr.csv*) should be placed in the same directory as `app.py`. These files contain the forecast and rooms booked data for the respective periods.
