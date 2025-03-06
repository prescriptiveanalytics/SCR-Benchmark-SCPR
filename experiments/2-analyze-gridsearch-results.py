
import pandas as pd
import numpy as np

summary = pd.read_csv('./results/1-gridsearch_results.csv')
summary['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in summary['DataSourceFile']]
summary['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in summary['DataSourceFile']]


print(f"unique quations: {len(np.unique(summary['EquationName']))}")

max_training_R2 = np.max(summary['R2_Training'])
max_test_R2 = np.max(summary['R2_Test'])
max_R2 = np.max(summary['R2_Full'])

#replace the default value of unseccussful runs with the worst known value
summary.loc[summary['R2_Training'] == -1 ,'R2_Training'] = max_training_R2
summary.loc[summary['R2_Test'] == -1 ,'R2_Test'] = max_test_R2
summary.loc[summary['R2_Full'] == -1 ,'R2_Full'] = max_R2


summary = summary[['EquationName','Degree','Lambda','Alpha','MaxInteractions', 'R2_Test']]
configuration = summary.groupby(['EquationName','Degree','Lambda','Alpha','MaxInteractions']).mean() 
configuration = configuration.reset_index()
print(configuration.groupby(['EquationName']).count())

best_configuration = configuration.iloc[configuration.groupby(['EquationName']).idxmin()['R2_Test'].values]
best_configuration = best_configuration.sort_values('EquationName')
best_configuration = best_configuration.reset_index()
print(best_configuration)
best_configuration = best_configuration[['EquationName','Degree','Lambda','Alpha','MaxInteractions']]
print(len(best_configuration))
best_configuration.to_csv('./results/2-best_gridsearch_config.csv', index = False)
