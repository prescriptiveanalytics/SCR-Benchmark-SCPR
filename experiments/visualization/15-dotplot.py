
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import seaborn as sns
import pandas as pd
import numpy as np
import random as rng
from SCRBenchmark import FEYNMAN_SRSD_HARD


EQUATIONS_COUNT = len(FEYNMAN_SRSD_HARD)
REPETITIONS  = 10

font = {'size'   : 9}

mpl.rc('font', **font)

results = pd.read_csv('./experiments/results/violations_best.csv')

print(np.unique(results['EquationName']))
print(len(np.unique(results['EquationName'])))

results['ConstraintsCount'].fillna(1, inplace=True)
results['ConstraintsDerivative1Count'].fillna(1, inplace=True)
results['ConstraintsDerivative2Count'].fillna(1, inplace=True)
results['ConstraintsViolated'].fillna(1, inplace=True)
results['ConstraintsViolatedDerivative1Count'].fillna(1, inplace=True)
results['ConstraintsViolatedDerivative2Count'].fillna(1, inplace=True)
results['R2_Test'].fillna(-10, inplace=True)

results['ConstraintsAchievedScaled'] = (1-(results['ConstraintsViolated']/results['ConstraintsCount']) ) * 100
results['ConstraintsAchievedDerivative1Scaled'] = (1-(results['ConstraintsViolatedDerivative1Count']/results['ConstraintsDerivative1Count'])) * 100
results['ConstraintsAchievedDerivative2Scaled'] = (1-(results['ConstraintsViolatedDerivative2Count']/results['ConstraintsDerivative2Count'])) * 100

results['ConstraintsAchievedScaled'].fillna(100, inplace=True)
results['ConstraintsAchievedDerivative1Scaled'].fillna(100, inplace=True)
results['ConstraintsAchievedDerivative2Scaled'].fillna(100, inplace=True)

results['SampleSize'] = [ float(filename.split('sample_size')[1].split('_')[0]) for filename in results['DataSourceFile']]
results['NoiseLevel'] = [ float(filename.split('noise_level')[1].split('_')[0]) for filename in results['DataSourceFile']]
results['CountHelper'] = [1] * len(results)
results['EquationName'] = results['EquationName'].astype("category")
results['EquationName'] = results['EquationName'].cat.set_categories(FEYNMAN_SRSD_HARD)

results = results[results['Successful'] == True]

print(results[['ConstraintsCount','ConstraintsViolated','ConstraintsAchievedScaled']])
results = results[['EquationName','Configuration','SampleSize','NoiseLevel', 'R2_Test',"ConstraintsAchievedScaled","ConstraintsAchievedDerivative1Scaled","ConstraintsAchievedDerivative2Scaled" ]]
results = results.groupby(
    ['EquationName','Configuration','SampleSize','NoiseLevel' ]).mean().reset_index()
results.index = pd.RangeIndex(len(results.index))

results = results.sort_values("EquationName", ascending=False)

# df = results[ results['SampleSize'] == 100 ]

for sampleSize in [100,1000]:
  df = results[ results['SampleSize'] == sampleSize ]

  g = sns.PairGrid(df,
                  x_vars=['R2_Test',"ConstraintsAchievedScaled","ConstraintsAchievedDerivative1Scaled","ConstraintsAchievedDerivative2Scaled"], y_vars=["EquationName"],
                  height=8, aspect=.25, hue = 'NoiseLevel')
  plt.subplots_adjust(left=0.17, bottom=0.09, right=0.90, top=0.97, wspace=0.16, hspace=0.1)

  # Draw a dot plot using the stripplot function
  g.map(sns.stripplot, size=7, orient="h", jitter=True,
        palette="flare_r", linewidth=1, edgecolor=None, marker = 'X')
  g.add_legend()

  for ax in g.axes.flat:

      ax.xaxis.grid(False)
      ax.yaxis.grid(True)
      label = ax.get_xlabel()
      if(label == "R2_test"):
        ax.set( xlabel="mean $R^2$ validation", ylabel="")
      if(label == "ConstraintsAchievedScaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\ntotal", ylabel="")
      if(label == "ConstraintsAchievedDerivative1Scaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\ndegree 1", ylabel="")
      if(label == "ConstraintsAchievedDerivative2Scaled"):
        ax.set(xlim=(-10,110), xlabel="mean %\nachieved constraints\ndegree 2", ylabel="")


  sns.despine(left=True, bottom=True)

  plt.savefig(f'./results/dotplot_SampleSize{sampleSize}.pdf',dpi = 500)
  plt.savefig(f'./results/dotplot_SampleSize{sampleSize}.png',dpi = 500)
  plt.show()
  plt.clf()
  plt.close()