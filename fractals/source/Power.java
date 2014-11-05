public class Power implements Function {

  Function f;
  Complex p;

  public Power(Function func1, Complex power) {
    f = func1;
    p = power;
  }

  public Complex apply(Complex input) {
    return Complex.power(f.apply(input), p);
  }

  public Function differentiate() {
    return new Product(new Constant(p),
                       new Power(f,
                                 Complex.add(p,
                                             new Complex(-1.0, 0.0))));
  }

  public String toString() {
    return "(" + f + ")^(" + p + ")";
  }

  public static void main(String[] args) {
    Function f;
    f = new Exp(new Complex(2.0, 0.0),
                Identity.IDENTITY);
    System.out.println(f);
    System.out.println(f.differentiate());

    f = new Power(Identity.IDENTITY,
                  new Complex(2.0, 0.0));
    System.out.println(f);
    System.out.println(f.differentiate());

    f = new Power2(Identity.IDENTITY,
                   Identity.IDENTITY);
    System.out.println(f);
    System.out.println(f.differentiate());
  }
}
