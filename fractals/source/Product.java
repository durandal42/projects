public class Product implements Function {

  Function f1;
  Function f2;

  public Product(Function func1, Function func2) {
    f1 = func1;
    f2 = func2;;
  }

  public Complex apply(Complex input) {
    return Complex.multiply(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    return new Sum(new Product(f1, f2.differentiate()),
                   new Product(f2, f1.differentiate()));
  }

  public String toString() {
    return "(" + f1 + ")^(" + f2 + ")";
  }
}
