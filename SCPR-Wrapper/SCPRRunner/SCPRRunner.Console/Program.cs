using System.Globalization;
using System.Text;
using CsvHelper;
using mosek;
using mosek.fusion;
using Newtonsoft.Json;
using SCPRRunner.Console.Data;
using ShapeConstrainedPolynomialRegression;
using static ShapeConstrainedPolynomialRegression.Regression;
using ConstraintTuple = System.Tuple<string, int, double, int, double[], double[]>;

int argumentIndex = 0;
foreach (var argument in Environment.GetCommandLineArgs()) {
  Console.WriteLine($"argument[{argumentIndex}]: {argument}");
  argumentIndex++;
}

Console.WriteLine("Expected Argument Order: ");
Console.WriteLine("argument[1]: training data folder for individual models");
Console.WriteLine("argument[2]: resulting data folder for individual model reports");
Console.WriteLine("argument[3]: resulting csv file location");
Console.WriteLine("argument[4]: int degree of parallelism");
Console.WriteLine("argument[5]: write individual csv files");
Console.WriteLine("argument[6]: maximum restarts");

//prepare data sources and result path
string dataParentFolder = Environment.GetCommandLineArgs()[1];
string resultFolder = Environment.GetCommandLineArgs()[2];
string mlResultFile = Environment.GetCommandLineArgs()[3];
int degreeParallelism = int.Parse(Environment.GetCommandLineArgs()[4]);
bool writeIndividualResultFiles = bool.Parse(Environment.GetCommandLineArgs()[5]);
int max_restarts = int.Parse(Environment.GetCommandLineArgs()[6]);
var file_write_lock = new object();


//read previous results
List<SCPRResult> results;
using (var reader = new StreamReader(mlResultFile, new FileStreamOptions() { Access = FileAccess.ReadWrite, Mode = FileMode.OpenOrCreate }))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture)) {
  results = csv.GetRecords<SCPRResult>().ToList();
}


var dataFiles = Directory.GetFiles(dataParentFolder, "*.csv", SearchOption.AllDirectories).OrderBy(x=>x).Select(path => new FileInfo(path));


//calculate for each data file
Parallel.ForEach(dataFiles,
  new ParallelOptions { MaxDegreeOfParallelism = degreeParallelism },
dataFile => {
  try {
    List<dynamic> records;

    var dataFile_FileName = Path.GetFileNameWithoutExtension(dataFile.Name);


    using (var reader = new StreamReader(dataFile.FullName))
    using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture)) {
      records = csv.GetRecords<dynamic>().ToList();
    }

    var first_record = records.First();
    var equation_name = dataFile.Directory.Name;

    var fileContent = File.ReadAllText(Path.Combine(dataFile.Directory.FullName, $"constraint_info.json"));

    var equation_parameters = JsonConvert.DeserializeObject<EquationInfo>(fileContent);
    var target = equation_parameters.TargetVariable;

    var countAll = records.Count();

    var training_records = records.Where(x => x.split == "training").ToList();
    var test_records = records.Where(x => x.split == "test").ToList();

    var inputVariables = equation_parameters.InputVariableRanges.Select(x => x.name).ToArray();
    ExtractScaledData(records, equation_parameters.InputVariableRanges.ToArray(), target, out double[,] X_full, out double[] y_full);
    ExtractScaledData(training_records, equation_parameters.InputVariableRanges.ToArray(), target, out double[,] X_train, out double[] y_train);
    ExtractScaledData(test_records, equation_parameters.InputVariableRanges.ToArray(), target, out double[,] X_test, out double[] y_test);

    ConstraintTuple[] constraints = CreateConstraint(equation_parameters).ToArray();
    foreach (var degree in equation_parameters.Degrees) {
      foreach (var interactions in equation_parameters.MaxInteractions) {
        foreach (var lambda in equation_parameters.Lambdas) {
          foreach (var alpha in equation_parameters.Alphas) {
            var minimumValue_MaxInterations = equation_parameters.MaxInteractions.Min();
            if ( (interactions> inputVariables.Length)   && (interactions> minimumValue_MaxInterations)) {
              Console.WriteLine($"file: {dataFile} degree: {degree} interactions:{interactions} lambda:{lambda} alpha: {alpha} skipping because interactions are not available");

              continue;
            }


            var predictionResultFileName = $"{dataFile_FileName}_d{degree}_i{interactions}_l{lambda}_a{alpha}.csv";
            var result_path = Path.Combine(resultFolder, predictionResultFileName);

            var result_record = new SCPRResult() {
              EquationName = equation_name,
              DataSourceFile = dataFile.FullName,
              DataTargetFile = result_path,
              Degree = degree,
              Lambda = lambda,
              Alpha = alpha,
              MaxInteractions = interactions,
              Runtime = 0,
              Successful = false,
              RMSE_Full = double.MaxValue,
              RMSE_Test = double.MaxValue,
              RMSE_Training = double.MaxValue,
              R2_Full = double.MinValue, 
              R2_Test = double.MinValue, 
              R2_Training = double.MinValue
            };


            //not calculated yet
            if (!results.Any(x => x.SameConfiguration(result_record) == 0)) {

              var tokenSource = new CancellationTokenSource();
              var timer = new System.Timers.Timer(TimeSpan.FromMinutes(2.5).TotalMilliseconds);
              timer.Elapsed += delegate {
                Console.WriteLine($"file: {dataFile} degree: {degree} interactions:{interactions} lambda:{lambda} alpha: {alpha} TIMER ELAPSED");

                tokenSource.Cancel();
                WriteAppend(mlResultFile, result_record);

              };

              var watch = new System.Diagnostics.Stopwatch();
              watch.Start();

              int restart = 0;
              bool success = false;

              Polynomial polynomial = null;
              while ((! (success = TrainModel(X: X_train, y: y_train, inputs: inputVariables, target: target,
                            degree: degree, alpha: alpha, lambda: lambda,
                            max_interactions: interactions, constraints: constraints, cancellationToken: tokenSource.Token, out polynomial,
                            out Result regressionResult))) && restart < max_restarts) {
                restart++;
                var seed = $"{equation_name}{restart}";
                var rand1 = new Random(seed.GetHashCode());
                var rand2 = new Random(seed.GetHashCode());
                X_train = Shuffle2D(rand1,X_train);
                y_train = Shuffle1D(rand2,y_train);
              }  

              if (success) {

                watch.Stop();
                Console.WriteLine($"Execution Time: {watch.ElapsedMilliseconds} ms");

                result_record.Runtime = watch.ElapsedMilliseconds;
                result_record.Successful = true;

                var y_predicted = CalculatePrediction(polynomial, X_full);
                var y_predicted_test = CalculatePrediction(polynomial, X_test);
                var y_predicted_train = CalculatePrediction(polynomial, X_train);
                result_record.EquationString = GetInfixNotation(polynomial, equation_parameters);
                result_record.RMSE_Test = CalculateRMSE(y_test, y_predicted_test);
                result_record.RMSE_Training = CalculateRMSE(y_train, y_predicted_train);
                result_record.RMSE_Full = CalculateRMSE(y_full, y_predicted);

                result_record.R2_Test = CalculateR2(y_test, y_predicted_test);
                result_record.R2_Training = CalculateR2(y_train, y_predicted_train);
                result_record.R2_Full = CalculateR2(y_full, y_predicted);

                for (int i = 0; i < records.Count(); i++) {
                  records.ElementAt(i).Predicted = y_predicted[i];
                }

                Console.WriteLine($"file: {dataFile} degree: {degree} interactions:{interactions} lambda:{lambda} alpha: {alpha} R2_Training: {result_record.R2_Training} R2_Test: {result_record.R2_Test}");

                if (writeIndividualResultFiles) {
                  if (!Directory.Exists(Path.GetDirectoryName(result_path))) Directory.CreateDirectory(Path.GetDirectoryName(result_path));
                  if (!File.Exists(result_path))
                    using (File.Create(result_path)) { }

                  using (var writer = new StreamWriter(result_path, append: false))
                  using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture)) {
                    csv.WriteRecords(records);
                    csv.Flush();
                    writer.Flush();
                  }
                }
              }
              WriteAppend(mlResultFile, result_record);
            }
          }
        }
      }
    }
  }
  catch (System.Exception ex) {
    Console.WriteLine(ex.Message);
  }
});

void ExtractScaledData(IEnumerable<dynamic> test_records, VariableInfo[] variables, string target, out double[,] X, out double[] y) {
  string[] allowed_inputs = variables.Select(x => x.name).ToArray();
  X = new double[test_records.Count(), allowed_inputs.Count()];
  y = new double[test_records.Count()];
  for (int i = 0; i < test_records.Count(); i++) {
    var row_record = (IDictionary<string, dynamic>)test_records.ElementAt(i);
    for (int j = 0; j < variables.Count(); j++) {
      var var_index = Array.IndexOf(allowed_inputs, variables[j].name);
      if (var_index >= 0) {
        var val = double.Parse(row_record[variables[j].name], CultureInfo.InvariantCulture);
        X[i, var_index] = Scale(val, variables[j].low, variables[j].high);
      }
    }
    y[i] = double.Parse(row_record[target], CultureInfo.InvariantCulture);
  }
}

double[] CalculatePrediction(Polynomial optimizedModel, double[,] x) {
  return Regression.Evaluate(optimizedModel, x);
}

bool TrainModel(double[,] X, double[] y, string[] inputs, string target, int degree, double alpha, double lambda,
                int max_interactions, Tuple<string, int, double, int, double[], double[]>[] constraints, CancellationToken cancellationToken,
                out Polynomial optimizedModel, out Result regressionResult) {

  optimizedModel = default;
  regressionResult = default;
  try {
    optimizedModel = ShapeConstrainedPolynomialRegression.Regression.Run(variableNames: inputs,
                                    X,
                                    y,
                                    degree: degree,
                                    maxVarsInInteraction: max_interactions,
                                    constraints: constraints,
                                    lambda: lambda,
                                    alpha: alpha,
                                    out regressionResult,
                                    scaleFeatures: true,
                                    approximation: "SDP",
                                    positivstellensatzDegree: -1,
                                    cancellationToken: cancellationToken);
  }
  catch (System.Exception e) {
    Console.WriteLine(e.ToString());
  }
  if (optimizedModel != null) {
    return true;
  }
  return false;
}



void WriteAppend<T>(string filePath, T record) {
  // This text is added only once to the file.
  if (!File.Exists(filePath)) {
    File.Create(filePath);
  } else {
    // Create a file to write to.
    lock (file_write_lock) {
      using (StreamWriter sw = new StreamWriter(filePath, append: true)) {
        using (var csv = new CsvWriter(sw, CultureInfo.InvariantCulture)) {
          if ((new FileInfo(filePath)).Length == 0) {
            csv.WriteHeader<T>();
            csv.NextRecord();
          }
          csv.WriteRecord(record);
          csv.NextRecord();
          sw.Flush();
        }
        sw.Close();
      }
    }
  }
}

T[,] Shuffle2D<T>(Random rng, T[,] old) {
  T[,] array = new T[old.GetLength(0), old.GetLength(1)];
  Array.Copy(old, array, old.Length);
  int n = array.GetLength(0);
  while (n > 1) {
    int k = rng.Next(n--);
    for (int j = 0; j < old.GetLength(1); j++) {
      T temp = array[n, j];
      array[n, j] = array[k, j];
      array[k, j] = temp;
    }
  }
  return array;
}

T[] Shuffle1D<T>(Random rng, T[] old) {
  T[] array = new T[old.Length];
  Array.Copy(old, array, old.Length);
  int n = array.Length;
  while (n > 1) {
    int k = rng.Next(n--);
    T temp = array[n];
    array[n] = array[k];
    array[k] = temp;
  }
  return array;
}

double CalculateRMSE(double[] y_target, double[] y_predicted) {
  if (y_target.Length != y_predicted.Length)
    throw new ArgumentException($"Length of the two arrays {nameof(y_target)} and {nameof(y_predicted)} must match.");
  var sumSqRes = 0.0;
  for (int i = 0; i < y_predicted.Length; i++) sumSqRes += ((y_target[i] - y_predicted[i]) * (y_target[i] - y_predicted[i])) / y_predicted.Length;
  return Math.Sqrt(sumSqRes);
}

double CalculateR2(double[] y_target, double[] y_predicted) {
  if (y_target.Length != y_predicted.Length)
    throw new ArgumentException($"Length of the two arrays {nameof(y_target)} and {nameof(y_predicted)} must match.");

  var y_hat = y_predicted;
  var y = y_target;
  var y_bar = y.Average();

  var sumSqRes = 0.0; //residual sum of squares
  for (int i = 0; i < y_predicted.Length; i++) sumSqRes += ((y[i] - y_hat[i]) * (y[i] - y_hat[i]))/ y_predicted.Length;
  var sumSqTot = 0.0; //variance of data
  for (int i = 0; i < y_predicted.Length; i++) sumSqTot += ((y[i] - y_bar) * (y[i] - y_bar))/ y_predicted.Length;

  return 1 - (sumSqRes / sumSqTot);
}

double Scale(double val, double minimum, double maximum) {

  double range = maximum - minimum;
  double multiplier = 2.0 / range;
  double addend = -1 - multiplier * minimum;

  return val * multiplier + addend;
}

VariableInfo GetRangeForVariabele(string variableName, EquationInfo equationInfo) {
  return equationInfo.InputVariableRanges.Single(x => x.name == variableName);
}

IEnumerable<ConstraintTuple> CreateConstraint(EquationInfo equationInfo) {
  foreach (var constraint in equationInfo.Constraints) {
    var lb = constraint.sample_space.Select(x => Scale(x.low, GetRangeForVariabele(x.name, equationInfo).low, GetRangeForVariabele(x.name, equationInfo).high)).ToArray();
    var ub = constraint.sample_space.Select(x => Scale(x.high, GetRangeForVariabele(x.name, equationInfo).low, GetRangeForVariabele(x.name, equationInfo).high)).ToArray();
    if (constraint.descriptor.Contains("increasing"))
      yield return Tuple.Create(constraint.var_name,
        constraint.order_derivative,
        0.0,  // threshold (here, lowest function value)
        1,    // sign
        (double[])lb.Clone(),   // the input space bounds
        (double[])ub.Clone());  // the input space bounds    
    else if (constraint.descriptor.Contains("decreasing"))
      yield return Tuple.Create(constraint.var_name,
        constraint.order_derivative,
        0.0,    // threshold (here, highest function value)
        -1,  // sign
        (double[])lb.Clone(),   // the input space bounds
        (double[])ub.Clone());  // the input space bounds   

  }
}



string GetInfixNotation(Polynomial Polynomial, EquationInfo equationInfo) {
  var sb = new StringBuilder();
  int paramIdx = 0;
  foreach (var mono in Polynomial.Terms) {
    if (Polynomial.Weights[paramIdx] != 0.0) {
      if (sb.Length > 0) sb.Append(" + ");

      if (Polynomial.Weights[paramIdx] != 1.0) {
        sb.Append($"{Polynomial.Weights[paramIdx].ToString(CultureInfo.InvariantCulture)}");
        if (mono.powers.Any(p => p.Value != 0))
          sb.Append($" * ");
      }

      if (mono.powers.Any(p => p.Value != 0)) {
        sb.Append(MonomialInfixNotation(mono, equationInfo));
      }
    }
    paramIdx++;
  }
  return sb.ToString();
}

string? MonomialInfixNotation(Monomial mono, EquationInfo equationInfo) {
  var sb = new StringBuilder();
  var powers = mono.powers.OrderBy(kvp => kvp.Key).ToArray();
  var numOfPowers = powers.Count();
  for (int i = 0; i < numOfPowers; i++) {
    var kvp = powers[i];
    var p = kvp.Value;
    var s = kvp.Key;
    if (p == 1) sb.Append(SymbolInfixNotation(s, equationInfo));
    else if (p != 0) sb.Append("(").Append(SymbolInfixNotation(s, equationInfo)).Append("**").Append(p).Append(")");
    if (numOfPowers > 1 && i < numOfPowers - 1) {
      //we are not at the last one
      sb.Append(" * ");
    }
  }
  if (sb.Length == 0) sb.Append(1);
  return sb.ToString();
}

string? SymbolInfixNotation(Symbol sym, EquationInfo equationInfo) {
  string[] allowed_inputs = equationInfo.InputVariableRanges.Select(x => x.name).ToArray();
  var rangeIndex = Array.IndexOf<string>(allowed_inputs, sym.Name);
  if (rangeIndex == -1)
    throw new ArgumentException($"Symbol of name {sym.Name} is not present in the available inputs of this model: '{string.Join(',', allowed_inputs)}'");
  var inputRange = equationInfo.InputVariableRanges[rangeIndex];

  double range = inputRange.high - inputRange.low ;
  double multiplier = 2.0 / range;
  double addend = -1 - multiplier * inputRange.low;

  if (double.IsNegative(addend)) {
    return $"(({sym.Name} * {multiplier.ToString(CultureInfo.InvariantCulture)}) {addend.ToString(CultureInfo.InvariantCulture)})";
  }
  return $"(({sym.Name} * {multiplier.ToString(CultureInfo.InvariantCulture)}) +{addend.ToString(CultureInfo.InvariantCulture)})";
}