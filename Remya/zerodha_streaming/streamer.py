import datetime
import json
import logging
from kiteconnect import KiteTicker
import requests
from urllib.error import HTTPError

logging.basicConfig(level=logging.DEBUG)

#Access Token
def get_token():
    token_url = "http://localhost:8080/token"
    #logging.debug(urllib.request.urlopen("http://localhost:8080/token"))

    token=""
    try:
        respsone = requests.get(token_url)
        token=respsone.text
        logging.debug("token : "+token)
    except HTTPError as e:
        content = e.read()
    return token
# Initialise
kws = KiteTicker("0045k3j5nf3a1wyp", get_token())


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.debug("Ticks: {}".format(ticks))
  #  json_obj=json.loads(json.dumps(ticks,default=myconverter))
    response=requests.post("http://localhost:8080/add_ticks",json=json.dumps(ticks,default=myconverter))
    logging.debug("response: {}".format(response))

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    #indigo, indigo fut 1.ashok lay, ashok fut , 2. 90 CE , 3. 100,105,110
    ws.subscribe([4532225	,
3924481	,
3365633	,
3820033	,
1112065	,
3609857	,
2906881	,
5344513	,
5376257	,
7387905	,
3037185	,
5025537	,
5197313	,
2987777	,
1000449	,
4453633	,
695553	,
3226369	,
6505985	,
693249	,
692481	,
4700417	,
2726401	,
3893505	,
2681089	,
3834113	,
2729217	,
687873	,
6583809	,
4518657	,
4873217	,
2402561	,
2391553	,
4840449	,
2236417	,
2730497	,
3563521	,
2641409	,
4861953	,
6191105	,
681985	,
3725313	,
678145	,
3650561	,
648961	,
6491649	,
5786113	,
3454977	,
676609	,
3660545	,
2905857	,
4701441
])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [4532225	,
3924481	,
3365633	,
3820033	,
1112065	,
3609857	,
2906881	,
5344513	,
5376257	,
7387905	,
3037185	,
5025537	,
5197313	,
2987777	,
1000449	,
4453633	,
695553	,
3226369	,
6505985	,
693249	,
692481	,
4700417	,
2726401	,
3893505	,
2681089	,
3834113	,
2729217	,
687873	,
6583809	,
4518657	,
4873217	,
2402561	,
2391553	,
4840449	,
2236417	,
2730497	,
3563521	,
2641409	,
4861953	,
6191105	,
681985	,
3725313	,
678145	,
3650561	,
648961	,
6491649	,
5786113	,
3454977	,
676609	,
3660545	,
2905857	,
4701441
])

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()