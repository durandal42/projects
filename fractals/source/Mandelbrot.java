import java.awt.Canvas;
import java.awt.Color;
import java.awt.Frame;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

public class Mandelbrot
    extends Canvas
    implements Runnable, MouseListener {

  public static final double THRESHOLD = 2.0;
  public static final int MAX_STEPS = 60;

  static int imageX = 800;
  static int imageY = 800;
  double viewMinX = -2.0;
  double viewMaxX = 1.0;
  double viewMinY = -1.5;
  double viewMaxY = 1.5;

  void recenter(double x, double y) {
    double dx = (viewMaxX - viewMinX) * 0.5;
    double dy = (viewMaxY - viewMinY) * 0.5;
    viewMinX = x - dx;
    viewMaxX = x + dx;
    viewMinY = y - dy;
    viewMaxY = y + dy;
    updateNeeded = true;
  }

  void zoom(double scale) {
    double cx = (viewMaxX + viewMinX) * 0.5;
    double cy = (viewMaxY + viewMinY) * 0.5;
    viewMinX = cx - (cx - viewMinX) * scale;
    viewMaxX = cx - (cx - viewMaxX) * scale;
    viewMinY = cy - (cy - viewMinY) * scale;
    viewMaxY = cy - (cy - viewMaxY) * scale;
    updateNeeded = true;
  }

  public static boolean escaped(Complex c) {
    return Complex.abs(c) > THRESHOLD;
  }

  public static int mandel(Complex seed) {
    int i = 0;
    Complex c = seed;
    while(!escaped(c) && i < MAX_STEPS) {
      c = Complex.add(Complex.multiply(c, c),
                      seed);
      i++;
    }
    return i;
  }

  BufferedImage bi;
  boolean updateNeeded = true;
  public void run() {
    bi =  new BufferedImage(imageX, imageY,
                            BufferedImage.TYPE_INT_RGB);
    while (true) {
      while (!updateNeeded) {
        paint(getGraphics());
        Thread.yield();
      }
      updateNeeded = false;
      draw(bi.getGraphics());
    }
  }

  public void mouseExited(MouseEvent e) {}
  public void mouseEntered(MouseEvent e) {}
  public void mousePressed(MouseEvent e) {}
  public void mouseReleased(MouseEvent e) {}
  public void mouseClicked(MouseEvent e) {
    int x = e.getX();
    int y = e.getY();
    log("Click detected at " + x + ", " + y);

    double scaleX = (viewMaxX - viewMinX) / (double) imageX;
    double scaleY = (viewMaxY - viewMinY) / (double) imageY;

    double r = scaleX * (double) x + viewMinX;
    double i = scaleY * (double) y + viewMinY;

    log("Coordinates: " + r + ", " + i);

    recenter(r,i);
    zoom(0.5);

    repaint();
  }

  public static void main(String[] args) {
    Frame f = new Frame("Mandelbrot");
    f.setSize(imageX, imageY);
    Mandelbrot n = new Mandelbrot();
    new Thread(n).start();
    n.addMouseListener(n);
    f.add(n);
    f.setVisible(true);
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
    draw(image.getGraphics());
    log("Saving to disk...");
    try {
      ImageIO.write(image, "png", new File("output.png"));
    } catch (IOException e) {
      log("ERROR: failed to output to file.");
    }
  }

  public void paint(Graphics g) {
    g.drawImage(bi, 0, 0, null);
  }

  public void draw(Graphics g) {
    log("Painting " + imageX*imageY + " pixels from view:");
    log("\tx: [" + viewMinX + " " + viewMaxX + "]");
    log("\ty: [" + viewMinY + " " + viewMaxY + "]");

    //	g.setColor(Color.green);
    //	g.fillRect(0,0,imageX,imageY);

    double scaleX = (viewMaxX - viewMinX) / (double) imageX;
    double scaleY = (viewMaxY - viewMinY) / (double) imageY;

    for (int x = 0; x < imageX ; x++) {
      for (int y = 0; y < imageY ; y++) {
        double r = scaleX * (double) x + viewMinX;
        double i = scaleY * (double) y + viewMinY;

        Complex c = new Complex(r, i);
        int steps = mandel(c);

        double stepScale = 1.0 - Math.sqrt(steps / (double) MAX_STEPS);

        float h = (float) 1.0;
        float s = (float) 1.0;
        float b = (float) stepScale;

        g.setColor(Color.getHSBColor(h, s, b));
        g.drawLine(x, y, x, y);
      }
    }
    log("... done.");
  }
}
