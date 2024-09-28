
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import yfinance as yf
from datetime import datetime

nifty = yf.download('^NSEI', start='2000-01-01', end=None)

nifty['Daily Change %'] = nifty['Adj Close'].pct_change() * 100
nifty.drop(columns=["Volume","Adj Close"],inplace=True)

nifty[["Open","High","Low","Close"]]=nifty[["Open","High","Low","Close"]].astype(int)
nifty.reset_index(inplace=True)

# instead of considering all four columns, we are creating a new column of average of all the 4 columns to easily study 
nifty["Average"]=(nifty["Open"]+nifty["High"]+nifty["Low"]+nifty["Close"])/4

nifty=nifty[["Date","Average","Daily Change %"]]
nifty=nifty.drop(index=0)
nifty['Date'] = nifty['Date'].dt.strftime('%Y-%m-%d')

df=nifty
df["Daily Change %"]=df["Daily Change %"].round(2)

app = Dash(__name__)

server=app.server

today = datetime.today()
start_of_year = datetime(today.year, 1, 1)


app.layout = html.Div([
    html.H1("Stock Market Data"),
    
    # Date range slider
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=start_of_year,
        end_date=today,
        display_format='YYYY-MM-DD',
    ),
    
    # Input for Daily Change %
    dcc.Input(id='change-filter', type='number', placeholder="Daily Change %",style={"font-size":"24px","margin":"20px"}),
    
    dcc.Checklist(
        id='change-type',   labelStyle={"font-size":"28px"}, inputStyle={"transform":"scale(2.5)","margin":"20px"}, style={"display":"flex","justify-content":"center","margin":"20px"},
        options=[
            {'label': 'Greater than', 'value': 'greater'},
            {'label': 'Less than', 'value': 'less'}
        ],
        value=['greater'],
        inline=True
    ),
    
    # Table to display data
    dash_table.DataTable( style_cell={"textAlign":"center", 'font_size': '24px'} , style_table={"width":"40%","margin":"auto"},
        id='table', columns=[{'name': col, 'id': col} for col in df.columns],style_data_conditional=[
            # Style for values less than -2.5 (Dark Red)
            {
                'if': {
                    'filter_query': '{Daily Change %} < -2.5',
                    'column_id': 'Daily Change %'
                },
                'backgroundColor': 'darkred',
                'color': 'white'
            },
            # Style for values less than -1 (Light Orange)
            {
                'if': {
                    'filter_query': '{Daily Change %} < -1 && {Daily Change %} >= -2.5',
                    'column_id': 'Daily Change %'
                },
                'backgroundColor': '#fa8107',
                'color': 'black'
            },
            # Style for values greater than 1 (Yellow)
            {
                'if': {
                    'filter_query': '{Daily Change %} > 1 && {Daily Change %} <= 2.5',
                    'column_id': 'Daily Change %'
                },
                'backgroundColor': '#d6fa07',
                'color': 'black'
            },
            # Style for values greater than 2.5 (Dark Green)
            {
                'if': {
                    'filter_query': '{Daily Change %} > 2.5',
                    'column_id': 'Daily Change %'
                },
                'backgroundColor': 'darkgreen',
                'color': 'white'
            }
        ]
),
    dcc.Graph(figure={}, id='controls-and-graph')
    
])

# Callback for filtering data
@app.callback(
    Output('table', 'data'),
    Output(component_id='controls-and-graph', component_property='figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('change-filter', 'value'),
     Input('change-type', 'value')]
)
def update_table(start_date, end_date, change_value, change_type):
    # Filter by date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Filter by Daily Change %
    if change_value is not None:
        if 'greater' in change_type:
            filtered_df = filtered_df[filtered_df['Daily Change %'] > change_value]
        if "less" in change_type:
            filtered_df = filtered_df[filtered_df['Daily Change %'] < change_value]
        else:
            filtered_df=filtered_df[filtered_df["Daily Change %"].abs()>change_value]    
    filtered_df=filtered_df.sort_values(by="Date",ascending=False)
    fig = px.line(filtered_df, x='Date', y='Average', title='Nifty over Time', labels={'Date': 'Date', 'Average': 'Average'})

    
    return filtered_df.to_dict('records'), fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)