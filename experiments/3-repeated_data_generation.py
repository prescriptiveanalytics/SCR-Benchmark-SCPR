from SCRBenchmark import FEYNMAN_SRSD_HARD,HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES
from SCRBenchmark import BenchmarkSuite
import json
import numpy as np
import pandas as pd

target_folder = './experiments/repeated_best_config_data'

best_configurations = pd.read_csv('./experiments/best_configurations.csv')
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
