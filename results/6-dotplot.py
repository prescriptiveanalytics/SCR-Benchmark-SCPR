
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import seaborn as sns
import pandas as pd
import numpy as np
import random as rng
from SCRBenchmark import FEYNMAN_SRSD_HARD


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

EQUATIONS_COUNT = len(FEYNMAN_SRSD_HARD)
REPETITIONS  = 5

font = {'size'   : 9}

mpl.rc('font', **font)

results_scpr = pd.read_csv('./results/4-R2Score-and-Violations.csv')

print(np.unique(results_scpr['EquationName']))
print(len(np.unique(results_scpr['EquationName'])))
results_scpr['ConstraintsDerivative0Count'] = results_scpr['ConstraintsCount'] - (results_scpr['ConstraintsDerivative1Count'] + results_scpr['ConstraintsDerivative2Count'])
results_scpr['ConstraintsViolatedDerivative0Count'] = results_scpr['ConstraintsViolated'] - (results_scpr['ConstraintsViolatedDerivative1Count'] + results_scpr['ConstraintsViolatedDerivative2Count'])

results_scpr['ConstraintsCount'].fillna(1, inplace=True)
results_scpr['ConstraintsDerivative0Count'].fillna(1, inplace=True)
results_scpr['ConstraintsDerivative1Count'].fillna(1, inplace=True)
results_scpr['ConstraintsDerivative2Count'].fillna(1, inplace=True)
results_scpr['ConstraintsViolated'].fillna(1, inplace=True)
results_scpr['ConstraintsViolatedDerivative0Count'].fillna(1, inplace=True)
results_scpr['ConstraintsViolatedDerivative1Count'].fillna(1, inplace=True)
results_scpr['ConstraintsViolatedDerivative2Count'].fillna(1, inplace=True)
results_scpr['R2_Test'].fillna(-10, inplace=True)

results_scpr['ConstraintsAchievedScaled'] = (1-(results_scpr['ConstraintsViolated']/results_scpr['ConstraintsCount']) ) * 100
results_scpr['ConstraintsAchievedDerivative0Scaled'] = (1-((results_scpr['ConstraintsViolated']-results_scpr['ConstraintsViolatedDerivative1Count']-results_scpr['ConstraintsViolatedDerivative2Count'])/results_scpr['ConstraintsCount'])) * 100
results_scpr['ConstraintsAchievedDerivative1Scaled'] = (1-(results_scpr['ConstraintsViolatedDerivative1Count']/results_scpr['ConstraintsDerivative1Count'])) * 100
results_scpr['ConstraintsAchievedDerivative2Scaled'] = (1-(results_scpr['ConstraintsViolatedDerivative2Count']/results_scpr['ConstraintsDerivative2Count'])) * 100

results_scpr['ConstraintsAchievedScaled'].fillna(0, inplace=True)
results_scpr['ConstraintsAchievedDerivative0Scaled'].fillna(0, inplace=True)
results_scpr['ConstraintsAchievedDerivative1Scaled'].fillna(0, inplace=True)
results_scpr['ConstraintsAchievedDerivative2Scaled'].fillna(0, inplace=True)

results_scpr['SampleSize'] = [ float(filename.split('sample_size')[1].split('_')[0]) for filename in results_scpr['DataSourceFile']]
results_scpr['NoiseLevel'] = [ float(filename.split('noise_level')[1].split('_')[0]) for filename in results_scpr['DataSourceFile']]
results_scpr['CountHelper'] = [1] * len(results_scpr)
results_scpr['EquationName'] = results_scpr['EquationName'].astype("category")
results_scpr['EquationName'] = results_scpr['EquationName'].cat.set_categories(FEYNMAN_SRSD_HARD)


results_scpr = results_scpr[results_scpr['Successful'] == True]

print(results_scpr[['ConstraintsCount','ConstraintsViolated','ConstraintsAchievedScaled']])
results_scpr = results_scpr[['EquationName','SampleSize','NoiseLevel', 'R2_Test',"ConstraintsAchievedScaled","ConstraintsAchievedDerivative0Scaled","ConstraintsAchievedDerivative1Scaled","ConstraintsAchievedDerivative2Scaled" ]]
results_scpr = results_scpr.groupby(
    ['EquationName','SampleSize','NoiseLevel' ]).median().reset_index()
results_scpr.index = pd.RangeIndex(len(results_scpr.index))

results_scpr = results_scpr.sort_values("EquationName", ascending=False)

# df = results[ results['SampleSize'] == 100 ]

for sampleSize in [1000,10000]:
  df = results_scpr[ results_scpr['SampleSize'] == sampleSize ]

  df = df.sort_values(['EquationName','SampleSize','NoiseLevel'])
  g = sns.PairGrid(df,
                  x_vars=['R2_Test',"ConstraintsAchievedScaled","ConstraintsAchievedDerivative0Scaled","ConstraintsAchievedDerivative1Scaled","ConstraintsAchievedDerivative2Scaled"], y_vars=["EquationName"],
                  height=8, aspect=.25, hue = 'NoiseLevel')
  plt.subplots_adjust(left=0.17, bottom=0.09, right=0.90, top=0.97, wspace=0.16, hspace=0.1)

  # Draw a dot plot using the stripplot function
  g.map(sns.stripplot, size=7, orient="h", jitter=False, hue = 'NoiseLevel', data = df, palette = 'tab10', marker = 'v', alpha = 0.5)
  g.add_legend()

  for ax in g.axes.flat:

      ax.xaxis.grid(False)
      ax.yaxis.grid(True)
      label = ax.get_xlabel()
      if(label == "R2_test"):
        ax.set( xlabel="mean $R^2$ validation", ylabel="")
      if(label == "ConstraintsAchievedScaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\ntotal", ylabel="")
      if(label == "ConstraintsAchievedDerivative0Scaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\nimage boundary", ylabel="")
      if(label == "ConstraintsAchievedDerivative1Scaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\nmonotonicity", ylabel="")
      if(label == "ConstraintsAchievedDerivative2Scaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\ncurvature", ylabel="")


  sns.despine(left=True, bottom=True)

  plt.savefig(f'./result-figures/scpr-dotplot_SampleSize{sampleSize}.pdf',dpi = 500)
  plt.savefig(f'./result-figures/scpr-dotplot_SampleSize{sampleSize}.png',dpi = 500)
  plt.clf()
  plt.close()