public class Log implements Function {

  Complex b;
  Function f;

  public Log(Complex base, Function func) {
    b = base;
    f = func;
  }

  public Complex apply(Complex input) {
    return Complex.log(b, f.apply(input));
  }

  public Function differentiate() {
    // D[log(x)] = 1/(x*ln(10))
    return new Quotient(new Constant(Complex.ONE),
                        new Product(Identity.IDENTITY,
                                    new Constant(Complex.ln(b))));
  }

  public String toString() {
    return "log" + b + "(" + f + ")";
  }

}
