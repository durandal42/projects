// A complex number, a + b*i, for real values of a and b.
public class Complex {

  public static final Complex ZERO = new Complex(0.0, 0.0);
  public static final Complex ONE =  new Complex(1.0, 0.0);
  public static final Complex I =  new Complex(0.0, 1.0);

  private final double r, i;

  public Complex(double r, double i) {
    this.r = r;
    this.i = i;
  }

  public String toString() {
    return "(" + r + " + " + i + "i)";
  }

  public static Complex add(Complex c1, Complex c2) {
    return new Complex(c1.r + c2.r, c1.i + c2.i);
  }

  public static Complex multiply(Complex c1, Complex c2) {
    return new Complex(c1.r * c2.r - c1.i * c2.i,
                       c1.r * c2.i + c1.i * c2.r);
  }

  public static Complex conjugate(Complex c) {
    return new Complex(c.r, -c.i);
  }

  public static Complex inverse(Complex c) {
    double d = c.r * c.r + c.i * c.i;
    return new Complex(c.r / d, -c.i / d);
  }

  public static Complex divide(Complex c1, Complex c2) {
    return multiply(c1, inverse(c2));
  }

  public static Complex negate(Complex c) {
    return new Complex(-c.r, -c.i);
  }

  public static Complex subtract(Complex c1, Complex c2) {
    return add(c1, negate(c2));
  }

  public static double abs(Complex c) {
    return Math.sqrt(c.r*c.r + c.i*c.i);
  }

  public static double angle(Complex c) {
    return Math.atan2(c.i, c.r);
  }

  public static Complex power(Complex c1, Complex c2) {
    double a = c1.r;
    double b = c1.i;
    double c = c2.r;
    double d = c2.i;

    double apbsq = a*a + b*b;
    double arg = angle(c1);

    double x = Math.pow(apbsq, c / 2.0) * Math.exp(-d * arg);
    double y = c * arg + 0.5 * d * Math.log(apbsq);

    return new Complex(x * Math.cos(y), x * Math.sin(y));
  }

  public static Complex ln(Complex c) {
    return new Complex(Math.log(abs(c)), angle(c));
  }
  public static Complex log(Complex b, Complex c) {
    return divide(ln(c), ln(b));
  }

}
