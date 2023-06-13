import numpy as np
import shutil
import filecmp
import os
import SCRBenchmark.SRSDFeynman as srsdf
from SCRBenchmark import BenchmarkSuite, FEYNMAN_SRSD_HARD, HARD_NOISE_LEVELS,HARD_SAMPLE_SIZES

folder1 = './experiments/repeated_best_config_data'
folder2 = './experiments/repeated_best_degree2_data'
folder3 = './experiments/repeated_best_degree3_data'

# must list only the **/constraint_info.json files 
# as we manipulate these files to match the structure required for SCPR

for subdir, dirs, files in os.walk(folder1):
  for file in files:
    folder2Subdir = subdir.replace(folder1,folder2)
    folder3Subdir = subdir.replace(folder1,folder3)
    file1 = os.path.join(subdir, file)
    file2 = os.path.join(folder2Subdir, file)
    file3 = os.path.join(folder3Subdir, file)
    if(not filecmp.cmp(file1, file2, shallow=False)):
      print(f'Not equal {file1} {file2}')
    if(not filecmp.cmp(file1, file3, shallow=False)):
      print(f'Not equal {file1} {file3}')