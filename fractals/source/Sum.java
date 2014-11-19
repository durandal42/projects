// The sum of two functions, y = f1(x) + f2(x).
public class Sum implements Function {

  private final Function f1;
  private final Function f2;

  public Sum(Function f1, Function f2) {
    this.f1 = f1;
    this.f2 = f2;;
  }

  public Complex apply(Complex input) {
    return Complex.add(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    // The derivative of a sum is the sum of the derivatives.
    return new Sum(f1.differentiate(), f2.differentiate());
  }

  public String toString() {
    return "(" + f1 + ")+(" + f2 + ")";
  }

}
