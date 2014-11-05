public class NewtonResult {
  public int steps;
  public Complex solution;

  public NewtonResult(Complex c, int s) {
    steps = s;
    solution = c;
  }
}