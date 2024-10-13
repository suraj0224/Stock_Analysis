
import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table, dcc, Output, Input,State
import yfinance as yf
from datetime import datetime
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')



app = Dash(__name__)

server=app.server

app.layout = html.Div(children=[
    html.Div(style={"background-color":"none","display":"flex","justify-content":"center","height":"none","margin":"0px"},className='joker',children=[html.H1(style={"background-color":"none","margin-bottom":"10px ","margin-top":"0px ","font-size":"24px"},children=["Stock Market Data"])]),
    
    html.Div(style={"display":"flex","margin-bottom":"10px","height":"50px","background-color":"#c5e788","border":"5px solid #e46161","border-radius":"12px","align-content":"center"},children=[
        html.Div(style={"display":"flex","height":"40px","width":"none","align-self":"center","background-color":"none"},children=[dcc.Input(id='input-on-submit', type='text', value="^NSEI", style={"display":"inline-block","font-size":"24px","background-color":"none","align-itmes": "center","border-radius":"12px"})]),
    html.Button('Submit', id='submit-val', n_clicks=0,style={"display":"inline-block","font-size":"18px","background-color":"#94dfe2","height":"30px","align-self":"center","margin":"0px 10px","border-radius":"12px"}),
    html.Div(id='container-button-basic',
             children='stock',style={"display":"inline-block","font-size":"24px","background-color":"none","align-self": "center","margin":"0px 10px"}),
    html.Div(style={"height":"40px","background-color":"none","display":"flex","align-self":"center"},children=[
     # Date range slider
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=datetime(datetime.today().year, 1, 1),
        end_date=datetime.today().date(),
        display_format='YYYY-MM-DD',
        className='date-picker',
        style={
                    'border': '1px solid #007BFF',  # Border color
                    'borderRadius': '5px',           # Rounded corners
                    'padding': '2px',                # Padding inside the component
                    'backgroundColor': '#none',     # Background color
                    'max-width': '100%' ,"height":"none",                  # Width of the date picker
                    "background-color":"black","display":"inline-block","align-self":"center","margin":"0px 10px","flex-shrink":"none"        # Keep the date picker inline
                }
    )]),
    
    
    
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
             "height":"40px",
            'width': '130px',  # Set width of the dropdown
            'padding': '0px',  # Add some padding
            'fontSize': '20px',  # Change font size
            'border': '2px solid #000',  # Add border
            'borderRadius': '10px',  # Rounded corners
            'backgroundColor': 'none',  # Background color
            'display':"inline-block",
            'margin':'0px',"background-color":"none","align-self":"center"
        }
    ),
    
    # Input for Daily Change %
    dcc.Input(id='change-filter', type='number', placeholder="Daily Change %",style={"font-size":"16px","margin":"20px","display":"inline-block","height":"30px","width":"130px","background-color":"none","align-self": "center"}),
    
    
    dcc.Checklist(
        id='change-type',   labelStyle={"font-size":"24px","background-color":"none","align-self": "center","margin-right":"10px"}, inputStyle={"transform":"scale(2.5)","margin":"10px","background-color":"yellow"}, style={"display":"inline-block","justify-content":"center","margin":"10px","background-color":"none","align-self": "center"},
        options=[
            {'label': 'Greater than', 'value': 'greater'},
            {'label': 'Less than', 'value': 'less'}
        ],
        
        value=[],
        inline=True
    )   
    
    ]),
    
      
    html.Div(style={"display":"flex"},children=[
        html.Div(style={"overflowY": "scroll", "height": "78vh", "width": "40%","display":"inline-block"},
                 children=[
                    # Table to display data
                    dash_table.DataTable( style_cell={"textAlign":"center",'minWidth': '10px','width': '15px','maxWidth': '15px', 'font_size': '18px',"width":"none"} , style_table={"width":"auto","margin":"auto","display":"block"},
                        id='table', 
                        columns=[
                            {'name': "Date", 'id': "Date"},
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
                    
                 ]    
        ),dcc.Graph(figure={}, id='controls-and-graph',style={"width":"60%","height":"80vh","display":"inline","border":"none"})
    ]
        
    )
    
    
        
    
    
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
    try:
        
        
        stock=ticker_value
        # print(stock,n_clicks)
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
            year_data["Average"]=year_data["Average"].round(2)
            year_data["Daily Change %"]=year_data["Daily Change %"].round(2)
            # month_data = month_data.sort_values(by=["Year",'Month_Num'], ascending=True)
            
            

            fig = px.line(year_data, x='Date', y='Average', title=f"{stock} over Time", labels={'Date': 'Date', 'Average': 'Average'})
            # Update the layout for styling
            fig.update_layout(
                title_font=dict(size=20),  # Change title font size if needed
                xaxis_title=dict(text='Year', font=dict(size=24, family='Arial', weight='bold')),
                yaxis_title=dict(text='Average', font=dict(size=24, family='Arial', weight='bold')),
                xaxis_tickfont=dict(size=18, family='Arial'),  # Style for x-axis ticks (years)
                yaxis_tickfont=dict(size=22, family='Arial')
                # plot_bgcolor='white',  # Optional: set background color
            )

                    # Update the line width
            fig.update_traces(line=dict(width=2))  # Adjust the number for desired thickness

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
            month_data["Average"]=month_data["Average"].round(2)
            month_data["Daily Change %"]=month_data["Daily Change %"].round(2)
            
            
            
            fig = px.line(month_data, x='Date', y='Average', title=f"{stock} over Time", labels={'Date': 'Date', 'Average': 'Average'})

            return ticker_value, month_data[['Date', 'Average', 'Daily Change %']].to_dict('records'), fig
        else:
            # Day-wise data (raw data)
            filtered_df["Date"]= filtered_df['Date'].dt.strftime('%Y-%m-%d')

            fig = px.line(filtered_df, x='Date', y='Average', title=f"{stock} over Time", labels={'Date': 'Date', 'Average': 'Average'})
        
            return ticker_value, filtered_df.to_dict('records'), fig
    except ValueError as ve:
        logging.error(ve)
        return f"Error: {str(ve)}", [], {}
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f'This stock "{ticker_value}" is not in the record', [], {}

    
    
    


# Run the app
if __name__ == '__main__':
    app.run(debug=True)