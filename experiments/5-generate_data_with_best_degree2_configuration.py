from SCRBenchmark import FEYNMAN_SRSD_HARD,HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES
from SCRBenchmark import BenchmarkSuite
import json
import numpy as np
import pandas as pd

target_folder = './experiments/repeated_best_degree2_data'

best_configurations = pd.read_csv('./experiments/best_degree2_configuration.csv')
# instances = FEYNMAN_SRSD_HARD
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

print('generating instances')
#creates one folder per equation under the parent folder
# each equation folder contains the info file as json
# and the data files for each configuration as csv
BenchmarkSuite.create_hard_instances(target_folder = target_folder,
                                      Equations= instances,
                                      sample_sizes=HARD_SAMPLE_SIZES,
                                      noise_levels=HARD_NOISE_LEVELS,
                                      repetitions = 10
                                      )


# for shape-constrained polynomial regression we add
# the algorithm configuration to the generated json files
print('appending info for SCPR')
for equation_name in instances:
  print(equation_name)
  equation_folder = f'{target_folder}/{equation_name}'
  best_configuration = best_configurations[best_configurations['EquationName'] == equation_name]
  with open(f'{equation_folder}/constraint_info.json', "r+") as f:
    data = json.load(f)
    data['Degrees']= list(best_configuration['Degree'])
    data['Lambdas']= list(best_configuration['Lambda'])
    data['Alphas']= list(best_configuration['Alpha'])
    data['MaxInteractions']= list(best_configuration['MaxInteractions'])

    supportedConstraints = []
    for constraint in data['Constraints']:
      if constraint['order_derivative'] == 2:
        # our current SCPR implementation only supports partial derivatives of 
        # order 2 if we derive over the same variable twice
        variables = np.unique(constraint['var_name'])
        variables_display = np.unique(constraint['var_display_name'])
        if(len(variables) == 1):
          constraint['var_name'] = variables[0]
          constraint['var_display_name'] = variables_display[0]
          supportedConstraints.append(constraint)
      else:
        supportedConstraints.append(constraint)
    data['Constraints'] = supportedConstraints
    
    f.seek(0)
    f.write(str(data).replace('\'',"\""))
    f.truncate()
    f.close()

    