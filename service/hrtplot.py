import json
import ROOT
from service import app, jsonp
from flask import (request, jsonify)

@app.route('/root/hrtplot/')
@jsonp
def hrtplot():
	# 1D overlayed histogram-ratio-trend plotting for detailed timing
  values = request.args.get('values', None).split(';')
  labels = request.args.get('labels', None).split(',')
  jobs_names = request.args.get('jobnames', '').split(',')

  plot_title = request.args.get('title', '')
  xaxis_label = request.args.get('xaxis', '')
  yaxis_label = request.args.get('yaxis', '')

  plot_ratio = request.args.get('ratio', None)
  plot_trend = request.args.get('trend', None)

  canvas = ROOT.TCanvas('c1', 'c1', 852, 480)
  canvas.SetHighLightColor(2)
  canvas.SetFillColor(0)
  canvas.SetBorderMode(0)
  canvas.SetBorderSize(0)
  canvas.SetFrameBorderMode(0)
  canvas.SetGrid()

  # Beautification
  ROOT.gStyle.SetPalette(57)

  # The maximum values to adjust overlay
  max_value = 0.
  ratios_max_value = 0.

  # Container of histograms and ratios
  histograms = []
  ratios = []

  # Trend histogram
  trend_histogram = None
  if plot_trend and len(values) > 1:
    trend_histogram = ROOT.TH1D('hTrend', '', len(values), 0, len(values))
    trend_histogram.SetStats(0)
    trend_histogram.GetXaxis().SetLabelSize(0.1)
    trend_histogram.GetYaxis().SetLabelSize(0.1)
    trend_histogram.SetMarkerSize(1.0)
    trend_histogram.SetMarkerStyle(0)
    trend_histogram.SetMarkerColor(1)

  legend = ROOT.TLegend(0.1, 0.86 - (0.036 * len(values)), 0.4, 0.9)

  # Loop over lists of values, create/configure/plot histograms for each
  for i in range(len(values)):
    tmp_values = values[i].split(',')
    histograms.append(ROOT.TH1D(str(jobs_names[i]),
                                str(jobs_names[i]),
                                len(tmp_values), 0, len(tmp_values)))

    histograms[i].SetTitle(plot_title)
    histograms[i].GetXaxis().SetTitle(xaxis_label)
    histograms[i].GetYaxis().SetTitle(yaxis_label)

    for j in range(len(tmp_values)):
      histograms[i].SetBinContent(j + 1, float(tmp_values[j]))
      histograms[i].GetXaxis().SetBinLabel(j + 1, str(labels[j]).replace('"', ''))
      if float(tmp_values[j]) > max_value:
        max_value = float(tmp_values[j])

    # If more than one histogram, prepair ratios
    if plot_ratio and i > 0:
      ratios.append(ROOT.TH1D('h' + str(i), '', len(tmp_values), 0, len(tmp_values)))

      # For multiple histograms, ratios are calculated in respect to the first job in the list
      for j in range(len(tmp_values)):
        if histograms[0].GetBinContent(j + 1) == 0:
          new_value = 0.
        else:
          new_value = histograms[i].GetBinContent(j + 1) / histograms[0].GetBinContent(j + 1)

        ratios[i - 1].SetBinContent(j + 1, new_value)
        ratios[i - 1].GetXaxis().SetBinLabel(j + 1, str(labels[j]).replace('"', ''))

        if new_value > ratios_max_value:
          ratios_max_value = new_value

      ratios[i - 1].SetStats(0)
      ratios[i - 1].GetXaxis().SetLabelSize(0)
      ratios[i - 1].GetYaxis().SetLabelSize(0.15)
      ratios[i - 1].SetMarkerSize(1.)
      ratios[i - 1].SetMarkerStyle(i + 2)
      ratios[i - 1].SetMarkerColor(i + 1)
      ratios[i - 1].SetLineColor(i + 1)
      ratios[i - 1].SetLineWidth(2)

      # Set the maximum value for the first drawn ratios histogram
      ratios[0].SetMaximum(ratios_max_value + (ratios_max_value/20.))
      ratios[i - 1].SetMinimum(0.)

    if plot_trend:
      trend_histogram.SetBinContent(i + 1, float(tmp_values[len(tmp_values) - 1]))
      trend_histogram.GetXaxis().SetBinLabel(i + 1, str(jobs_names[i]))

    histograms[i].SetStats(0)
    histograms[i].GetXaxis().SetLabelSize(0.03)
    histograms[i].GetYaxis().SetLabelSize(0.03)
    histograms[i].SetMarkerSize(1.5)
    histograms[i].SetMarkerStyle(i + 2)
    histograms[i].SetMarkerColor(i + 1)
    histograms[i].SetLineColor(i + 1)

    # Set the maximum value for the first drawn histogram
    histograms[0].SetMaximum(max_value + (max_value/20.))
    histograms[i].SetMinimum(-10.)

    legend.AddEntry(histograms[i], histograms[i].GetName(), 'p')

    if i == 0:
      histograms[i].Draw('ap')
    else:
      histograms[i].Draw('ap same')

  legend.Draw()
  canvas.Update()

  result = {'result': json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))}

  if plot_ratio:
    canvas.Clear()
    canvas.SetCanvasSize(852, 120)
    for hist in ratios:
      hist.Draw('same')
    canvas.Update()

    result['ratio'] = json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))

  if plot_trend:
    canvas.Clear()
    canvas.SetCanvasSize(852, 120)
    trend_histogram.SetMinimum(trend_histogram.GetMinimum() - trend_histogram.GetMinimum()/2.)
    trend_histogram.SetMaximum(trend_histogram.GetMaximum() + trend_histogram.GetMaximum()/5.)
    trend_histogram.Draw('ap')
    canvas.Update()

    result['trend'] = json.loads(str(ROOT.TBufferJSON.ConvertToJSON(canvas)))

  return jsonify(result)
