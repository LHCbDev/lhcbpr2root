import json
import ROOT
from service import app, jsonp
from flask import (request, jsonify)

@app.route('/root/text2dhist/')
@jsonp
def text2dhist():
	# 2D text histogram (table) for timings of particles
  values = request.args.get('values', None).split(';')
  xlabels = request.args.get('xlabels', None).split(';')
  ylabels = request.args.get('ylabels', None).split(';')

  plot_title = request.args.get('title', '')
  xaxis_label = request.args.get('xaxis', '')
  yaxis_label = request.args.get('yaxis', '')

  canvas = ROOT.TCanvas('c1', 'c1', 852, 360)
  canvas.SetHighLightColor(2)
  canvas.SetFillColor(0)
  canvas.SetBorderMode(0)
  canvas.SetBorderSize(0)
  canvas.SetFrameBorderMode(0)
  canvas.SetGrid()

  # Beautification
  ROOT.gStyle.SetPalette(64)

  # Estimate the number of y-bins
  histo_y_bins_num = 1;
  for i in range(len(ylabels)):
    tmp_ylabels = ylabels[i].split(',')
    if histo_y_bins_num < len(tmp_ylabels):
      histo_y_bins_num = len(tmp_ylabels)

  histogram = ROOT.TH2D('partimingh2d', '', len(values), 0, len(values), histo_y_bins_num, 0, histo_y_bins_num)

  # Loop over columns
  for i in range(len(values)):
    tmp_values = values[i].split(',')
    tmp_xlabels = xlabels[i].split(',')
    tmp_ylabels = ylabels[i].split(',')

    histogram.GetXaxis().SetBinLabel(i + 1, str(xlabels[i]).replace('"', ''))

    # Loop over rows
    for j in range(len(tmp_ylabels)):
      histogram.SetBinContent(histogram.GetBin(i + 1, j + 1), float(tmp_values[j]))
      histogram.GetYaxis().SetBinLabel(j + 1, str(tmp_ylabels[j]).replace('"', ''))

  # Histogram beautification
  histogram.SetStats(0)
  histogram.GetXaxis().SetLabelSize(0.05)
  histogram.GetYaxis().SetLabelSize(0.05)
  histogram.SetTitle(plot_title)

  histogram.GetXaxis().SetTitle(xaxis_label)
  histogram.GetYaxis().SetTitle(yaxis_label)

  histogram.Draw('text')
  canvas.Update()

  result = {'result': json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))}

  return jsonify(result)
