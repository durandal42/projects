public class Mandelbrot {

  public static final double THRESHOLD = 1 << 16;
  public static final int MAX_STEPS = 60;

  public static boolean escaped(Complex c) {
    return Complex.abs(c) > THRESHOLD;
  }

  public static int mandel(Complex seed) {
    int i = 0;
    Complex c = seed;
    while (!escaped(c) && i < MAX_STEPS) {
      c = Complex.add(Complex.multiply(c, c),
                      seed);
      i++;
    }
    return i;
  }

  public static double smoothMandel(Complex seed) {
    int n = 0;
    Complex zn = seed;
    while (!escaped(zn) && n < MAX_STEPS) {
      zn = Complex.add(Complex.multiply(zn, zn),
                       seed);
      n++;
    }
    if (!escaped(zn)) return 1.0;
    return (n + 1 - Math.log(Math.log(Complex.abs(zn))) / Math.log(2)) / (double) MAX_STEPS;
  }
}
