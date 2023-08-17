from SCRBenchmark import Benchmark
from SCRBenchmark.SRSDFeynman import FeynmanICh6Eq20a
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np

summary_best = pd.read_csv('./experiments/results/summary_best.csv')
# the column 'Configuration' distinguishes the different algorithm runs
# this serves as an analog to future comparison with other algorithms
summary_best['Configuration'] = ['best parameters'] * len(summary_best)
print(f"average runtime [best configuration] {np.mean(summary_best[ summary_best['Successful'] == True]['Runtime'])}" )

summary_degree2= pd.read_csv('./experiments/results/summary_degree2.csv')
summary_degree2['Configuration'] = ['degree 2'] * len(summary_degree2)
print(f"average runtime [degree 2] {np.mean(summary_degree2[ summary_degree2['Successful'] == True]['Runtime'])}" )

summary_degree3 = pd.read_csv('./experiments/results/summary_degree3.csv')
summary_degree3['Configuration'] = ['degree 3'] * len(summary_degree3)
print(f"average runtime [degree 3] {np.mean(summary_degree3[ summary_degree3['Successful'] == True]['Runtime'])}" )

summary = pd.concat([summary_best,summary_degree2, summary_degree3])
summary['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in summary['DataSourceFile']]
summary['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in summary['DataSourceFile']]

mean_over_repetitions = summary[['EquationName','Configuration','SampleSize','NoiseLevel','R2_Training','R2_Test' ]]
print( mean_over_repetitions.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).count().reset_index())
mean_over_repetitions = mean_over_repetitions.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).mean().reset_index()
mean_over_repetitions = mean_over_repetitions.fillna(float('-inf'))
print('Mean per Repetition')
print(mean_over_repetitions)



sns.set_theme(style="ticks", palette="husl")
def plotFigure(data, measure, yAxisLabel, plot = 'boxplot'):
  data = data.sort_values(['EquationName','SampleSize','NoiseLevel', measure], ascending = False)
  # old calculation of rank below does not account for several entries having the same value. i.e. a better rank should be achieved
  # data['Rank'] = data.groupby(['EquationName','SampleSize','NoiseLevel']).transform('cumcount') + 1
  data['Rank'] = [float('inf')]*len(data)

  rank = 1
  skip = 0
  old_equation = ''
  old_sampleSize = ''
  old_noiseLevel = ''
  old_measureValue = ''
  for id, row in data.iterrows():
    if( (old_equation != row['EquationName']) |
        (old_sampleSize != row['SampleSize']) |
        (old_noiseLevel != row['NoiseLevel']) ):
      old_measureValue = row[measure]
      rank = 1
      skip = 0
    else:
      if(old_measureValue > row[measure]):
        rank = rank + 1 + skip
        skip = 0
      else:
        skip = skip + 1 

    old_measureValue = row[measure]
    data.loc[id, 'Rank'] = rank
    
    old_equation = row['EquationName']
    old_sampleSize = row['SampleSize']
    old_noiseLevel = row['NoiseLevel']

  print("Ranks!!")
  print(np.min(data['Rank']))
  print(np.max(data['Rank']))
  rank_per_group = data[['EquationName','Configuration','SampleSize','NoiseLevel','Rank']]
  mean_rank_per_group = rank_per_group.groupby(['EquationName','Configuration','SampleSize','NoiseLevel' ]).mean().reset_index()


  f, ax = plt.subplots(2,5, figsize=(10, 4), sharex=True, sharey=True)
  plt.subplots_adjust(left=0.11, bottom=0.1, right=0.98, top=0.90, wspace=0.1, hspace=0.1)

  row = 0
  max_row_idx = len(np.unique(mean_rank_per_group['SampleSize']))-1

  for sampleSize in np.unique(mean_rank_per_group['SampleSize']):
    col = 0
    for noiseLevel in np.unique(mean_rank_per_group['NoiseLevel']):
      df = mean_rank_per_group[ ((mean_rank_per_group['SampleSize'] == sampleSize) &
                        (mean_rank_per_group['NoiseLevel'] == noiseLevel)) ]
      
      if(plot == 'boxplot'):
        bx = sns.boxplot(y='Rank',
                  x = "Configuration",
                  hue = "Configuration",
                  data=df,
                  ax = ax[row,col] )
      elif(plot == "pointplot"):
        bx = sns.pointplot(y='Rank',
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
  lines = lines[:3]
  labels = labels[:3]
  for ax in f.axes:
    ax.get_legend().remove()

  plt.gca().invert_yaxis()
  f.legend(lines,labels,
              loc='upper center', ncol=3)
  plt.savefig(f'./results/summary_{plot}_ranking_{measure}.pdf',dpi = 500)
  plt.savefig(f'./results/summary_{plot}_ranking_{measure}.png',dpi = 500)
  # plt.show()
  plt.clf()
  plt.close()

plotFigure(mean_over_repetitions,"R2_Training", "R2 training",'pointplot')
plotFigure(mean_over_repetitions,"R2_Test", "R2 validation",'pointplot')

