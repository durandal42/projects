// Newton's method for finding zeros of a function.
// Given a guess, find the slope of the function at that point,
// and find where that line hits zero.
// That's the new guess; iterate until we're close enough.

public class Newton {

  // How close to get to zero before it's good enough.
  public static final double MARGIN = 0.0001;

  // How many steps we should take before giving up.
  public static final int MAX_STEPS = 60;

  public static Result newton(Complex guess, Function f, Function fPrime) {
    int i = 0;
    while(!closeEnough(guess, f) && i < MAX_STEPS) {
      guess = iterate(guess, f, fPrime);
      i++;
    }
    return new Result(guess, i);
  }

  // Given a function, its derivative, and a guess, compute the next guess.
  public static Complex iterate(Complex guess, Function f, Function fPrime) {
    return Complex.subtract(guess,
                            Complex.divide(f.apply(guess),
                                           fPrime.apply(guess)));
  }

  // Is this guess close enough to a zero?
  public static boolean closeEnough(Complex guess, Function f) {
    return Complex.abs(f.apply(guess)) < MARGIN;
  }

  // Annotated Complex number, also includes how many steps it took to converge
  // to this number.
  public static class Result {
    public int steps;
    public Complex solution;

    public Result(Complex c, int s) {
      steps = s;
      solution = c;
    }
  }

}
