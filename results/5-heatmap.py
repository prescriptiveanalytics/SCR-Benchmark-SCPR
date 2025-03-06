
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import seaborn as sns
import pandas as pd
import numpy as np
import random as rng
from SCRBenchmark import FEYNMAN_SRSD_HARD

mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

EQUATIONS_COUNT = len(FEYNMAN_SRSD_HARD)
REPETITIONS  = 5

font = {'size'   : 8}

mpl.rc('font', **font)

results = pd.read_csv('./results/4-R2Score-and-Violations.csv')

print(np.unique(results['EquationName']))
print(len(np.unique(results['EquationName'])))

results['ConstraintsCount'].fillna(1, inplace=True)
results['ConstraintsViolated'].fillna(1, inplace=True)
results['R2_Test'].fillna(-10, inplace=True)


results['ConstraintsAchievedScaled'] = 1-(results['ConstraintsViolated']/results['ConstraintsCount'])
results['ConstraintsAchievedScaled'].fillna(1, inplace=True)
results['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in results['DataSourceFile']]
results['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in results['DataSourceFile']]
results['CountHelper'] = [1] * len(results)

print(results[['ConstraintsCount','ConstraintsViolated','ConstraintsAchievedScaled']])

R2ScoreOrder = ["[−∞,0]","]0, 0.5]","]0.5, 0.75]","]0.75, 1]"]
def GetR2Score(row):

  if(row['R2_Test'] <= 0):
    return R2ScoreOrder[0]
  elif(row['R2_Test'] <= 0.5):
    return R2ScoreOrder[1]
  elif(row['R2_Test'] <= 0.75):
    return R2ScoreOrder[2]
  elif(row['R2_Test'] <= 1):
    return R2ScoreOrder[3]
  else:
    raise " missing a case "
results['R2_Score'] = [ GetR2Score(row) for (idx,row) in results.iterrows() ]
results["R2_Score"] = pd.Categorical(results['R2_Score'], categories=R2ScoreOrder)


ConstraintScoreOrder = ["0 %","] 0 %, 50 %]", "] 50 %, 100 %]", "100 %"]
def GetConstraintScore(row):
  if(row['ConstraintsAchievedScaled'] == 0):
    return ConstraintScoreOrder[0]
  elif(row['ConstraintsAchievedScaled'] <= 0.5):
    return ConstraintScoreOrder[1]
  elif(row['ConstraintsAchievedScaled'] < 1):
    return ConstraintScoreOrder[2]
  elif(row['ConstraintsAchievedScaled'] == 1):
    return ConstraintScoreOrder[3]
  else:
    raise " missing a case "
results['Constraint_Score'] = [ GetConstraintScore(row) for (idx,row) in results.iterrows() ]
results["Constraint_Score"] = pd.Categorical(results['Constraint_Score'], categories=ConstraintScoreOrder)



norm = Normalize(vmin=0, vmax=100)
cmap = sns.color_palette("flare", as_cmap=True)
# ax.set_xlabel(f'error function width $\psi$')
# ax.set_ylabel(f'noise level $\zeta$')
f, ax = plt.subplots(2,3, figsize=(5, 3), sharex=True, sharey=True)
plt.subplots_adjust(left=0.21, bottom=0.365, right=0.87, top=1, wspace=0.1, hspace=0.1)
cbar_ax = f.add_axes([.921, .55, .02, .3])

cbar_ax.set_xlabel(f'% of runs')
cbar_ax.set_ylabel(f'% of runs')

def scaled_counted_attempts(a):
  return np.sum(a) / (EQUATIONS_COUNT * REPETITIONS) * 100
row = 0
max_row_idx = len(np.unique(results['SampleSize']))-1
for sampleSize in np.unique(results['SampleSize']):
  col = 0
  for noiseLevel in np.unique(results['NoiseLevel']):
    df = results[ ((results['SampleSize'] == sampleSize) &
                      (results['NoiseLevel'] == noiseLevel)) ]

    pivot = df.pivot_table(index='R2_Score', columns='Constraint_Score',
                        values='CountHelper', aggfunc=scaled_counted_attempts, dropna=False, fill_value = 0)
 
    hm = sns.heatmap(data=pivot, ax=ax[row,col], norm=norm, cmap=cmap, cbar_ax=cbar_ax, annot=True, fmt='.1f', annot_kws={"size": 8})

    if((row == max_row_idx ) and (col == 1)):
      ax[row,col].set_xlabel(f'achieved constraints\nnoise level = {noiseLevel}')
    else:
      ax[row,col].set_xlabel(f'')
    if(col == 0):
      ax[row,col].set_ylabel(f'{sampleSize} samples\n$R^2$ validation')
    else:
      ax[row,col].set_ylabel(f'')

    col = col+1

  row = row+1


plt.savefig(f'./result-figures/heatmap.pdf',dpi = 500)
plt.savefig(f'./result-figures/heatmap.png',dpi = 500)
plt.show()