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

public class RenderDemo
  extends Canvas
  implements Runnable, MouseListener {

  Renderer renderer = new MandelbrotRenderer();

  BufferedImage bi;
  public void run() {
    bi =  new BufferedImage(renderer.imageX, renderer.imageY,
                            BufferedImage.TYPE_INT_RGB);
    while (true) {
      renderer.compute();
      renderer.paint(bi.getGraphics());
      paint(getGraphics());
      try {
        synchronized (bi) {
          bi.wait();
        }
      } catch (InterruptedException e) {

      }
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

    double scaleX = (renderer.viewMaxX - renderer.viewMinX) / (double) renderer.imageX;
    double scaleY = (renderer.viewMaxY - renderer.viewMinY) / (double) renderer.imageY;

    double r = scaleX * (double) x + renderer.viewMinX;
    double i = scaleY * (double) y + renderer.viewMinY;

    log("Coordinates: " + r + ", " + i);

    renderer.recenter(r, i);
    renderer.zoom(0.5);
    synchronized (bi) {
      bi.notify();
    }

    repaint();
  }

  public static void main(String[] args) {
    Frame f = new Frame("Mandelbrot");
    RenderDemo n = new RenderDemo();
    f.setSize(n.renderer.imageX, n.renderer.imageY);
    new Thread(n).start();
    n.addMouseListener(n);
    f.add(n);
    f.setVisible(true);
  }

  static void log(String msg) {
    System.out.println(msg);
  }
  public void paint(Graphics g) {
    g.drawImage(bi, 0, 0, null);
  }
}
