
import pandas as pd
import plotly.express as px
from dash import Dash, html, dash_table, dcc, Output, Input,State
import yfinance as yf
from datetime import datetime
import logging
import pytz
import dash_bootstrap_components as dbc

ist=pytz.timezone("Asia/Kolkata")
utc_now=datetime.now(pytz.utc)
ist_now=utc_now.astimezone(ist)

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

app = Dash(__name__)

GA_TRACKING_ID="G-9ET5TW2W6J"

server=app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script async src="https://www.googletagmanager.com/gtag/js?id=''' + GA_TRACKING_ID + '''"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', ''' + GA_TRACKING_ID + ''', { 'anonymize_ip': true });
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(children=[
    html.Div(className='joker',children=[html.H1(className="top-box",children=["Stock Market Data"])]),
    
    html.Div(className="nav-box",children=[
        html.Div(className="input-box",children=[dcc.Input(id='input-on-submit', type='text', value="^NSEI",className="dccinput" )]),
    html.Button('Submit', id='submit-val', n_clicks=0,className="button"),
    html.Div(id='container-button-basic',children='stock'),
    html.Div(className="date-box",children=[
     # Date range slider
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=datetime(datetime.today().year, 1, 1),
        end_date=ist_now.date(),
        display_format='YYYY-MM-DD',
        className='date-picker'
     
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
        clearable=False
    ),
    
    # Input for Daily Change %
    dcc.Input(id='change-filter', type='number', placeholder="Daily Change %"),

    dcc.Checklist(
        id='change-type',   labelStyle={"className":"labelcss"}, inputStyle={"className":"inputcss"},
        options=[{'label': 'Greater than', 'value': 'greater'},{'label': 'Less than', 'value': 'less'}],value=[],inline=True
    )   
    
    ]),
    
     dcc.Loading(  # Add Loading component here
            id="loading",
            type="graph",  # You can choose "graph","cube","circle","dot","default
            children=[  
        html.Div(className="body-box",children=[
            html.Div(className="table-box",
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
            ),html.Div(className="graph-box",children=[dcc.Graph(figure={}, id='controls-and-graph')]),
            dcc.Store(id='screen-size', data=''),
            html.Script('window.onresize = function() { var size = window.innerWidth; document.getElementById("screen-size").value = size; };')
        ]
            
        )
            ])
        
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
     Input('screen-size', 'data'),
     State('input-on-submit', 'value')
      ]
    
)

def update_table(start_date, end_date, change_value, change_type, view_type, n_clicks,screen_size,ticker_value):
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

        # Update the layout for styling
        # default setting 
        title_font = dict(size=20)
        xaxis_title = dict(text='Year', font=dict(size=24, family='Arial', weight='bold'))
        yaxis_title = dict(text='Average', font=dict(size=24, family='Arial', weight='bold'))
        xaxis_tickfont = dict(size=18, family='Arial')
        yaxis_tickfont = dict(size=22, family='Arial')
        plot_bgcolor="red"
        
        # applying new setting on screen size 
        print("here is my"+screen_size)
        if screen_size and int(screen_size) < 480:
            title_font['size']=10
            xaxis_title['font']['size'] = 12  # Example: larger font for wider screens
            yaxis_title['font']['size'] = 15
            xaxis_tickfont['size'] = 12
            yaxis_tickfont['size'] = 13
            plot_bgcolor="white"
        
        
            
                
        
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
            
            fig.update_layout(title_font=title_font, xaxis_title=xaxis_title, yaxis_title=yaxis_title, xaxis_tickfont=xaxis_tickfont,yaxis_tickfont=yaxis_tickfont, plot_bgcolor=plot_bgcolor)
            
            
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