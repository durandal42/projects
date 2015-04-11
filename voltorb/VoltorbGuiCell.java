import java.awt.*;
import java.awt.event.*;

class VoltorbGuiCell extends Container implements KeyListener {
  Label suggest = new Label("----");
  TextField valueField = new TextField();
  VoltorbGuiScore scoreCanvas = new VoltorbGuiScore(this);
  Label[] scores = new Label[4];

  VoltorbGuiCell[][] neighbors;
  VoltorbGui owner;

  private static final Insets insets =
    new Insets(10,10,10,10);
  public Insets getInsets() { return insets; }
  public void paint(Graphics g) {
    Dimension size = getSize();
    g.setColor(getBackground());
    g.draw3DRect(5, 5,
           size.width - 11, size.height - 11, true);
    super.paint(g);
  }

  VoltorbGuiCell(VoltorbGuiCell[][] neighbors, VoltorbGui owner) {
    this.neighbors = neighbors;
    this.owner = owner;

    Container valueContainer = new Container();
    valueContainer.setLayout(new GridLayout(1, 2));
    valueContainer.add(suggest);
    valueContainer.add(valueField);

    setLayout(new GridLayout(2, 1));
    add(valueContainer);
    add(scoreCanvas);

    valueField.addActionListener(owner);
    valueField.addKeyListener(this);

    setEditable(false);
  }

  void setEditable(boolean yes) {
    valueField.setEditable(yes);
    valueField.setFocusable(yes);
  }

  boolean hasValue() {
    try {
      getValue();
      return true;
    } catch (NumberFormatException e) {
      return false;
    }
  }

  int getValue() {
    return Integer.parseInt(valueField.getText());
  }

  static java.text.DecimalFormat df = new java.text.DecimalFormat("0.00");
  void displayHistogram(Histogram hist) {
    scoreCanvas.updateScore(hist);
  }
  void displayScore(double score) {
    suggest.setText(df.format(score));
  }
  void clearScore() {
    suggest.setText("----");
  }

  void reset() {
    displayHistogram(null);
    clearScore();
    valueField.setText("");
    setEditable(false);
  }

  void setRecommended(Color c) {
    suggest.setBackground(c);
  }

  public void keyTyped(KeyEvent e) {
  }
  public void keyReleased(KeyEvent e) {
    switch(e.getKeyChar()) {
    case '0':
    case '1':
    case '2':
    case '3':
      owner.recalculate();
      break;
    default:
      break;
    }    
  }
  public void keyPressed(KeyEvent e) {
    int dx = 0;
    int dy = 0;
    switch(e.getKeyCode()) {
    case KeyEvent.VK_KP_LEFT:
    case KeyEvent.VK_LEFT:
      dy = -1;
      break;
    case KeyEvent.VK_KP_RIGHT:
    case KeyEvent.VK_RIGHT:
      dy = 1;
      break;
    case KeyEvent.VK_KP_UP:
    case KeyEvent.VK_UP:
      dx = -1;
      break;
    case KeyEvent.VK_KP_DOWN:
    case KeyEvent.VK_DOWN:
      dx = 1;
      break;
    default:
      break;
    }
    if (dx != 0 || dy != 0) {
      int x = 0;
      int y = 0;
      search:
      for(int i = 0; i < 5; i++) {
        for(int j = 0; j < 5; j++) {
          if (neighbors[i][j] == this) {
            x = i;
            y = j;
            break search;
          }
        }
      }
      x = (x + dx + 5) % 5;
      y = (y + dy + 5) % 5;
      neighbors[x][y].valueField.requestFocus();
    }
  }
}
