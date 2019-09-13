import java.awt.Color;

public class NewtonRenderer extends Renderer {

  public static void main(String[] args) {
    // f(x) = x^5 - 1
    Function x5m1 = new Sum(new Power(Identity.IDENTITY,
                                      new Complex(5.0, 0.0)),
                            new Constant(new Complex(-1.0, 0.0)));

    // unused functions    
    // f(x) = x^7 - 1
    Function x7m1 = new Sum(new Power(Identity.IDENTITY,
                                      new Complex(7.0, 0.0)),
                            new Constant(new Complex(-1.0, 0.0)));
    // f(x) = 2^x - x^2
    Function foo = new Sum(new Exp(new Complex(2.0, 0.0),
                                   Identity.IDENTITY),
                           new Product(new Power(Identity.IDENTITY,
                                                 new Complex(2.0, 0.0)),
                                       new Constant(new Complex(-1.0, 0.0))));
    // f(x) = log(x)
    Function log = new Log(new Complex(Math.E, 0.0),
                           Identity.IDENTITY);

    // Create a fractal renderer using a specific function:
    NewtonRenderer n = new NewtonRenderer(x5m1);

    // Check for command-line args to change the render size.
    try {
      if (args.length >= 2) {
        int x = Integer.parseInt(args[0]);
        int y = Integer.parseInt(args[1]);
        n.imageX = x;
        n.imageY = y;
      }
    } catch (NumberFormatException e) {
      // use defaults
    }

    // Render!
    n.output("newton_x5m1");
  }

  Function function;
  Function derivative;
  public NewtonRenderer(Function func) {
    function = func;
    derivative = func.differentiate();
  }

  public Color pickColor(double r, double i) {
    Complex guess = new Complex(r, i);
    Newton.Result nr = Newton.newton(guess, function, derivative);

    double stepScale = 1.0 - Math.sqrt(nr.steps / (double) Newton.MAX_STEPS);

    double angle = Complex.angle(nr.solution);
    double degrees = Math.round(Math.toDegrees(angle));

    float h = (float) (degrees / 360.0);
    float s = (float) 1.0;
    float b = (float) stepScale;

    return Color.getHSBColor(h, s, b);
  }
}
