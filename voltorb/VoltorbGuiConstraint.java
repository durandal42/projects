import java.awt.*;
import java.awt.event.*;

class VoltorbGuiConstraint extends Container implements KeyListener {
  TextField coinField;
  TextField orbField;

  VoltorbGui owner;

  VoltorbGuiConstraint(GroupConstraint gc, VoltorbGui owner) {
    this.owner = owner;

    coinField = new TextField("" + gc.coins);
    orbField = new TextField("" + gc.orbs);

    coinField.addActionListener(owner);
    orbField.addActionListener(owner);

    coinField.addKeyListener(this);
    orbField.addKeyListener(this);

    setLayout(new GridLayout(2, 2));
    add(new Label("coins"));
    add(coinField);
    add(new Label("orbs"));
    add(orbField);
  }

  GroupConstraint getConstraint() {
    int coins = -1;
    int orbs = -1;
    try {
      coins = Integer.parseInt(coinField.getText());
      coinField.setBackground(Color.gray);
    } catch (NumberFormatException e) {
      coinField.setBackground(Color.red);
    }
    try {
      orbs = Integer.parseInt(orbField.getText());
      orbField.setBackground(Color.gray);
    } catch (NumberFormatException e) {
      orbField.setBackground(Color.red);
    }
    if (coins == -1 || orbs == -1) {
      return null;
    }
    return new GroupConstraint(coins, orbs);
  }

  void setEditable(boolean yes) {
    coinField.setEditable(yes);
    orbField.setEditable(yes);
    coinField.setFocusable(yes);
    orbField.setFocusable(yes);
  }

  void reset() {
    coinField.setText("");
    orbField.setText("");
    setEditable(true);
  }


  VoltorbGuiConstraint nextConstraint = null;
  void setNextConstraint(VoltorbGuiConstraint c) {
      nextConstraint = c;
  }
  public void keyTyped(KeyEvent e) {
    if (e.getSource() == orbField) {
      switch(e.getKeyChar()) {
      case '0':
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
        if (nextConstraint != null) {
          nextConstraint.coinField.requestFocus();
        } else {
          owner.control.levelField.requestFocus();
        }
      }
    }
    if (e.getSource() == coinField) {
      switch (e.getKeyChar()) {
      case '1':
      case '2':
      case '3':
        if (coinField.getText().length() == 2) {
            orbField.requestFocus();
            break;
        }
      case '4':
      case '5':
      case '6':
      case '7':
      case '8':
      case '9':
        if (coinField.getText().length() == 2) {
          orbField.setText(coinField.getText().substring(1,2));
          coinField.setText(coinField.getText().substring(0,1));
          if (nextConstraint != null) {
            nextConstraint.coinField.requestFocus();
          } else {
            owner.control.levelField.requestFocus();
          }
        } else if (e.getKeyChar() != '1') {
          orbField.requestFocus();
        }
        break;
      case '0':
        orbField.requestFocus();
        break;
      }
    }
  }
  public void keyPressed(KeyEvent e) {}
  public void keyReleased(KeyEvent e) {}

}
