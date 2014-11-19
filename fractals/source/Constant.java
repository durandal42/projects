// A constant function: y = c
public class Constant implements Function {

  // Some useful constants:
  public static final Constant ZERO = new Constant(Complex.ZERO);
  public static final Constant ONE = new Constant(Complex.ONE);

  private Complex c;

  public Constant(Complex c) {
    this.c = c;
  }

  public Complex apply(Complex input) {
    return c;
  }

  public Function differentiate() {
    // The derivative of any constant function is zero.
    return ZERO;
  }

  public String toString() {
    return c.toString();
  }

}
