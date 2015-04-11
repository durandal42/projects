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
    int barWidth = width / (VoltorbBoard.MAX_MULTIPLIER + 1);
    for(int i = 0; i <= VoltorbBoard.MAX_MULTIPLIER; i++) {
      g.setColor(colors[i]);
      double fraction = latestScore.getProbability(i);
      g.fillRect(i * barWidth, height - (int) (fraction * height),
                 barWidth, (int) (fraction * height));
    }
  }

  public void mouseClicked(MouseEvent e) {
    int x = e.getX();
    int y = e.getY();
    owner.valueField.setText("" + ((VoltorbBoard.MAX_MULTIPLIER + 1) * x / getWidth()));
    owner.owner.recalculate();
  }
  public void mouseEntered(MouseEvent e) {}
  public void mouseExited(MouseEvent e) {}
  public void mousePressed(MouseEvent e) {}
  public void mouseReleased(MouseEvent e) {}
}