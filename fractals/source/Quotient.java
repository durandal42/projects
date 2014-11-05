public class Quotient implements Function {

  Function f1;
  Function f2;

  public Quotient(Function func1, Function func2) {
    f1 = func1;
    f2 = func2;;
  }

  public Complex apply(Complex input) {
    return Complex.divide(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    // D[u/v] = (v*D[u] - u*D[v]) /(v^2)
    return new Quotient(new Sum(new Product(f2, f1.differentiate()),
                                new Product(new Product(f1, f2.differentiate()),
                                            new Constant(new Complex(-1.0, 0.0)))),
                        new Power(f2, new Complex(2.0, 0.0)));
  }

  public String toString() {
    return "(" + f1 + ")/(" + f2 + ")";
  }

}
