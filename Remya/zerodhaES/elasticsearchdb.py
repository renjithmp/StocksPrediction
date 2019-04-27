from datetime import datetime, timezone

import pytz
from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from flask_restful import Resource, Api
import json
import uuid
from tzlocal import get_localzone
from Expando import Expando


class ElasaticSearchDB(Resource):
    es = Elasticsearch()
    def __init__(self):
        self.es = Elasticsearch()  # Instance Variable

    def get(self):
        #es = Elasticsearch()
        results = self.es.get(index='kibana_sample_data_ecommerce', doc_type='_doc', id='IOxi7GkBZhg0znMTmZ_Q')
        return jsonify(results['_source'])

    def store_portfolio(self,holdings):
        id=1
        for holding in holdings:
            result = self.es.index(index='portfolio', doc_type='zerodha', id=id, body=holding)
            id=id+1

    def store_instruments(self,instruments):
        #es = Elasticsearch()
        id=1
        for instrument in instruments:
            result = self.es.index(index='instruments', doc_type='zerodha', id=id, body=instrument)
            id=id+1

    def store_tick(self, tick):
        #for instrument in instruments:
        result = self.es.index(index='ticks', doc_type='zerodha', id=id, body=tick)

    def gendata(self,ticks):
        ticks_list = json.loads(ticks)
        for tick in ticks_list:
            yield {
                "_index": "ticks",
                "_type": "zerodha",
                "doc": str(tick),
            }
    def store_ticks(self, ticks):
        ticks_list=json.loads(ticks)
        for tick in ticks_list:
            now_utc = datetime.utcnow()
            now_local = now_utc.astimezone(get_localzone())
            tick['timestamp1']=now_utc.isoformat()
            #tick['_id'] = uuid.uuid4()
            result = self.es.index(id=uuid.uuid4(), index='ticks', doc_type='zerodha', body=json.dumps(tick,default=self.myconverter))

        #for instrument in instruments:
        #k = (
        #k=   {
         #   "_index": "ticks_test",
          #  "_type": "zerodha",
           # "_source": json.dumps(ticks_list[0]),
        #}
        #body=','.join(str(v) for v in ticks_list)

#        result = self.es.bulk(True,body=k)
        #result = self.es.bulk(index="ticks_test",doc_type="zerodha", body=json.dumps(body))
        #result= self.es.bulk(self.gendata(ticks))
    def myconverter(this,o):
        if isinstance(o, datetime):
            return o.__str__()
    def store_token(self, token):
        # for instrument in instruments:
        body={}
        body["token"]=token
        body["timestamp1"]=datetime.now()
        result = self.es.index(index='zerodha_tokens', doc_type='zerodha', id=id, body=json.dumps(body,default=self.myconverter))
    def find_latest_token(self):
        # for instrument in instruments:
        result = self.es.search(index='zerodha_tokens', doc_type='zerodha', size=1,sort="timestamp.keyword:desc")
        return result

    def store_historica_data(self, historicalData,instrument):

        for candle in historicalData:
            candle["instrument_name"]=instrument["tradingsymbol"]
            candle["instrument"] = instrument
            candle["timestamp_iso"] =candle["date"].isoformat()
            now_utc = datetime.utcnow()
            candle['added_time'] = now_utc.isoformat()
            # tick['_id'] = uuid.uuid4()
            result = self.es.index(id=uuid.uuid4(), index='historical_data', doc_type='_doc',
                                   body=json.dumps(candle, default=self.myconverter))


