public class Exp implements Function {

  Complex b;
  Function f;

  public Exp(Complex base, Function func) {
    b = base;
    f = func;
  }

  public Complex apply(Complex input) {
    return Complex.power(b, f.apply(input));
  }

  public Function differentiate() {
    return new Product(new Constant(Complex.ln(b)),
                       this);
  }

  public String toString() {
    return "(" + b + ")^(" + f + ")";
  }

}
