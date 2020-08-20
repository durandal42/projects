import java.awt.Color;
import java.util.*;

public class MandelbrotRenderer extends Renderer {

  public static void main(String[] args) {
    MandelbrotRenderer n = new MandelbrotRenderer();

    // Check for command-line args to change the render size.
    try {
      if (args.length >= 2) {
        n.imageX = Integer.parseInt(args[0]);
        n.imageY = Integer.parseInt(args[1]);
      }
    } catch (NumberFormatException e) {
      // use defaults
    }

    n.viewMinX = -2.25;
    n.viewMaxX = 0.75;
    n.viewMinY = -1.5;
    n.viewMaxY = 1.5;

    n.compute();
    // Render!
    n.output("mandelbrot");
  }

  public MandelbrotRenderer() {
  }

  Map<Complex, Double> computed = new HashMap<>();
  Histogram<Double> normalizer = new Histogram<>();
  public void compute() {
      Timer t = new Timer("Computing " + imageX * imageY + " pixels from view:" +
			  "\tx: [" + viewMinX + " " + viewMaxX + "]" +
			  "\ty: [" + viewMinY + " " + viewMaxY + "]");
    normalizer.clear();

    double scaleX = (viewMaxX - viewMinX) / (double) imageX;
    double scaleY = (viewMaxY - viewMinY) / (double) imageY;

    
    for (int x = 0; x < imageX ; x++) {
      for (int y = 0; y < imageY ; y++) {
        double r = scaleX * (double) x + viewMinX;
        double i = scaleY * (double) y + viewMinY;
        Complex c = new Complex(r, i);
        // log("prepainted: " + c);
        double smooth = Mandelbrot.smoothMandel(new Complex(r, i));
        computed.put(c, smooth);
        if (smooth < 1.0) {
          normalizer.add(smooth);
        }
      }
    }
    log("computed " + computed.size() + " pixels.");
    t.Stop();

    t = new Timer("normalizing...");
    normalizer.done();
    t.Stop();
  }

  static Color[] wikipedia = new Color[] {
    new Color(66, 30, 15),
    new Color(25, 7, 26),
    new Color(9, 1, 47),
    new Color(4, 4, 73),
    new Color(0, 7, 100),
    new Color(12, 44, 138),
    new Color(24, 82, 177),
    new Color(57, 125, 209),
    new Color(134, 181, 229),
    new Color(211, 236, 248),
    new Color(241, 233, 191),
    new Color(248, 201, 95),
    new Color(255, 170, 0),
    new Color(204, 128, 0),
    new Color(153, 87, 0),
    new Color(106, 52, 3),
  };

  public Color pickColor(double r, double i) {
    Complex c = new Complex(r, i);
    // log("painting: " + c);
    double smooth = computed.get(c);
    if (smooth >= 1.0) return Color.BLACK;
    smooth = normalizer.normalize(smooth);

    // Black & White
    // return Color.WHITE;

    // Greyscale
    //      return Color.getHSBColor(0, 0, 1.0f - (float) smooth);

    // Rainbow
    return Color.getHSBColor((float) smooth, 1, 1);

    // Wikipedia
    // TODO: requires interpolation
    //      return wikipedia[steps % wikipedia.length];
  }
}
