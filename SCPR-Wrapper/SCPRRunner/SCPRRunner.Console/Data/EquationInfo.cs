namespace SCPRRunner.Console.Data {
  public class EquationInfo {
    public string EquationName { get; set; }
    public string TargetVariable { get; set; }
    public int[] Degrees { get; set; }
    public double[] Lambdas { get; set; }
    public double[] Alphas { get; set; }
    public int[] MaxInteractions { get; set; }
    public List<ConstraintInfo> Constraints { get; set; }       
    
    public List<VariableInfo> InputVariableRanges { get; set; }
  }
  public class ConstraintInfo {
    public string var_name { get; set; }
    public string var_display_name { get; set; }
    public int order_derivative { get; set; }
    public string descriptor { get; set; }
    public string derivative { get; set; }
    public List<VariableInfo> sample_space { get; set; }
    public int id { get; set; }
  }
  public class VariableInfo {
    public string name { get; set; }
    public double low { get; set; }
    public double high { get; set; }
  }
}
