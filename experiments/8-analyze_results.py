from SCRBenchmark import Benchmark
from SCRBenchmark.SRSDFeynman import FeynmanICh6Eq20a
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np

summary_best = pd.read_csv('./experiments/repeated_best_config_results/summary_best.csv')
summary_best['Configuration'] = ['best parameters'] * len(summary_best)
print(f"average runtime [best configuration] {np.mean(summary_best[ summary_best['Successful'] == True]['Runtime'])}" )

summary_degree2= pd.read_csv('./experiments/repeated_best_config_results/summary_degree2.csv')
summary_degree2['Configuration'] = ['degree 2'] * len(summary_degree2)
print(f"average runtime [degree 2] {np.mean(summary_degree2[ summary_degree2['Successful'] == True]['Runtime'])}" )


summary_degree3 = pd.read_csv('./experiments/repeated_best_config_results/summary_degree3.csv')
summary_degree3['Configuration'] = ['degree 3'] * len(summary_degree3)
print(f"average runtime [degree 3] {np.mean(summary_degree3[ summary_degree3['Successful'] == True]['Runtime'])}" )


summary = pd.concat([summary_best,summary_degree2, summary_degree3])
summary['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in summary['DataSourceFile']]
summary['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in summary['DataSourceFile']]

mean_per_repetition = summary[['EquationName','Configuration','SampleSize','NoiseLevel','R2_Training','R2_Test' ]]
print( mean_per_repetition.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).count().reset_index())
mean_per_repetition = mean_per_repetition.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).mean().reset_index()
print(mean_per_repetition)




sns.set_theme(style="ticks", palette="husl")


print("data for")
print(np.unique(mean_per_repetition['EquationName']))
print(np.unique(mean_per_repetition['SampleSize']))
print(np.unique(mean_per_repetition['NoiseLevel']))



def plotFigure(yAxis, yAxisLabel, plot = 'boxplot'):
  f, ax = plt.subplots(2,5, figsize=(10, 4), sharex=True, sharey=True)
  plt.subplots_adjust(left=0.11, bottom=0.1, right=0.98, top=0.90, wspace=0.1, hspace=0.1)

  row = 0
  max_row_idx = len(np.unique(mean_per_repetition['SampleSize']))-1

  for sampleSize in np.unique(mean_per_repetition['SampleSize']):
    col = 0
    for noiseLevel in np.unique(mean_per_repetition['NoiseLevel']):
      df = mean_per_repetition[ ((mean_per_repetition['SampleSize'] == sampleSize) |
                        (mean_per_repetition['NoiseLevel'] == noiseLevel)) ]
      
      if(plot == 'boxplot'):
        bx = sns.boxplot(y=yAxis,
                  x = "Configuration",
                  hue = "Configuration",
                  data=df,
                  ax = ax[row,col] )
      elif(plot == "pointplot"):
        bx = sns.pointplot(y=yAxis,
                        x = "Configuration",
                        hue = "Configuration",
                        errorbar = ('pi',100),
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
  lines = lines[:4]
  labels = labels[:4]
  for ax in f.axes:
    ax.get_legend().remove()

  f.legend(lines,labels,
              loc='upper center', ncol=3)
  plt.savefig(f'./results/summary_{plot}_{yAxis}.pdf',dpi = 500)
  plt.savefig(f'./results/summary_{plot}_{yAxis}.png',dpi = 500)
  # plt.show()
  plt.clf()
  plt.close()

plotFigure("R2_Training", "R2 training",'boxplot')
plotFigure("R2_Test", "R2 validation",'boxplot')
plotFigure("R2_Training", "R2 training",'pointplot')
plotFigure("R2_Test", "R2 validation",'pointplot')