
import pandas as pd
import numpy as np
from SCRBenchmark import FEYNMAN_SRSD_HARD,HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES

instances = ['FeynmanBonus1'
,'FeynmanBonus2'
,'FeynmanBonus3'
,'FeynmanBonus4'
,'FeynmanBonus5'
,'FeynmanBonus6'
,'FeynmanBonus7'
,'FeynmanBonus9'
,'FeynmanBonus10'
,'FeynmanBonus11'
,'FeynmanBonus12'
,'FeynmanBonus13'
,'FeynmanBonus14'
,'FeynmanBonus15'
,'FeynmanBonus16'
,'FeynmanBonus17'
,'FeynmanBonus19'
,'FeynmanBonus20']



def reportSuccessfulRuns(summary, fileName, formatters = None,float_format = None):
  summary['Configuration'] = ['best parameters'] * len(summary)
  print(f"average runtime [best configuration] {np.mean(summary[ summary['Successful'] == True]['Runtime'])}" )

  print(len(summary))
  summary = summary[summary['Successful'] == True]
  print(len(summary))

  summary['SampleSize'] = [ int(filename.split('sample_size')[1].split('_')[0]) for filename in summary['DataSourceFile']]
  summary['NoiseLevel'] = [ float(filename.split('noise_level')[1].split('_')[0]) for filename in summary['DataSourceFile']]
  summary['Repetition'] = [ int(filename.split('repetition')[1].split('.')[0]) for filename in summary['DataSourceFile']]
  summary['Helper'] = [1] * len(summary)

  import itertools
  combined = [instances, HARD_NOISE_LEVELS, HARD_SAMPLE_SIZES, range(0,10) ]
  allCombinations = pd.DataFrame(columns = ['EquationName', 'NoiseLevel', 'SampleSize','Repetition'], data=list(itertools.product(*combined)))



  df = allCombinations.merge(summary, how='left').fillna(0)
  df = df[['EquationName','SampleSize','NoiseLevel','Helper']]
  df['NoiseLevel'] = [ "{:.2f}".format(level) for level in df['NoiseLevel']]
  sum = df.groupby(['EquationName','SampleSize','NoiseLevel']).sum().reset_index()
  pivot = sum.pivot(index='EquationName', columns=['SampleSize','NoiseLevel'], values='Helper')
  pivot.to_csv(f'./results/{fileName}.csv')
  pivot.to_latex(f'./results/{fileName}.tex', formatters = formatters, float_format = float_format)

def reportR2ValidationMean(summary, fileName, formatters = None,float_format = None):
  summary['Configuration'] = ['best parameters'] * len(summary)
  print(f"average runtime [best configuration] {np.mean(summary[ summary['Successful'] == True]['Runtime'])}" )

  print(len(summary))
  summary = summary[summary['Successful'] == True]
  print(len(summary))

  summary['SampleSize'] = [ int(filename.split('sample_size')[1].split('_')[0]) for filename in summary['DataSourceFile']]
  summary['NoiseLevel'] = [ float(filename.split('noise_level')[1].split('_')[0]) for filename in summary['DataSourceFile']]


  df = summary[['EquationName','SampleSize','NoiseLevel','R2_Test']]
  df['NoiseLevel'] = [ "{:.2f}".format(level) for level in df['NoiseLevel']]
  sum = df.groupby(['EquationName','SampleSize','NoiseLevel']).mean().reset_index()
  pivot = sum.pivot(index='EquationName', columns=['SampleSize','NoiseLevel'], values='R2_Test')
  pivot.to_csv(f'./results/{fileName}.csv')
  pivot.to_latex(f'./results/{fileName}.tex', formatters = formatters, float_format = float_format)

summary = pd.read_csv('./experiments/results/summary_best.csv')
reportSuccessfulRuns(summary,'sucessful_runs_best_configuration', float_format="{:.0f}".format)
reportR2ValidationMean(summary,'mean_r2_best_configuration', float_format="{:.5f}".format)

summary = pd.read_csv('./experiments/results/summary_degree2.csv')
reportSuccessfulRuns(summary,'sucessful_runs_degree2_configuration', float_format="{:.0f}".format)
reportR2ValidationMean(summary,'mean_r2_degree2_configuration', float_format="{:.5f}".format)

summary = pd.read_csv('./experiments/results/summary_degree3.csv')
reportSuccessfulRuns(summary,'sucessful_runs_degree3_configuration', float_format="{:.0f}".format)
reportR2ValidationMean(summary,'mean_r2_degree3_configuration', float_format="{:.5f}".format)