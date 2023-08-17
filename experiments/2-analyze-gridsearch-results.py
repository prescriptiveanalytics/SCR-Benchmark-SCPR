
import pandas as pd
import numpy as np

summary = pd.read_csv('./experiments/gridsearch_results/summary.csv')
summary['SampleSize'] = [ filename.split('sample_size')[1].split('_')[0] for filename in summary['DataSourceFile']]
summary['NoiseLevel'] = [ filename.split('noise_level')[1].split('_')[0] for filename in summary['DataSourceFile']]
# summary = summary[ summary['EquationName'].str.contains('FeynmanBonus')]

summary = summary[ summary['Degree'] <= 5]
summary = summary[ summary['MaxInteractions'] <= 3]

max_training_rmse = np.max(summary['RMSE_Training'])
max_test_rmse = np.max(summary['RMSE_Test'])
max_rmse = np.max(summary['RMSE_Full'])

#replace the default value of unseccussful runs with the maximum known value
summary.loc[summary['RMSE_Training'] == -1 ,'RMSE_Training'] = max_training_rmse
summary.loc[summary['RMSE_Test'] == -1 ,'RMSE_Test'] = max_test_rmse
summary.loc[summary['RMSE_Full'] == -1 ,'RMSE_Full'] = max_rmse


summary = summary[['EquationName','Degree','Lambda','Alpha','MaxInteractions', 'RMSE_Test']]
configuration = summary.groupby(['EquationName','Degree','Lambda','Alpha','MaxInteractions']).mean() 
configuration = configuration.reset_index()
print(configuration.groupby(['EquationName']).min())

best_configuration = configuration.iloc[configuration.groupby(['EquationName']).idxmin()['RMSE_Test'].values]
best_configuration = best_configuration.sort_values('EquationName')
best_configuration = best_configuration.reset_index()
print(best_configuration)
best_configuration = best_configuration[['EquationName','Degree','Lambda','Alpha','MaxInteractions']]
print(len(best_configuration))
best_configuration.to_csv('./experiments/best_configurations.csv', index = False)

degree2_configuration = configuration[configuration['Degree'] == 2].reset_index()
best_degree2_configuration = degree2_configuration.iloc[degree2_configuration.groupby(['EquationName']).idxmin()['RMSE_Test'].values]
best_degree2_configuration = best_degree2_configuration.sort_values('EquationName')
best_degree2_configuration = best_degree2_configuration.reset_index()
print(best_degree2_configuration)
best_degree2_configuration = best_degree2_configuration[['EquationName','Degree','Lambda','Alpha','MaxInteractions']]
print(len(best_degree2_configuration))
best_degree2_configuration.to_csv('./experiments/best_degree2_configuration.csv', index = False)

degree3_configuration = configuration[configuration['Degree'] == 3].reset_index()
best_degree3_configuration = degree3_configuration.iloc[degree3_configuration.groupby(['EquationName']).idxmin()['RMSE_Test'].values]
best_degree3_configuration = best_degree3_configuration.sort_values('EquationName')
best_degree3_configuration = best_degree3_configuration.reset_index()
print(best_degree3_configuration)
best_degree3_configuration = best_degree3_configuration[['EquationName','Degree','Lambda','Alpha','MaxInteractions']]
print(len(best_degree3_configuration))
best_degree3_configuration.to_csv('./experiments/best_degree3_configuration.csv', index = False)