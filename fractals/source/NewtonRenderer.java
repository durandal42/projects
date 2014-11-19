import java.awt.Canvas;
import java.awt.Color;
import java.awt.Frame;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

public class NewtonRenderer extends Canvas {

  int imageX = 600;
  int imageY = 600;
  double viewMinX = -2.0;
  double viewMaxX = 2.0;
  double viewMinY = -2.0;
  double viewMaxY = 2.0;

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
    n.output();
  }

  static void log(String msg) {
    System.out.println(msg);
  }

  public void output() {
    int gridThreshold = 2;
    log("Creating image buffer...");
    BufferedImage image = new BufferedImage(imageX, imageY,
                                            BufferedImage.TYPE_INT_RGB);
    log("Painting...");
    paint(image.getGraphics());
    log("Saving to disk...");
    try {
      ImageIO.write(image, "png", new File("output.png"));
    } catch (IOException e) {
      log("ERROR: failed to output to file.");
    }
  }

  Function function;
  Function derivative;
  public NewtonRenderer(Function func) {
    function = func;
    derivative = func.differentiate();
  }

  public void paint(Graphics g) {
    log("Painting " + imageX*imageY + " pixels from view:");
    log("\tx: [" + viewMinX + " " + viewMaxX + "]");
    log("\ty: [" + viewMinY + " " + viewMaxY + "]");

    g.setColor(Color.green);
    g.fillRect(0,0,imageX,imageY);

    double scaleX = (viewMaxX - viewMinX) / (double) imageX;
    double scaleY = (viewMaxY - viewMinY) / (double) imageY;

    for (int x = 0; x < imageX ; x++) {
      for (int y = 0; y < imageY ; y++) {
        double r = scaleX * (double) x + viewMinX;
        double i = scaleY * (double) y + viewMinY;

        Complex guess = new Complex(r, i);
        Newton.Result nr = Newton.newton(guess, function, derivative);

        double stepScale = 1.0 - Math.sqrt(nr.steps / (double) Newton.MAX_STEPS);

        double angle = Complex.angle(nr.solution);
        double degrees = Math.round(Math.toDegrees(angle));

        float h = (float) (degrees / 360.0);
        float s = (float) 1.0;
        float b = (float) stepScale;

        g.setColor(Color.getHSBColor(h, s, b));
        g.drawLine(x, y, x, y);
      }
    }
  }
}
