import java.awt.Canvas;
import java.awt.Color;
import java.awt.Frame;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

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

        g.setColor(pickColor(r, i));
        g.drawLine(x, y, x, y);
      }
    }
  }

  public abstract Color pickColor(double r, double i);

}
