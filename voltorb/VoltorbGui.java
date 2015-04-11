import java.util.*;
import java.awt.*;
import java.awt.event.*;
import java.util.concurrent.*;

public class VoltorbGui extends Container implements ActionListener {

  VoltorbGuiCell[][] cells = new VoltorbGuiCell[VoltorbBoard.SIZE][VoltorbBoard.SIZE];
  VoltorbGuiConstraint[] rows = new VoltorbGuiConstraint[VoltorbBoard.SIZE];
  VoltorbGuiConstraint[] cols = new VoltorbGuiConstraint[VoltorbBoard.SIZE];
    VoltorbGuiControl control = new VoltorbGuiControl(this);

  public void actionPerformed(ActionEvent e) {
      recalculate();
  }

    int lastSize = -1;
  void recalculate() {
      int level = Integer.parseInt(control.levelField.getText());

    java.util.List<GroupConstraint> rowConstraints =
        new ArrayList<GroupConstraint>(VoltorbBoard.SIZE);
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      rowConstraints.add(rows[i].getConstraint());
    }
    java.util.List<GroupConstraint> colConstraints =
        new ArrayList<GroupConstraint>(VoltorbBoard.SIZE);
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      colConstraints.add(cols[i].getConstraint());
    }

    Map<Probe,Integer> discoveries = new HashMap<Probe,Integer>();
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
        for(int j = 0; j < VoltorbBoard.SIZE; j++) {
            if (cells[i][j].hasValue()) {
                discoveries.put(new Probe(i, j), cells[i][j].getValue());
            }
        }
    }

    java.util.List<VoltorbBoard> possible =
        VoltorbAssistant.fromConstraints(rowConstraints,
                                         colConstraints,
                                         discoveries);
    VoltorbAssistant.filterByLevel(level, possible);

    if (lastSize != -1) {
        if (possible.size() * 10 <= lastSize) {
            System.out.println("Was that what you were expecting?!");
        }
    } else {
        System.out.println("Calculating possibilities for a new set of constraints...");
    }
    lastSize = possible.size();

    if (possible.size() > 0) {
      for(int i = 0; i < VoltorbBoard.SIZE; i++) {
        for(int j = 0; j < VoltorbBoard.SIZE; j++) {
          cells[i][j].setEditable(true);
        }
        rows[i].setEditable(false);
        cols[i].setEditable(false);
      }
    }
    System.out.println("Possible boards: " + possible.size());

    Map<Probe,Histogram> histo = VoltorbAssistant.histo(possible);
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      for(int j = 0; j < VoltorbBoard.SIZE; j++) {
        VoltorbGuiCell vc = cells[i][j];
        Histogram h = histo.get(new Probe(i,j));
        vc.displayHistogram(h);
        vc.clearScore();
      }
    }

    if (discoveries.size() == level) {
        System.out.println("Current level is covered; now gunning for points...");
    }

    threadedStrategic(possible, level, discoveries);
  }

    static ExecutorService threadPool = Executors.newCachedThreadPool();
    Future strategicFuture = null;
    void threadedStrategic(final java.util.List<VoltorbBoard> possible,
                           final int level,
                           final Map<Probe,Integer> discoveries) {
        if (strategicFuture != null && strategicFuture.cancel(true)) {
            System.out.println("(cancelled previously running computation)");
        }
        //        System.out.println("Evaluating best strategic option; this may take a while...");
        strategicFuture = threadPool.submit(new Runnable() {
                public void run() {
                    strategic(possible, level, discoveries);
                }
            });
    }

  void strategic(java.util.List<VoltorbBoard> possible, int level, Map<Probe,Integer> discoveries) {
    Evaluation eval = VoltorbAssistant.bestProbe(possible, level, discoveries, 1.0);
    if (eval == null || eval.bestProbe == null) {
        // We've won!
        System.out.println("board is solved! all remaining multipliers are known.");
        return;
    }

    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      for(int j = 0; j < VoltorbBoard.SIZE; j++) {
        VoltorbGuiCell vc = cells[i][j];
        Probe p = new Probe(i, j);
        if (eval.scores.containsKey(p)) {
            vc.displayScore(eval.scores.get(p));
        }
      }
    }
    VoltorbGuiCell bestCell = cells[eval.bestProbe.row][eval.bestProbe.col];
    bestCell.valueField.requestFocus();

    //    System.out.println("... best strategic play found!");
  }

  public void Init() {
    // VoltorbBoard vb = VoltorbBoard.random();
    // java.util.List<GroupConstraint> rowConstraints = vb.constraints(true);
    // java.util.List<GroupConstraint> colConstraints = vb.constraints(false);

    setLayout(new GridLayout(VoltorbBoard.SIZE + 1, VoltorbBoard.SIZE + 1));
    VoltorbGuiConstraint prev = null;
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      for(int j = 0; j < VoltorbBoard.SIZE; j++) {
        VoltorbGuiCell vc = new VoltorbGuiCell(cells, this);
        cells[i][j] = vc;
        add(vc);
      }
      VoltorbGuiConstraint cc = new VoltorbGuiConstraint(new GroupConstraint(0,0), this);
      if (prev != null) prev.setNextConstraint(cc);
      prev = cc;
      rows[i] = cc;
      add(cc);
    }
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      VoltorbGuiConstraint cc = new VoltorbGuiConstraint(new GroupConstraint(0,0), this);
      if (prev != null) prev.setNextConstraint(cc);
      prev = cc;
      cols[i] = cc;
      add(cc);
    }
    add(control);
  }

  public static void main(String[] args) {
    VoltorbGui vg = new VoltorbGui();
    vg.Init();

    final Frame frame = new Frame("Voltorb Flip Assistant");
    frame.add("Center", vg);
    frame.pack();
    frame.setSize(new Dimension(800, 600));
    frame.addWindowListener(new WindowListener() {
        public void windowDeactivated(WindowEvent we) {}
        public void windowActivated(WindowEvent we) {}
        public void windowDeiconified(WindowEvent we) {}
        public void windowIconified(WindowEvent we) {}
        public void windowClosed(WindowEvent we) {}
        public void windowClosing(WindowEvent we) {
            frame.setVisible(false);
            VoltorbGui vg = new VoltorbGui();
            vg.Init();
            frame.removeAll();
            frame.add("Center", vg);
            frame.pack();
            frame.setSize(new Dimension(800, 600));
            frame.setVisible(true);
        }
        public void windowOpened(WindowEvent we) {}
      });
    frame.setVisible(true);
  }

}
