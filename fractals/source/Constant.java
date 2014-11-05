public class Constant implements Function {

  public static final Constant ZERO = new Constant(Complex.ZERO);
  public static final Constant ONE = new Constant(Complex.ONE);

  Complex c;

  public Constant(Complex comp) {
    c = comp;
  }

  public Complex apply(Complex input) {
    return c;
  }

  public Function differentiate() {
    return ZERO;
  }

  public String toString() {
    return c.toString();
  }

}
