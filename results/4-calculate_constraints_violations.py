from SCRBenchmark import Benchmark, FEYNMAN_SRSD_HARD
from SCRBenchmark.registry import EQUATION_CLASS_DICT
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np

summary_best = pd.read_csv('./results/3-benchmark-results-best-configuration.csv')
summary_best['Configuration'] = ['best parameters'] * len(summary_best)


print('Creating Benchmark Sets')
benchmarks = {}
for equation_name in FEYNMAN_SRSD_HARD:
  print(equation_name)
  benchmarks[equation_name] = Benchmark(EQUATION_CLASS_DICT[equation_name])

def CheckConstraints(df, data_name):
  i = 0
  df
  length = len(df)
  for (idx,row) in df.iterrows():
    benchmark = benchmarks[row['EquationName']]
    df.loc[idx, 'ConstraintsMatched'] = False

    df.loc[idx, 'ConstraintsCount'] = len(benchmark.get_constraints())
    df.loc[idx, 'ConstraintsViolated']= df.loc[idx, 'ConstraintsCount']

    df.loc[idx, 'ConstraintsDerivative1Count'] = np.sum([ 1 for constraint in benchmark.get_constraints() if constraint['order_derivative'] == 1])
    df.loc[idx, 'ConstraintsViolatedDerivative1Count'] = df.loc[idx, 'ConstraintsDerivative1Count']

    df.loc[idx, 'ConstraintsDerivative2Count'] = np.sum([ 1 for constraint in benchmark.get_constraints() if constraint['order_derivative'] == 2])
    df.loc[idx, 'ConstraintsViolatedDerivative2Count'] = df.loc[idx, 'ConstraintsDerivative2Count'] 

    if(row['Successful'] == True):
      #we only have a model to check if the algorithm run was successful
      try:
        (success,violated) = benchmark.check_constraints(row['EquationString'])
        df.loc[idx, 'ConstraintsMatched'] = success
        df.loc[idx, 'ConstraintsViolated'] = len(violated)
        df.loc[idx, 'ConstraintsViolatedDerivative1Count'] = np.sum([ 1 for constraint in violated if constraint['order_derivative'] == 1])
        df.loc[idx, 'ConstraintsViolatedDerivative2Count'] = np.sum([ 1 for constraint in violated if constraint['order_derivative'] == 2])

        print(f"[{i}/{length}] - [{data_name}] - {row['EquationName']} - Success {success} - violated {df.loc[idx, 'ConstraintsViolated']}/{df.loc[idx, 'ConstraintsCount']} - violated d1 {df.loc[idx, 'ConstraintsViolatedDerivative1Count']}/{df.loc[idx, 'ConstraintsDerivative1Count']} - violated d2 {df.loc[idx, 'ConstraintsViolatedDerivative2Count']}/{df.loc[idx, 'ConstraintsDerivative2Count']}")

      except:
        print("An exception occurred") 

      
    i = i+1
    if(i%100 == 0):
      print('saving intermediate')
      df.to_csv(f'./results/{data_name}.csv')
  df.to_csv(f'./results/{data_name}.csv')

CheckConstraints(summary_best, '4-R2Score-and-Violations.csv')