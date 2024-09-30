
import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table, dcc, Output, Input,State
import yfinance as yf
from datetime import datetime



app = Dash(__name__)

server=app.server

today = datetime.today()
start_of_year = datetime(today.year, 1, 1)



app.layout = html.Div([
    html.H1("Stock Market Data"),
    
     html.Div(dcc.Input(id='input-on-submit', type='text',value="^NSEI",style={"display":"inline-block","font-size":"28px"})),
    html.Button('Submit', id='submit-val', n_clicks=0,style={"display":"inline-block","font-size":"24px"}),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit',style={"display":"flex","font-size":"24px"}), 
   
    
    # Date range slider
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=start_of_year,
        end_date=today,
        display_format='YYYY-MM-DD',
      style={
                'border': '1px solid #007BFF',  # Border color
                'borderRadius': '5px',           # Rounded corners
                'padding': '2px',                # Padding inside the component
                'backgroundColor': '#f8f9fa',     # Background color
                'width': 'auto',                  # Width of the date picker
                'display': 'inline-block',         # Keep the date picker inline
            }
    ),
    
    
    
     # input for monthwise or date wise
    dcc.Dropdown(
        id='view-selector',
        options=[
            {'label': 'Daily', 'value': 'day'},
            {'label': 'Monthly', 'value': 'month'},
            {'label': 'Yearly', 'value': 'year'}
        ],
        value='day',  # Default view is day-wise
        clearable=False,
         style={
             'height':'auto',
            'width': '200px',  # Set width of the dropdown
            'padding': '0px',  # Add some padding
            'fontSize': '24px',  # Change font size
            'border': '2px solid #000',  # Add border
            'borderRadius': '10px',  # Rounded corners
            'backgroundColor': '#f9f9f9',  # Background color
            'display':"inline-block",
            'margin':'0px'
        }
    ),
    
    # Input for Daily Change %
    dcc.Input(id='change-filter', type='number', placeholder="Daily Change %",style={"font-size":"24px","margin":"20px","display":"inline-block"}),
    
    
    dcc.Checklist(
        id='change-type',   labelStyle={"font-size":"28px"}, inputStyle={"transform":"scale(2.5)","margin":"20px"}, style={"display":"inline-block","justify-content":"center","margin":"20px"},
        options=[
            {'label': 'Greater than', 'value': 'greater'},
            {'label': 'Less than', 'value': 'less'}
        ],
        
        value=[],
        inline=True
    ),
    
    # Table to display data
    dash_table.DataTable( style_cell={"textAlign":"center", 'font_size': '24px'} , style_table={"width":"40%","margin":"auto"},
        id='table', 
        columns=[
            {'name': "Date/Month", 'id': "Date"},
            {"name":"Average","id":"Average"},
            {"name":"Daily Change %","id":"Daily Change %"}
            ],
        data=[],
        style_data_conditional=[
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
    Output('container-button-basic', 'children'),
    Output('table', 'data'),
    Output(component_id='controls-and-graph', component_property='figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('change-filter', 'value'),
     Input('change-type', 'value'),
     Input('view-selector', 'value'),
     Input('submit-val', 'n_clicks'),
     State('input-on-submit', 'value')
      ]
    
)




def update_table(start_date, end_date, change_value, change_type, view_type, n_clicks, ticker_value):
    
    
    stock=ticker_value
    print(stock,n_clicks)
    nifty = yf.download(stock, start='2000-01-01', end=None)
    nifty = pd.DataFrame(nifty)

    nifty['Daily Change %'] = nifty['Adj Close'].pct_change() * 100
    nifty.drop(columns=["Volume","Adj Close"],inplace=True)

    nifty[["Open","High","Low","Close"]]=nifty[["Open","High","Low","Close"]].astype(int)
    nifty.reset_index(inplace=True)

    # instead of considering all four columns, we are creating a new column of average of all the 4 columns to easily study 
    nifty["Average"]=(nifty["Open"]+nifty["High"]+nifty["Low"]+nifty["Close"])/4

    nifty=nifty[["Date","Average","Daily Change %"]]
    nifty=nifty.drop(index=0)
    nifty['Date'] = pd.to_datetime(nifty['Date'])

    nifty["Daily Change %"]=nifty["Daily Change %"].round(2)

    df=nifty
    df["Month"]=df['Date'].dt.month_name()
    df["Month_Num"]=df['Date'].dt.month
    df['Year'] = df['Date'].dt.year

    
    
    if view_type == 'year':
        # Aggregate data by month (sum of values) and calculate daily change percentage mean
        year_data = df.groupby('Year').agg({
            'Average': 'mean',  # mean of values for each month
            'Daily Change %': 'sum'  # Average daily change percentage for each month
        }).reset_index()
        
        if change_value is not None:
            if 'greater' in change_type:
                year_data = year_data[year_data['Daily Change %'] > change_value]
            if "less" in change_type:
                year_data = year_data[year_data['Daily Change %'] < change_value]
            else:
                year_data=year_data[year_data["Daily Change %"].abs()>change_value]   
        
        year_data['Date'] = year_data['Year']
        # month_data = month_data.sort_values(by=["Year",'Month_Num'], ascending=True)
        
         

        fig = px.line(year_data, x='Date', y='Average', title='Nifty over Time', labels={'Date': 'Date', 'Average': 'Average'})

        return ticker_value, year_data[['Date', 'Average', 'Daily Change %']].to_dict('records'), fig
  
    # Filter by date range
    filtered_df=df2 = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Filter by Daily Change %
    if change_value is not None:
        if 'greater' in change_type:
            filtered_df = filtered_df[filtered_df['Daily Change %'] > change_value]
            
        if "less" in change_type:
            filtered_df = filtered_df[filtered_df['Daily Change %'] < change_value]
            
        else:
            filtered_df=filtered_df[filtered_df["Daily Change %"].abs()>change_value]    
    filtered_df=filtered_df.sort_values(by="Date",ascending=False)
    # df2=df2.sort_values(by="Date",ascending=False)
    
    if view_type == 'month':
        # Aggregate data by month (sum of values) and calculate daily change percentage mean
        month_data = df2.groupby(['Year','Month',"Month_Num"]).agg({
            'Average': 'mean',  # mean of values for each month
            'Daily Change %': 'sum'  # Average daily change percentage for each month
        }).reset_index()
        
        if change_value is not None:
            if 'greater' in change_type:
                month_data = month_data[month_data['Daily Change %'] > change_value]
            if "less" in change_type:
                month_data = month_data[month_data['Daily Change %'] < change_value]
            else:
                month_data=month_data[month_data["Daily Change %"].abs()>change_value]   
        
        month_data['Date'] = month_data['Year'].astype(str) + "-" + month_data['Month']
        month_data = month_data.sort_values(by=["Year",'Month_Num'], ascending=True)
        
         
        
        fig = px.line(month_data, x='Date', y='Average', title='Nifty over Time', labels={'Date': 'Date', 'Average': 'Average'})

        return ticker_value, month_data[['Date', 'Average', 'Daily Change %']].to_dict('records'), fig
    else:
        # Day-wise data (raw data)
        filtered_df["Date"]= filtered_df['Date'].dt.strftime('%Y-%m-%d')

        fig = px.line(filtered_df, x='Date', y='Average', title='Nifty over Time', labels={'Date': 'Date', 'Average': 'Average'})
    
        return ticker_value, filtered_df.to_dict('records'), fig

    
    
    


# Run the app
if __name__ == '__main__':
    app.run(debug=True)