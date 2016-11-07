import ROOT
from service import app, jsonp, utils
from flask import (request, jsonify)
from array import array
import json
# import q

@app.route('/root/profile/')
@jsonp
def profile():
  points = json.loads(request.args.get("points", ""))

  titles = request.args.get("titles", None)
  titles = titles.split(";") if titles else [""] * len(points)

  xaxis_title = request.args.get("xaxis", "")
  yaxis_title = request.args.get("yaxis", "")

  canvas = ROOT.TCanvas("c1", "c1", 200, 10, 700, 500);

  profile = ROOT.TH1D("p1","p1",len(points), 0, len(points) + 1)

  for i in range(len(points)):
    bin_name = points[i][0]
    bin_value = points[i][1]
    bin_error = points[i][2]
    # q(i, bin_name, bin_value, bin_error)
    profile.SetBinContent(i + 1, bin_value)
    profile.SetBinError(i + 1, bin_error)
    profile.GetXaxis().SetBinLabel(i + 1, bin_name)
    profile.SetTitle(titles[i])
    # profile.SetLineColor(color);
    # profile.SetMarkerColor(color);
    profile.SetMarkerStyle(21)
    profile.SetMarkerSize(1.3)
    profile.SetFillColor(0)

  profile.GetXaxis().LabelsOption("v")
  profile.Draw("AP")

#   profile.GetXaxis().CenterLabels(True)
  profile.GetXaxis().SetTitle(xaxis_title)
  profile.GetYaxis().SetTitle(yaxis_title)

  results = {
    "result": json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))
  }

  return jsonify(results)
