"""
Author: Armand R. Quenum
Date: September 1, 2016
Title: 12 Day Program Milestone Project 
Description: 
Clone the Flask Demo repository and create your own Flask app on Heroku that accepts a stock ticker input 
from the user and plots closing price data for the last month. The Quandle WIKI dataset provides this data for free, and you 
can use Python's Requests library along with simplejson to access it in Python via API. You can analyze the data using pandas 
and plot using Bokeh. By the end you should have some kind of interactive visualization viewable from the Internet.

"""
# Module imports
import sys
import requests
import json
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components 
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

from flask import Flask,render_template,request
app = Flask(__name__)

@app.route('/index',methods=['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('userinfo_pg1.html')
  else:
    stock = request.form['ticker']
    
    dates, closing_prices = get_stock_data(stock, 30)
    
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    
    script, div = plot(dates, closing_prices)
    
    return render_template('userinfo_pg2.html', stock_symbol = stock.upper(), script=script, div=div, js_resources=js_resources, css_resources=css_resources)

@app.errorhandler(404)
def not_found(error):
  return render_template('userinfo_pg3.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
  return render_template('userinfo_pg3.html'), 500    

@app.errorhandler(Exception)
def unhandled_exception(e):
    return render_template('userinfo_pg3.html'), 500 

# Returns a line plot which can be embedded in a HTML document    
def plot(x, y):
  
  p = figure(title = 'Data From Quandle WIKI Set', x_axis_label='Date', x_axis_type='datetime')
  #p.y_range.start = 0
  #p.y_range.end = max(y)*1.1
  #p.x_range.start = x[-1]
  p.line(x, y)
  
  script, div = components(p)
  return script, div    

# Returns N days back of a stock ticker closing price valuations  
def get_stock_data(stock, days_back):
    
  url = 'https://www.quandl.com/api/v1/datasets/WIKI/'  
  data = requests.get(url + stock.lower())
  json_data = json.loads(data.text) # Type = Dict
  
  col_headers = json_data['column_names'] # Type = List
  stock_data = json_data['data'] # Type = List
  
  stock_df = pd.DataFrame(stock_data, columns = col_headers) # Type = Data Frame
  lastNdays = stock_df.iloc[:days_back]
  
  stock_dates = lastNdays['Date'].values.tolist()
  stock_dates = [str(date) for date in stock_dates]
  stock_dates = pd.to_datetime(pd.Series(stock_dates))
  
  stock_close = lastNdays['Close'].values.tolist()
  
  return stock_dates, stock_close  
  
if __name__ == '__main__':
    app.run(port=33507)