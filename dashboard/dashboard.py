import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
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

# DATABASE CONNECTION
engine = create_engine(DB_URL)
data = pd.read_sql('SELECT * FROM plates_platepaid', engine)


# DASH APP
app = Dash(__name__)
app.layout = html.Div([
                dcc.DatePickerSingle(id='date', display_format='YYYY-MM-DD', date=datetime.now().date(), 
                                     style={'position': 'realtive', 'align': 'center'}),
                dcc.Graph(id='cars_per_hour', style={'height': '75%'}),
            ], style={
                    'position': 'fixed',
                    'top': '0',       
                    'right': '0',        
                    'display': 'flex'   
              })

# FUNCTIONS
@app.callback(Output('cars_per_hour', 'figure'), 
              Input('date', 'date'))
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
    df_count = df_hours.groupby(df_hours['arrived_at'].dt.hour).size().reset_index()
    df_count.columns = ['hour', 'count']

    # Merge all hours with the count
    df = pd.merge(all_hours, df_count, on='hour', how='left').fillna(0)

    # Plotting
    fig = px.bar(df, 
                 x='hour', 
                 y='count'
            )
    fig.update_layout(
        title={
            'text': 'Number of cars per hour',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Hour',
        yaxis_title='Number of cars',
    )
    fig.update_xaxes(tickvals=list(range(24)))
    fig.update_yaxes(tickvals=list(range(0, df['count'].astype(int).max() + 1)))
    return fig





if __name__ == '__main__':
    app.run_server(debug=True)