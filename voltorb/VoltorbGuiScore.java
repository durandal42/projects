import java.awt.*;
import java.awt.event.*;

class VoltorbGuiScore extends Canvas implements MouseListener {

  VoltorbGuiCell owner;

  VoltorbGuiScore(VoltorbGuiCell owner) {
    this.owner = owner;
    addMouseListener(this);
  }

  Histogram latestScore = null;
  void updateScore(Histogram h) {
    latestScore = h;
    paint(getGraphics());
  }

  static Color[] colors = new Color[] { Color.red, Color.yellow, Color.green, Color.blue };

  public void paint(Graphics g) {
    int width = getWidth();
    int height = getHeight();
    g.setColor(Color.white);
    g.fillRect(0, 0, width, height);
    if (latestScore == null) {
      return;
    }
    for(int i = 0; i < 4; i++) {
      g.setColor(colors[i]);
      double fraction = latestScore.getProbability(i);
      g.fillRect(i * width / 4, height - (int) (fraction * height),
                 width / 4, (int) (fraction * height));
    }
  }

  public void mouseClicked(MouseEvent e) {
    int x = e.getX();
    int y = e.getY();
    owner.valueField.setText("" + (4 * x / getWidth()));
    owner.owner.recalculate();
  }
  public void mouseEntered(MouseEvent e) {}
  public void mouseExited(MouseEvent e) {}
  public void mousePressed(MouseEvent e) {}
  public void mouseReleased(MouseEvent e) {}
}