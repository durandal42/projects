import java.awt.Canvas;
import java.awt.Color;
import java.awt.Frame;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;
import java.util.*;

public abstract class Renderer extends Canvas {

  int imageX = 600;
  int imageY = 600;
  double viewMinX = -2.0;
  double viewMaxX = 2.0;
  double viewMinY = -2.0;
  double viewMaxY = 2.0;

  static void log(String msg) {
    System.out.println(msg);
  }

  void recenter(double x, double y) {
    double dx = (viewMaxX - viewMinX) * 0.5;
    double dy = (viewMaxY - viewMinY) * 0.5;
    viewMinX = x - dx;
    viewMaxX = x + dx;
    viewMinY = y - dy;
    viewMaxY = y + dy;
  }

  void zoom(double scale) {
    double cx = (viewMaxX + viewMinX) * 0.5;
    double cy = (viewMaxY + viewMinY) * 0.5;
    viewMinX = cx - (cx - viewMinX) * scale;
    viewMaxX = cx - (cx - viewMaxX) * scale;
    viewMinY = cy - (cy - viewMinY) * scale;
    viewMaxY = cy - (cy - viewMaxY) * scale;
  }

  public void output(String label) {
    compute();

    int gridThreshold = 2;
    log("Creating image buffer...");
    BufferedImage image = new BufferedImage(imageX, imageY,
                                            BufferedImage.TYPE_INT_RGB);
    log("Painting...");
    paint(image.getGraphics());
    String format = "png";
    String fileName = "../images/" + label + "_" + imageX + "x" + imageY + "." + format;;
    log("Saving to disk as " + fileName + " ...");
    try {
      ImageIO.write(image, format, new File(fileName));
    } catch (IOException e) {
      log("ERROR: failed to output to file.");
    }
  }

  Map<Complex, Double> computed = new HashMap<>();
  Histogram<Double> normalizer = new Histogram<>();
  public void compute() {
    log("Computing " + imageX * imageY + " pixels from view:");
    log("\tx: [" + viewMinX + " " + viewMaxX + "]");
    log("\ty: [" + viewMinY + " " + viewMaxY + "]");
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

    log("normalizing...");
    normalizer.done();
  }

  public void paint(Graphics g) {
    log("Painting " + imageX * imageY + " pixels from view:");
    log("\tx: [" + viewMinX + " " + viewMaxX + "]");
    log("\ty: [" + viewMinY + " " + viewMaxY + "]");

    g.setColor(Color.green);
    g.fillRect(0, 0, imageX, imageY);

    double scaleX = (viewMaxX - viewMinX) / (double) imageX;
    double scaleY = (viewMaxY - viewMinY) / (double) imageY;

    for (int x = 0; x < imageX ; x++) {
      for (int y = 0; y < imageY ; y++) {
        double r = scaleX * (double) x + viewMinX;
        double i = scaleY * (double) y + viewMinY;

        g.setColor(pickColor(r, i));
        g.drawLine(x, y, x, y);
      }
    }
  }

  public abstract Color pickColor(double r, double i);

}
