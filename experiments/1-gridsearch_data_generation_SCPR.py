from SCRBenchmark import FEYNMAN_SRSD_HARD,HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES
from SCRBenchmark import BenchmarkSuite
from SCRBenchmark import StringKeys as sk
import json
import numpy as np

target_folder = './experiments/gridsearch_data'

Degrees = [2,3,4,5,6]
Lambdas = [10**-7,10**-6,10**-5,10**-4,10**-3,10**-2,10**-1,1,10]
Alphas = [0,0.5,1]
MaxInteractions = [2,3]

HARD_SAMPLE_SIZES = [100]
HARD_NOISE_LEVELS = [0.05]

print('generating instances')
#creates one folder per equation under the parent folder
# each equation folder contains the info file as json
# and the data files for each configuration as csv
BenchmarkSuite.create_hard_instances(target_folder = target_folder,
                                        Equations= FEYNMAN_SRSD_HARD,
                                        sample_sizes=HARD_SAMPLE_SIZES,
                                        noise_levels=HARD_NOISE_LEVELS,
                                        repetitions=1)

# for shape-constrained polynomial regression we add
# the algorithm configuration to the generated json files
print('appending info for SCPR')
for equation_name in FEYNMAN_SRSD_HARD:
  print(equation_name)
  equation_folder = f'{target_folder}/{equation_name}'

  with open(f'{equation_folder}/constraint_info.json', "r+") as f:
    data = json.load(f)
    data['Degrees']= Degrees
    data['Lambdas']= Lambdas
    data['Alphas']= Alphas
    data['MaxInteractions']= MaxInteractions

    supportedConstraints = []
    for constraint in data['Constraints']:
      # if constraint['order_derivative'] == 0:
      #   continue
      # if constraint['descriptor'] == sk.EQUATION_CONSTRAINTS_DESCRIPTOR_ZERO:
      #   continue
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

    