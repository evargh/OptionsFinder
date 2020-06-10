#!/usr/bin/env python

import json
import os
from datetime import datetime

import pandas
import plotly as pl
import plotly.graph_objects as go
from flask import Flask, render_template, flash, request
from flask_uploads import UploadSet, configure_uploads, DATA

app = Flask(__name__)

ceeesvees = UploadSet(name='csvs', extensions=DATA)
app.config['UPLOADS_DEFAULT_DEST'] = 'static/csv'
app.config['UPLOADED_DATA_DEST'] = 'static/csv'
app.config['SECRET_KEY'] = 'very secret'

configure_uploads(app, ceeesvees)

graphcount = 2

plot1 = ""
plot2 = ""

def take_numeric(df):
    df["Open"] = df["Open"].astype("str")
    df["Open"] = df["Open"].str.replace(',', '').replace('--', '0')
    df["Open"] = pandas.to_numeric(df["Open"])

    df["Last"] = df["Last"].astype("str")
    df["Last"] = df["Last"].str.replace(',', '').replace('--', '0')
    df["Last"] = pandas.to_numeric(df["Last"])

    df["Chg"] = df["Chg"].astype("str")
    df["Chg"] = df["Chg"].str.replace(',', '').replace('--', '0')
    df["Chg"] = pandas.to_numeric(df["Chg"])

    df["Chg%"] = df["Chg%"].astype("str")
    df["Chg%"] = df["Chg%"].str.rstrip(to_strip='%')
    df["Chg%"] = df["Chg%"].str.replace(',', '').replace('%%', '').replace('--', '0')
    df["Chg%"] = pandas.to_numeric(df["Chg%"])

    df["IV Idx"] = df["IV Idx"].astype("str")
    df["IV Idx"] = df["IV Idx"].str.rstrip(to_strip='%')
    df["IV Idx"] = df["IV Idx"].str.replace(',', '').replace('%%', '').replace('--', '0')
    df["IV Idx"] = pandas.to_numeric(df["IV Idx"])


def readCSV(filename, datesent):
    todaysfile = pandas.read_csv(filepath_or_buffer='static/csv/csvs/'+filename,
                                 usecols=[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                                 sep=',', thousands=',')
    take_numeric(todaysfile)

    datecol = []
    for x in range(len(todaysfile.index)):
        datecol.append(pandas.to_datetime(datesent))
    todaysfile['Date'] = datecol
    todaysfile.set_index(keys=['Date', 'Symbol'], append=False, inplace=True)
    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        fulllodge = pandas.read_csv(filepath_or_buffer='static/permanent/fulldir.csv', index_col=[0, 1],
                                    sep=',', thousands=',')
        take_numeric(fulllodge)
        todaysfile = pandas.concat([todaysfile, fulllodge])
    open('static/permanent/fulldir.csv', 'w').close()
    todaysfile.to_csv(path_or_buf='static/permanent/fulldir.csv')

    os.remove('static/csv/csvs/'+filename)


def loadbig():
    bigset = pandas.read_csv(filepath_or_buffer='static/permanent/fulldir.csv', index_col=[0, 1],
                             sep=',', thousands=',')
    take_numeric(bigset)
    printer = bigset.reset_index()
    goodparm = bigset.columns.tolist()
    del goodparm[0]
    allsymb = list(dict.fromkeys(printer['Symbol'].astype("str").tolist()))
    return [goodparm, allsymb, bigset]


def getplot(df, parm, names):
    data = []
    freshsets = []
    for i in range(len(names)):
        freshsets.append(df.reset_index())

        if names[i] in (df.reset_index())['Symbol'].tolist():
            freshsets[i] = freshsets[i].loc[freshsets[i].Symbol[freshsets[i].Symbol == names[i]].index.tolist()]
            data.append(go.Scatter(x=freshsets[i]['Date'],
                                   y=freshsets[i][parm],
                                   mode='lines+markers',
                                   name=names[i]))

    layout = dict(title=parm + ' vs Time', xaxis_title="Time", yaxis_title=parm, showlegend=True)
    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=pl.utils.PlotlyJSONEncoder)


@app.route('/', methods=['GET', 'POST'])
def loadsite():
    if request.method == 'POST' and 'csvtype' in request.files:
        filename = ceeesvees.save(request.files['csvtype'])
        dateSource = datetime.now().date()
        readCSV(filename, dateSource)
        flash('File Uploaded!')
    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        importantset = loadbig()
        return render_template('index.html', params=importantset[0], symbols=importantset[1], index=graphcount)

    return render_template('index.html')


@app.route('/swapgraph', methods=['POST'])
def swapgraph():
    names = []
    jsons = []

    names = json.loads(request.form['items'])
    print(names)
    del names[0]

    parameter = request.form['parma']
    appender = request.form['graph']

    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        importantset = loadbig()
        global plot1
        global plot2
        if appender == "1":
            print("appender is 1")
            jsons.append(getplot(importantset[2], parameter, names))
            plot1 = jsons[0]
            return plot1

        if appender == "2":
            print("appender is 2")
            jsons.append(getplot(importantset[2], parameter, names))
            plot2 = jsons[0]
            return plot2

    return render_template('index.html', params=importantset[0], symbols=importantset[1], index=graphcount,
                           plot1=plot1, plot2=plot2)


@app.route('/test', methods=['GET', 'POST'])
def test():
    names = []
    jsons = []

    names = str(request.form.get('showVals')).split("\r\n ")
    del names[0]

    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        importantset = loadbig()
        for i in range(graphcount):
            jsons.append(getplot(importantset[2], "Open", names))
        global plot1, plot2
        plot1 = jsons[0]
        plot2 = jsons[1]

        importantset[1].sort()

        symbollength = len(importantset[1])

        return render_template('index.html', params=importantset[0], symbols=importantset[1], appsymbollength=int(symbollength/15)+1, symbolindex=graphcount,
                               plot1=plot1, plot2=plot2)

    return names + " " + jsons


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)
