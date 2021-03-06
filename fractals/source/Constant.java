// A constant function: y = c
public class Constant implements Function {

  // Some useful constants:
  public static final Constant ZERO = new Constant(Complex.ZERO);
  public static final Constant ONE = new Constant(Complex.ONE);

  private final Complex c;

  public Constant(Complex c) {
    this.c = c;
  }

  public Complex apply(Complex unused) {
    // f(x) = c
    return c;
  }

  public Function differentiate() {
    // f'(c) = 0
    return ZERO;
  }

  public String toString() {
    return c.toString();
  }

}
