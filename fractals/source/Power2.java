public class Power2 implements Function {

  Function f1;
  Function f2;

  public Power2(Function func1, Function func2) {
    f1 = func1;
    f2 = func2;
  }

  public Complex apply(Complex input) {
    return Complex.power(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    //	D[u^v] = (u^v) * (v*D[u]/u + ln(u)*D[v])
    return new Product(this,
                       new Sum(new Quotient(new Product(f2,
                                                        f1.differentiate()),
                                            f1),
                               new Product(new Log(new Complex(Math.E, 0.0), f1),
                                           f2.differentiate())));
  }

  public String toString() {
    return "(" + f1 + ")^(" + f2 + ")";
  }
}
