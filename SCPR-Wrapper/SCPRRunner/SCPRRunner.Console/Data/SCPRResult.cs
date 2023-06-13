namespace SCPRRunner.Console.Data {
  public class SCPRResult {
    public string EquationName { get; set; }
    public string DataSourceFile { get; set; }
    public string DataTargetFile { get; set; }
    public string EquationString { get; set; }

    public double Degree { get; set; }
    public double Lambda { get; set; }
    public double Alpha { get; set; }
    public double MaxInteractions { get; set; }

    public long Runtime { get; set; } = 0;
    public bool Successful { get; set; } = false;

    public double RMSE_Training { get; set; }
    public double RMSE_Test { get; set; }
    public double RMSE_Full { get; set; }

    public double R2_Training { get; set; }
    public double R2_Test { get; set; }
    public double R2_Full { get; set; }

    public int SameConfiguration(object? obj) {
      if (!(obj is SCPRResult)) return -1;
      var other = obj as SCPRResult;
      if (other == null) return -1;

      int comp;
      if ((comp = other.EquationName.CompareTo(EquationName)) != 0)
        return comp;
      if ((comp = other.DataSourceFile.CompareTo(DataSourceFile)) != 0)
        return comp;
      if ((comp = other.Degree.CompareTo(Degree)) != 0)
        return comp;
      if ((comp = other.Lambda.CompareTo(Lambda)) != 0)
        return comp;
      if ((comp = other.Alpha.CompareTo(Alpha)) != 0)
        return comp;
      if ((comp = other.MaxInteractions.CompareTo(MaxInteractions)) != 0)
        return comp;
      return 0;
    }
  }
}
