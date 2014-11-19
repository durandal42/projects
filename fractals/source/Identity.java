// The identity function, f(x) = x
public class Identity implements Function {

  public static final Function IDENTITY = new Identity();

  public Complex apply(Complex c) {
    // f(x) = x
    return c;
  }

  public Function differentiate() {
    // f'(x) = 1
    return Constant.ONE;
  }

  public String toString() {
    return "x";
  }

}
