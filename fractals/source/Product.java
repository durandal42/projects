public class Product implements Function {

  Function f1;
  Function f2;

  public Product(Function func1, Function func2) {
    f1 = func1;
    f2 = func2;;
  }

  public Complex apply(Complex input) {
    // f(x) = f1(x) * f2(x)
    return Complex.multiply(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    // f'(x) = (f1(x) * f2'(x) +
    //          f1'(x) * f2(x))
    return new Sum(new Product(f1, f2.differentiate()),
                   new Product(f1.differentiate(), f2));
  }

  public String toString() {
    return "(" + f1 + ")^(" + f2 + ")";
  }
}
