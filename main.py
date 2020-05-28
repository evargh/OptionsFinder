#!/usr/bin/env python

import os
import pandas
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, DATA

app = Flask(__name__)

ceeesvees = UploadSet(name='csvs', extensions=DATA)
app.config['UPLOADS_DEFAULT_DEST'] = 'static/csv'
app.config['UPLOADED_DATA_DEST'] = 'static/csv'
app.config['SECRET_KEY'] = 'very secret'

configure_uploads(app, ceeesvees)

graphcount = 2

figa = plt.gcf()
figa.set_size_inches(12,8)
sns.set_style("whitegrid")

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
    allsymb = printer['Symbol'].tolist()
    allsymb.insert(0, 'None')
    return [goodparm, allsymb, bigset]


def getplot(df, parm, red, green, blue, number):
    valids = []
    coolset = df.reset_index()
    if red in (df.reset_index())['Symbol'].tolist():
        valids.extend(coolset.Symbol[coolset.Symbol == red].index.tolist())
    if green in (df.reset_index())['Symbol'].tolist():
        valids.extend(coolset.Symbol[coolset.Symbol == green].index.tolist())
    if blue in (df.reset_index())['Symbol'].tolist():
        valids.extend(coolset.Symbol[coolset.Symbol == blue].index.tolist())
    partplot = sns.relplot(x='Date', y=parm, hue='Symbol', kind='line', markers=True, data=coolset.loc[valids])
    figure = partplot.fig
    figure.savefig('static/permanent/figure' + str(number) + '.png')


@app.route('/', methods=['GET', 'POST'])
def loadsite():
    if request.method == 'POST' and 'csvtype' in request.files:
        filename = ceeesvees.save(request.files['csvtype'])
        dateSource = datetime.now().date()
        readCSV(filename, dateSource)
        flash('File Uploaded!')
        for i in range(graphcount):
            open('static/permanent/figure' + str(i) + '.png', 'w').close()
    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        importantset = loadbig()
        return render_template('index.html', params=importantset[0], symbols=importantset[1], index=graphcount)

    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    paramer = []
    redder = []
    greener = []
    bluer = []
    for i in range(graphcount):
        appender = str(i)
        paramer.append(str(request.form.get('params'+appender)))
        redder.append(str(request.form.get('reds'+appender)))
        greener.append(str(request.form.get('greens'+appender)))
        bluer.append(str(request.form.get('blues'+appender)))
    if os.stat('static/permanent/fulldir.csv').st_size != 0:
        importantset = loadbig()
        for i in range(graphcount):
            if not (redder[i] == greener[i] == bluer[i] == 'None'):
                getplot(importantset[2], paramer[i], redder[i], greener[i], bluer[i], i)
        return render_template('index.html', params=importantset[0], symbols=importantset[1], index=graphcount)
    return paramer + redder + greener + bluer


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)
