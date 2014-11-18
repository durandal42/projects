// Annotated Complex number, also includes how many steps it took to converge
// to this number.
public class NewtonResult {
  public int steps;
  public Complex solution;

  public NewtonResult(Complex c, int s) {
    steps = s;
    solution = c;
  }
}