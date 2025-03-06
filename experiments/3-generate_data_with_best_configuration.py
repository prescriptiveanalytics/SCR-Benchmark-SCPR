from SCRBenchmark import FEYNMAN_SRSD_HARD,HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES
from SCRBenchmark import BenchmarkSuite
from SCRBenchmark import StringKeys as sk

import json
import numpy as np
import pandas as pd

target_folder = './experiments/repeated_best_config_data'

best_configurations = pd.read_csv('./results/2-best_gridsearch_config.csv')
print('generating instances')
#creates one folder per equation under the parent folder
# each equation folder contains the info file as json
# and the data files for each configuration as csv
BenchmarkSuite.create_hard_instances(target_folder = target_folder,
                                      Equations= FEYNMAN_SRSD_HARD,
                                      sample_sizes=HARD_SAMPLE_SIZES,
                                      noise_levels=HARD_NOISE_LEVELS,
                                      repetitions = 5
                                      )


# for shape-constrained polynomial regression we add
# the algorithm configuration to the generated json files
print('appending info for SCPR')
for equation_name in FEYNMAN_SRSD_HARD:
  print(equation_name)
  equation_folder = f'{target_folder}/{equation_name}'
  best_configuration = best_configurations[best_configurations['EquationName'] == equation_name]
  if(len(best_configuration) == 0 ):
    print("no gridsearch result found for equation")

  with open(f'{equation_folder}/constraint_info.json', "r+") as f:
    data = json.load(f)
    data['Degrees']= list(best_configuration['Degree'])
    data['Lambdas']= list(best_configuration['Lambda'])
    data['Alphas']= list(best_configuration['Alpha'])
    data['MaxInteractions']= list(best_configuration['MaxInteractions'])

    supportedConstraints = []
    for constraint in data['Constraints']:
      if constraint['descriptor'] == sk.EQUATION_CONSTRAINTS_DESCRIPTOR_NEGATIVE:
        constraint['descriptor'] = 'decreasing'
      if constraint['descriptor'] == sk.EQUATION_CONSTRAINTS_DESCRIPTOR_POSITIVE:
        constraint['descriptor'] = 'increasing'
      
      supportedConstraints.append(constraint)
    data['Constraints'] = supportedConstraints
    
    f.seek(0)
    f.write(str(data).replace('\'',"\""))
    f.truncate()
    f.close()

    