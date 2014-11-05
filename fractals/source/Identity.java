public class Identity implements Function {

  public static final Function IDENTITY = new Identity();

  public Complex apply(Complex c) {
    return c;
  }

  public Function differentiate() {
    return Constant.ONE;
  }

  public String toString() {
    return "x";
  }

}
