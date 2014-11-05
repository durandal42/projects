import java.awt.*;
import java.awt.event.*;

class VoltorbGuiControl extends Container implements KeyListener {

    TextField levelField = new TextField("1");

    VoltorbGui owner;

  VoltorbGuiControl(VoltorbGui owner) {
      this.owner = owner;

      setLayout(new GridLayout(2, 1));
      Button b = new Button("Calculate!");
      b.addActionListener(owner);
      add(b);

      Container levelContainer = new Container();
      levelContainer.setLayout(new GridLayout(1,2));
      levelContainer.add(new Label("Level:"));
      levelField.addActionListener(owner);
      levelField.addKeyListener(this);
      levelContainer.add(levelField);

      add(levelContainer);
  }

    public void keyPressed(KeyEvent e) {}
    public void keyReleased(KeyEvent e) {}
    public void keyTyped(KeyEvent e) {
	owner.recalculate();
    }


}