import ROOT
from service import app, jsonp, utils
from flask import (request, jsonify)
from array import array
from fractions import Fraction
import json
import q


@app.route('/root/multigraph/')
@jsonp
def multigraph():
    # -------------------------------------------------------------------------
    points = request.args.get("points", "").split(';')
    points = map(lambda serie: json.loads(serie), points)
    show_rate = request.args.get("rate", None)

    # ys = utils.fserie(request.args.get("y", None))

    # ex = utils.fserie(request.args.get("ex", None))
    # ey = utils.fserie(request.args.get("ey", None))

    titles = request.args.get("titles", None)
    titles = titles.split(";") if titles else [""] * len(points)

    colors = request.args.get("colors", None)
    colors = titles.split(";") if colors else utils.colors

    xaxis_title = request.args.get("xaxis", "")
    yaxis_title = request.args.get("yaxis", "")
    canvas = ROOT.TCanvas("c1","c1",200,10,700,500);
    mg = ROOT.TMultiGraph()
    leg = ROOT.TLegend(0.5,0.65,0.88,0.85);
    n = len(points)
    for i in range(n):
        ps = points[i]
        xs = []
        ys = []
        exs = []
        eys = []
        color = colors[i % len(colors)]
        q(color)
        for x, y, e in ps:
            xs.append(x)
            ys.append(y)
            exs.append(0)
            eys.append(e)

        g = ROOT.TGraphErrors(len(xs), array('f', xs), array('f', ys),
                              array('f', exs), array('f', eys))
        g.SetTitle(titles[i])
        g.SetLineColor(color);
        g.SetMarkerColor(color);
        g.SetMarkerStyle(21)
        g.SetMarkerSize(1.3)
        g.SetFillColor(0)
        # leg.AddEntry(g, titles[i], "le")
        # q(titles[i])
        mg.Add(g)

    mg.Draw("APC")
    leg = canvas.BuildLegend(0.5, 0.65,0.88, 0.85);
    mg.GetXaxis().SetTitle(xaxis_title)
    mg.GetYaxis().SetTitle(yaxis_title)
    leg.Draw()

    results = {
        "result": json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))
    }
    ratios = []
    if show_rate and len(points) > 1:
        for i in range(1, len(points)):
            canvas.Clear()
            xs = []
            ys = []

            for j, ref in enumerate(points[0]):
                x0, y0, e0 = ref
                x1, y1, e1 = points[i][i]
                xs.append(x0)
                frac = 0 if y0 == 0 else y1 / y0
                ys.append(round(frac,2))

            g = ROOT.TGraph(len(xs), array('f', xs), array('f', ys))
            g.SetTitle("Ratio %s / %s" % (titles[i], titles[0]))
            g.Draw()
            g.GetXaxis().SetTitle(xaxis_title)
            g.GetYaxis().SetTitle("Ratio")
            ratios.append(json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas))))
    results["ratios"] = ratios




    return jsonify(results)
