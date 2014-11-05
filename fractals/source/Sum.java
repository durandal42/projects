public class Sum implements Function {

  Function f1;
  Function f2;

  public Sum(Function func1, Function func2) {
    f1 = func1;
    f2 = func2;;
  }

  public Complex apply(Complex input) {
    return Complex.add(f1.apply(input), f2.apply(input));
  }

  public Function differentiate() {
    return new Sum(f1.differentiate(), f2.differentiate());
  }

  public String toString() {
    return "(" + f1 + ")/(" + f2 + ")";
  }

}
