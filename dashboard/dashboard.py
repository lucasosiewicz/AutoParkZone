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
                html.H1('Cars per hour'),
                dcc.DatePickerSingle(id='date', display_format='YYYY-MM-DD', date=datetime.now().date()),
                dcc.Graph(id='cars_per_hour', style={'width': '75%'}),
              ], style={
                    'position': 'fixed',
                    'bottom': '0',       # Ustawienie dolnego marginesu na 0
                    'right': '0',        # Ustawienie prawego marginesu na 0
                    'display': 'flex',   # Użycie flexboxa do ułożenia elementów obok siebie
                    'align-items': 'center',
                    'background-color': 'white',  # Tło białe (możesz zmienić)
                    'padding': '10px',   # Opcjonalne padding
                    'border': '1px solid #ccc',  # Opcjonalna ramka
                    'box-shadow': '0px 0px 10px rgba(0,0,0,0.1)'  # Opcjonalny cień
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
    fig = px.bar(df, x='hour', y='count', labels={'hour': 'Hour', 'count': 'Number of cars'})
    fig.update_xaxes(tickvals=list(range(24)))
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)