from SCRBenchmark import Benchmark
from SCRBenchmark.SRSDFeynman import FeynmanICh6Eq20a
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np

summary_best = pd.read_csv('./experiments/repeated_best_config_results/summary_best.csv')
summary_best['Configuration'] = ['best configuration'] * len(summary_best)

summary_degree2= pd.read_csv('./experiments/repeated_best_config_results/summary_degree2.csv')
summary_degree2['Configuration'] = ['degree 2'] * len(summary_degree2)

summary_degree3 = pd.read_csv('./experiments/repeated_best_config_results/summary_degree3.csv')
summary_degree3['Configuration'] = ['degree 3'] * len(summary_degree3)

summary = pd.concat([summary_best,summary_degree2, summary_degree3])
summary['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in summary['DataSourceFile']]
summary['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in summary['DataSourceFile']]

median_per_repetition = summary[['EquationName','Configuration','SampleSize','NoiseLevel','R2_Training','R2_Test' ]]
print( median_per_repetition.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).count().reset_index())
median_per_repetition = median_per_repetition.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).median().reset_index()
print(median_per_repetition)




sns.set_theme(style="ticks", palette="husl")


print("data for")
print(np.unique(median_per_repetition['EquationName']))
print(np.unique(median_per_repetition['SampleSize']))
print(np.unique(median_per_repetition['NoiseLevel']))


def plotFigure(yAxis, yAxisLabel):
  f, ax = plt.subplots(2,5, figsize=(10, 4), sharex=True, sharey=True)
  plt.subplots_adjust(left=0.11, bottom=0.1, right=0.98, top=0.90, wspace=0.1, hspace=0.1)

  row = 0
  max_row_idx = len(np.unique(median_per_repetition['SampleSize']))-1

  for sampleSize in np.unique(median_per_repetition['SampleSize']):
    col = 0
    for noiseLevel in np.unique(median_per_repetition['NoiseLevel']):
      df = median_per_repetition[ ((median_per_repetition['SampleSize'] == sampleSize) |
                        (median_per_repetition['NoiseLevel'] == noiseLevel)) ]
      bx = sns.boxplot(y=yAxis,
                      x = "Configuration",
                      hue = "Configuration",
            data=df,
            ax = ax[row,col] )
      
      bx.set(xticklabels=[])

      # ax[row,col].set_yscale("log")

      if(row == max_row_idx):
        ax[row,col].set_xlabel(f'noise level = {noiseLevel}')
      else:
        ax[row,col].set_xlabel(f'')
      if(col == 0):
        ax[row,col].set_ylabel(f'sample_size = {sampleSize}\n{yAxisLabel}')
      else:
        ax[row,col].set_ylabel(f'')

      col = col+1

    row = row+1

  lines_labels = [ax.get_legend_handles_labels() for ax in f.axes]
  lines, labels = [sum(total, []) for total in zip(*lines_labels)]
  lines = lines[:3]
  labels = labels[:3]
  for ax in f.axes:
    ax.get_legend().remove()

  f.legend(lines,labels,
              loc='upper center', ncol=3)
  plt.savefig(f'./experiments/summary_{yAxis}.png',dpi = 500)
  plt.show()
  plt.clf()
  plt.close()

plotFigure("R2_Training", "R2 training")
plotFigure("R2_Test", "R2 validation")