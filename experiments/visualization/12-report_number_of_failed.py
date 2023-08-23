from SCRBenchmark import Benchmark
from SCRBenchmark.SRSDFeynman import FeynmanICh6Eq20a
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np

summary_best = pd.read_csv('./experiments/results/summary_best.csv')
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

summary['Failed'] = np.invert(summary['Successful'])
summary = summary[['Configuration', 'Failed']]
group = summary.groupby(['Configuration']).sum().reset_index()

bx = sns.barplot(y='Failed',
          x = "Configuration",
          data=group )
for i in bx.containers:
    bx.bar_label(i,)
bx.set_xlabel('')
bx.set_ylabel('number of failed executions')
plt.savefig('./results/number_of_unsuccessful_runs.pdf')
plt.savefig('./results/number_of_unsuccessful_runs.png', dpi = 500)
plt.close()