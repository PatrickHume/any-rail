from flask import Flask, render_template, request, jsonify
import requests
import json
import os.path

import os
import signal
import subprocess


app = Flask(__name__)

@app.route('/')
def get_beer():
    r = requests.get('https://api.punkapi.com/v2/beers/random')
    beerjson = r.json()
    beer = {
        'name': beerjson[0]['name'],
        'abv': beerjson[0]['abv'],
        'desc': beerjson[0]['description'],
        'foodpair': beerjson[0]['food_pairing'][0]
    }

    return render_template('index.html', beer=beer)
    
@app.route('/search')
def search_stations():
    src = request.args.get('src')
    dst = request.args.get('dst')
    start = request.args.get('start')
    end = request.args.get('end')
    date = request.args.get('date')

    # This begins the search
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    cmd = f'python3 search.py {src} {dst} {start} {end} {date}'
    print(cmd)

    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid) 

    #os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
    return 'success'

@app.route('/results')
def search_results():
    src = request.args.get('src')
    dst = request.args.get('dst')
    start = request.args.get('start')
    end = request.args.get('end')
    date = request.args.get('date')

    filename = f'{src}-{dst}-{start}-{end}-{date}.txt'

    if not os.path.isfile(filename):
        return jsonify('{"info":{"status":"not started"}}')

    faresFile = open(filename, 'r')
    data = faresFile.read()
    faresFile.close()

    #os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
    return jsonify(data)
