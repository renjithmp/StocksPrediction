###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Zerodha technologies Pvt. Ltd.
#
# This is simple Flask based webapp to generate access token and get basic
# account info like holdings and order.
#
# To run this you need Kite Connect python client and Flask webserver
#
#   pip install Flask
#   pip install kiteconnect
#
#   python examples/simple_webapp.py
###############################################################################
import os
import json
import logging
from datetime import date, datetime
from decimal import Decimal

from flask import Flask, request, jsonify, session
from kiteconnect import KiteConnect
from elasticsearchdb import ElasaticSearchDB

logging.basicConfig(level=logging.INFO)

# Base settings
PORT = 8080
HOST = "127.0.0.1"

serializer = lambda obj: isinstance(obj, (date, datetime, Decimal)) and str(obj)  # noqa

# Kite Connect App settings. Go to https://developers.kite.trade/apps/
# to create an app if you don't have one.
kite_api_key = "0045k3j5nf3a1wyp"
kite_api_secret = "xuy3c7qumo6bf1cj484tysgkll680war"

# Create a redirect url
redirect_url = "http://{host}:{port}/login".format(host=HOST, port=PORT)

# Login url
login_url = "https://kite.trade/connect/login?api_key={api_key}".format(api_key=kite_api_key)

# Kite connect console url
console_url = "https://developers.kite.trade/apps/{api_key}".format(api_key=kite_api_key)

# App
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Templates
index_template = """
    <div>Make sure your app with api_key - <b>{api_key}</b> has set redirect to <b>{redirect_url}</b>.</div>
    <div>If not you can set it from your <a href="{console_url}">Kite Connect developer console here</a>.</div>
    <a href="{login_url}"><h1>Login to generate access token.</h1></a>"""

login_template = """
    <h2 style="color: green">Success</h2>
    <div>Access token: <b>{access_token}</b></div>
    <h4>User login data</h4>
    <pre>{user_data}</pre>
    <a target="_blank" href="/holdings.json"><h4>Fetch user holdings</h4></a>
    <a target="_blank" href="/orders.json"><h4>Fetch user orders</h4></a>
    <a target="_blank" href="https://kite.trade/docs/connect/v1/"><h4>Checks Kite Connect docs for other calls.</h4></a>"""


def get_kite_client():
    """Returns a kite client object
    """
    kite = KiteConnect(api_key=kite_api_key)
    if "access_token" in session:
        kite.set_access_token(session["access_token"])
    return kite


@app.route("/")
def index():
    return index_template.format(
        api_key=kite_api_key,
        redirect_url=redirect_url,
        console_url=console_url,
        login_url=login_url
    )


@app.route("/login")
def login():
    request_token = request.args.get("request_token")

    if not request_token:
        return """
            <span style="color: red">
                Error while generating request token.
            </span>
            <a href='/'>Try again.<a>"""

    kite = get_kite_client()
    data = kite.generate_session(request_token, api_secret=kite_api_secret)
    session["access_token"] = data["access_token"]
    es.store_token(session["access_token"])

    return login_template.format(
        access_token=data["access_token"],
        user_data=json.dumps(
            data,
            indent=4,
            sort_keys=True,
            default=serializer
        )
    )

@app.route("/holdings.json")
def holdings():
    kite = get_kite_client()
    holdings = kite.holdings()
    historicalData=kite.historical_data(instrument_token=13458434,from_date="2007-01-01",to_date ="2019-04-01",continuous=True,interval="day");
    ElasaticSearchDB.store_portfolio(holdings)
    return jsonify(holdings)




@app.route("/orders.json")
def orders():
    kite = get_kite_client()
    return jsonify(orders=kite.orders())

@app.route("/placeorder")
def placeorders():
    kite = get_kite_client()

    result =kite.place_order(tradingsymbol="SANWARIA",
                                exchange=kite.EXCHANGE_NSE,
                                transaction_type=kite.TRANSACTION_TYPE_SELL,
                                quantity=0,
                                order_type=kite.ORDER_TYPE_MARKET,
                                product=kite.PRODUCT_CNC,
                                variety=kite.VARIETY_REGULAR,


                             )
    return  jsonify(result)


@app.route("/instruments.json")
def instruments(stock_exchange="NSE"):

    kite = get_kite_client()
    exchange=kite.EXCHANGE_NSE
    if stock_exchange == "NFO":
        exchange=kite.EXCHANGE_NFO

    instruments = kite.instruments(exchange)

   # es.store_instruments(instruments)
    return jsonify(instruments)

@app.route("/storeAllNSEStocks")
def store_all_nse_stocks_historical_data(from_date="2019-04-01",to_date="2019-04-26",interval="day",continuous=False):
    kite = get_kite_client()
    holdings = kite.holdings()
    instrumentList=instruments()
    stored=True
    for instrument in instrumentList.json:
        if instrument["instrument_token"] == 163073:
            stored=True
        if stored:
            try:
                historicalData=kite.historical_data(instrument_token=instrument["instrument_token"],from_date=from_date,to_date =to_date,continuous=continuous,interval=interval);
                es.store_historica_data(historicalData,instrument)
            except:
                logging.info("token failed:"+str(instrument["instrument_token"]))
    return jsonify("OK")
@app.route("/add_ticks",methods = ['POST'])
def add_tick():
    ticks=request.get_json(force=True)
    es.store_ticks(ticks)
    return "OK"

@app.route("/token")
def access_token():
    latest_token=es.find_latest_token()
    return latest_token['hits']['hits'][0]['_source']['token']

@app.route("/storeAllFut")
def store_all_fut(from_date="2019-04-01",to_date="2019-04-26",interval="day",continuous=True):
    kite = get_kite_client()
    holdings = kite.holdings()
    instrumentList=instruments("NFO")
    #stored=False
    stored = True
    for instrument in instrumentList.json:
        if instrument["instrument_type"] == "FUT":
            if instrument["instrument_token"] == 13459458:
                stored = True
            if stored:
                try:
                    historicalData=kite.historical_data(instrument_token=instrument["instrument_token"],from_date=from_date,to_date =to_date,continuous=continuous,interval=interval);
                    es.store_historica_data(historicalData,instrument)
                except:
                    logging.info("token failed:" + str(instrument["instrument_token"]))
    return jsonify("OK")

@app.route("/storeAllCE")
def store_all_ce(from_date="2019-04-01",to_date="2019-04-26",interval="day",continuous=True):
    kite = get_kite_client()
    holdings = kite.holdings()
    instrumentList=instruments("NFO")
    #stored=False
    stored = True
    for instrument in instrumentList.json:
        if instrument["instrument_type"] == "CE":
            if instrument["instrument_token"] == 24467970:
                stored = True
            if stored:
                try:
                    historicalData=kite.historical_data(instrument_token=instrument["instrument_token"],from_date=from_date,to_date =to_date,continuous=continuous,interval=interval);
                    es.store_historica_data(historicalData,instrument)
                except:
                    logging.info("token failed:" + str(instrument["instrument_token"]))
    return jsonify("OK")

@app.route("/storeAllPE")
def store_all_pe(from_date="2019-04-01",to_date="2019-04-26",interval="day",continuous=True):
    kite = get_kite_client()
    holdings = kite.holdings()
    instrumentList=instruments("NFO")
    #stored=False
    stored = False
    for instrument in instrumentList.json:
        if instrument["instrument_type"] == "PE":
            if instrument["instrument_token"] == 12229890:
                stored = True
            if stored:
                try:
                    historicalData=kite.historical_data(instrument_token=instrument["instrument_token"],from_date=from_date,to_date =to_date,continuous=continuous,interval=interval);
                    es.store_historica_data(historicalData,instrument)
                except:
                    logging.info("token failed:" + str(instrument["instrument_token"]))
    return jsonify("OK")

if __name__ == "__main__":
    logging.info("Starting server: http://{host}:{port}".format(host=HOST, port=PORT))
    es=ElasaticSearchDB()
    app.run(host=HOST, port=PORT, debug=True)
