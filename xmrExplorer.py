#!/usr/bin/env python
import json,pickle,pprint,re,sqlite3,sys,syslog,time
from collections import OrderedDict
from operator import itemgetter
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
from flask_caching import Cache
import requests
import xmrfmt


daemon_host='127.0.0.1'
daemon_port=18081
url = "http://" + daemon_host + ":" + str(daemon_port) + "/json_rpc"
id = '42'

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
#Compress(app)


def is_hex(s):                                         
    return re.search(r'^[0-9A-Fa-f]+$', s) is not None

def getTX(txid):
    try:
        url = 'http://127.0.0.1:18081/gettransactions'
        txPost = requests.post(url, data=json.dumps({'txs_hashes':[str(txid)],'decode_as_json': True}), headers={'content-type': 'application/json'})
        txResponse = txPost.json()['txs'][0]
        if txPost.status_code == 200:
            return txResponse
        else:
            return False
        #
    except Exception as e:
        return False
        print(str(e))

def getTXPool():
    try:
        url = 'http://127.0.0.1:18081/get_transaction_pool'
        txpoolPost = requests.post(url, headers={'content-type': 'application/json'})
        txpoolResponse = txpoolPost.json()
        if txpoolPost.status_code == 200:
            if len(txpoolResponse['transactions']) >= 1:
                for item in txpoolResponse['transactions']:
                    item['fee'] = float("{:.8f}".format(xmrfmt.AmountToString(item['fee'])))
                    item['receive_time'] = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(item['receive_time']))
                return txpoolResponse
            else:
                return False
        else:
            return False
        #
    except Exception as e:
        return False
        print(str(e))

def getBlock(height=1):
    try:
        getBlockData = {"jsonrpc":"2.0","method":"getblock","id":id,"params":{"height":height}}
        getBlockPost = requests.post(url, json=getBlockData)
        getBlockResp = getBlockPost.json()['result']
        #pprint.pprint(getBlockResp)
        if getBlockPost.status_code == 200:
            return getBlockResp
        else:
            return False
        #
    except Exception as e:
        print(str(e))
        return False

@cache.cached(timeout=60, key_prefix='blockstats')
def blockstats():
    try:
        getInfoData = {"jsonrpc":"2.0","method":"get_info","id":id}
        getInfoPost = requests.post(url, json=getInfoData)
        getInfoResp = getInfoPost.json()['result']
        #pprint.pprint(getInfoResp)
        if getInfoPost.status_code == 200:
            return getInfoResp
        else:
            return False
        #
    except Exception as e:
        print(str(e))
        return False

@app.errorhandler(404)
@cache.cached(timeout=60)
def error404(e):
    return render_template('404.jinja', page='error',blockstats=blockstats()), 404
    #return render_template('404.jinja'), 404

@app.errorhandler(410)
@cache.cached(timeout=60)
def error410(e):
    return render_template('410.jinja', page='error',blockstats=blockstats()), 410

@app.errorhandler(500)
@cache.cached(timeout=60)
def error500(e):
    return render_template('500.jinja', page='error',blockstats=blockstats()), 500



@app.route('/block/<block>')
@cache.cached(timeout=60)
def block(block):
    try:
        blockData = getBlock(int(block))
        #print(type(blockData))
        try:
            blockData['block_header']['timestamp'] = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(blockData['block_header']['timestamp']))
            blockData['block_header']['reward'] = float("{:.8f}".format(xmrfmt.AmountToString(blockData['block_header']['reward'])))
        except:
            blockData['block_header']['timestamp'] = "Err!"
            blockData['block_header']['reward'] = "Err!"
    except Exception as e:
        blockData = False
        print(str(e))
        #blockList.append({metric:{'current': currentMetric, 'full': metricFull}})

    return render_template('block.jinja', page='block',blockstats=blockstats(),blockData=blockData)


@app.route('/', methods=["GET"])
@cache.cached(timeout=60)
def blockexplorer():
    #We normal just use the function in the render_template, but we need access to the current height.
    stats = blockstats()
    height = stats['height']
    #print(height)
    #
    blockList = []
    for block in reversed(range(int(height)-25,height)):
        try:
            blockData = getBlock(block)
            #print(blockData)
            try:
                blockData['block_header']['timestamp'] = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(blockData['block_header']['timestamp']))
            except:
                blockData['block_header']['timestamp'] = "Err!"
            blockList.append(blockData)
        except Exception as e:
            blockList = False
            print(str(e))

    return render_template('blockexplorer.jinja', page='blockexplorer',blockstats=stats,blockList=blockList)



@app.route('/expsearch/', methods=["GET", "POST"])
def expsearch():
    if request.method == 'POST':
        #print(request.form)
        if request.form['blocksearch']:
            if is_hex(request.form['blocksearch']):
                return redirect(url_for('block', block=request.form['blocksearch']))
            else:
                return render_template('error.jinja', page='error',blockstats=blockstats())
        elif request.form['txsearch']:
            if is_hex(request.form['txsearch']):
                return redirect(url_for('txid', txid=request.form['txsearch']))
            else:
                return render_template('error.jinja', page='error',blockstats=blockstats())
        else:
            return redirect(url_for('blockexplorer'))
    else:
        return redirect(url_for('blockexplorer'))



@app.route('/txid/<txid>')
@cache.cached(timeout=60)
def txid(txid):
    try:
        txDataFull = getTX(txid)
        txData = (txDataFull,str(txDataFull['as_json']))
    except Exception as e:
        txData = False
        print(str(e))

    return render_template('txid.jinja', page='txid',blockstats=blockstats(),txData=txData)


if __name__ == "__main__":
    @app.route('/assets/<path:path>')
    def send_assets(path):
        return send_from_directory('assets', path)
    app.run(debug=True,host='0.0.0.0',port=8888)

