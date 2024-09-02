import os
from style import *
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dash import Dash, html, dcc, Output, Input

# ENVIROMENT VARIABLES
load_dotenv()
DB_USERNAME = os.getenv('DJANGO_USER')
DB_PASSWORD = os.getenv('DJANGO_PASSWORD')
DB_HOST = os.getenv('DJANGO_HOST')
DB_PORT = os.getenv('DJANGO_PORT')
DB_NAME = os.getenv('DJANGO_NAME')
DB_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

N_PLACES = 20


# DATABASE CONNECTION
engine = create_engine(DB_URL)
data = pd.read_sql('SELECT * FROM plates_platepaid', engine)

# COUNTING OCCUPACITY
occupied_places = pd.read_sql('SELECT COUNT(*) FROM plates_plate', engine)['count'][0]
occupacity_data = pd.DataFrame(['Free' for _ in range(N_PLACES)], columns=['status'])

if occupied_places > N_PLACES:
    extra_places = occupied_places - N_PLACES
    for i in range(extra_places):
        occupacity_data.loc[N_PLACES + i, 'status'] = 'Free'

occupacity_data.loc[:occupied_places - 1, 'status'] = 'Occupied'



# CONVERTING INTO RIGHT DATA FORMAT
data['arrived_at'] = data['arrived_at'].dt.tz_convert('Europe/Warsaw')
data['paid_at'] = data['paid_at'].dt.tz_convert('Europe/Warsaw')

# DASH APP
app = Dash(__name__)
app.layout = html.Div([
                html.Div([
                    dcc.Graph(id='cars_per_hour'),
                    dcc.DatePickerSingle(id='date_hour', 
                                         display_format='YYYY-MM-DD', 
                                         date=datetime.now().date(), 
                                         style={'position': 'absolute', 'top': '0', 'right': '0'}),
                ], style=cars_per_hour_style),
                html.Div([
                    dcc.Graph(id='cars_on_parking'),
                    dcc.DatePickerSingle(id='date_parking', 
                                         display_format='YYYY-MM-DD', 
                                         date=datetime.now().date(), 
                                         style={'position': 'absolute', 'top': '0', 'left': '0'}),
                ], style=cars_already_parked_style),
                html.Div([
                    dcc.Graph(id='profit_per_month'),
                    dcc.DatePickerSingle(id='date_month', 
                                         display_format='YYYY-MM', 
                                         date=datetime.now().date(),
                                         style={'position': 'absolute', 'top': '0', 'right': '0', 'width': '15%'}),
                ], style=profit_per_month_style),
                html.Div([
                    dcc.Graph(figure=px.pie(
                                data_frame=occupacity_data,
                                names='status',
                                hole=0.7,
                            ).update_layout(
                                title={
                                    'text': f'Currently occupied places: {str(occupied_places)}/{N_PLACES}' 
                                            if occupied_places <= N_PLACES 
                                            else f'Parking overflowed! {str(occupied_places)}/{N_PLACES} occupied (extra: {extra_places})',
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top'
                                }
                            )),
                ], style=occupacity_style),
                html.Div([
                    dcc.Graph(figure=go.Figure(
                        data=go.Table(
                            header=dict(
                                values=['Plate code', 'Arrived at']
                            ), cells=dict(
                                values=pd.read_sql("SELECT plate_code, TO_CHAR(arrived_at, 'YYYY-MM-DD HH24:MI:SS') FROM plates_plate", engine).T
                            ),
                        )
                    ).update_layout(
                        title={
                            'text': 'Cars currently on parking',
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        }
                    ), style=table_style),
                ])
            ])

# FUNCTIONS
@app.callback(Output('cars_per_hour', 'figure'), 
              Input('date_hour', 'date'))
def cars_per_hour(date):

    # If date isn't specified, use today's date
    if date is None:
        date = datetime.now().date()

    # Convert date to datetime object
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetching data from the current day
    df_hours = data[data['arrived_at'].dt.date == date]

    # Grouping by hour
    all_hours = pd.DataFrame({'hour': range(24)})
    for i, row in all_hours.iterrows():
        hour = row['hour']
        all_hours.at[i, 'count'] = len(df_hours[df_hours['arrived_at'].dt.hour == hour])

    # Plotting
    fig = px.bar(all_hours, 
                 x='hour', 
                 y='count',
                 text_auto=True,
            )
    fig.update_layout(
        title={
            'text': 'Number of cars arriving per hour',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Hour',
        yaxis_title='Number of cars',
    )
    fig.update_xaxes(tickvals=list(range(24)))
    fig.update_yaxes(tickvals=list(range(all_hours['count'].astype(int).max() + 1)))
    return fig


@app.callback(Output('cars_on_parking', 'figure'), 
              Input('date_parking', 'date'))
def cars_on_parking(date):

    if date is None:
        date = datetime.now().date()

    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetching data from the current day
    df_hours = data[(data['arrived_at'].dt.date >= date) & (data['paid_at'].dt.date <= date)]

    # Grouping by hour
    all_hours = pd.DataFrame({'hour': range(24)})

    # Counting cars on parking per hour
    for i, row in all_hours.iterrows():
        hour = row['hour']
        all_hours.at[i, 'count'] = len(df_hours[(df_hours['arrived_at'].dt.hour <= hour) & (df_hours['paid_at'].dt.hour >= hour)])

    # Plotting
    fig = px.bar(all_hours, 
                 x='hour', 
                 y='count',
                 text_auto=True,
            )
    fig.update_layout(
        title={
            'text': 'Number of cars currently at the parking per hour',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Hour',
        yaxis_title='Number of cars',
    )
    fig.update_xaxes(tickvals=list(range(24)))
    fig.update_yaxes(tickvals=list(range(0, all_hours['count'].astype(int).max() + 1, 4)))

    return fig


@app.callback(Output('profit_per_month', 'figure'),
              Input('date_month', 'date'))
def profit_per_month(date):
    
    if date is None:
        date = datetime.now().date()

    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Fetching data from the current month
    df_month = data[(data['paid_at'].dt.month == date.month) & (data['paid_at'].dt.year == date.year)]

    # Grouping by day
    all_days = pd.DataFrame({'day': range(1, 32)})

    # Counting profit per day
    for i, row in all_days.iterrows():
        day = row['day']
        all_days.at[i, 'profit'] = df_month[df_month['paid_at'].dt.day == day]['cost'].sum()

    # Counting whole month profit
    whole_profit = all_days['profit'].sum()

    # Plotting
    fig = px.line(all_days, 
                  x='day', 
                  y='profit',
            )
    fig.update_layout(
        title={
            'text': 'Profit per day - whole month profit: ' + str(round(whole_profit, 2)) + ' PLN',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Day',
        yaxis_title='Profit',
    )
    fig.update_xaxes(tickvals=list(range(1, 32)))
    fig.update_yaxes(tickvals=list(range(0, int(all_days['profit'].max()) + 1, 100)))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)