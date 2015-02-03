import java.util.*;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.*;
import javax.imageio.ImageIO;

public class Maze {

  private class Cell {
    public final int x, y;
    private List<Cell> walls = new LinkedList<Cell>();

    public Cell(int x, int y) { this.x = x; this.y = y; }

    // Adds another cell as a neighbor of this cell, and vice versa.
    // Returns true this neighbor was newly added.
    boolean addNeighbor(Cell c) {
      if (walls.contains(c)) return false;
      walls.add(c);
      c.addNeighbor(this);
      return true;
    }

    // Removes another cell as a neighbor of this cell, and vice versa.
    // Returns true this neighbor was newly removed.
    boolean removeNeighbor(Cell c) {
      if (!walls.contains(c)) return false;
      walls.remove(c);
      c.removeNeighbor(this);
      return true;
    }
  }

  private class Wall {
    Cell c1, c2;

    public Wall(Cell cell1, Cell cell2) { c1 = cell1; c2 = cell2; }

    public int hashCode() {
      return c1.hashCode() * c2.hashCode();
    }

    public boolean equals(Object other) {
      Wall w = (Wall) other;
      return (c1.equals(w.c1) && c2.equals(w.c2)) ||
          (c1.equals(w.c2) && c2.equals(w.c1));
    }
  }

  List<Cell> cells;
  List<Wall> walls;

  public void initRect(int x, int y) {
    cells = new ArrayList<Cell>(x * y);
    walls = new ArrayList<Wall>(x * y * 2);

    Timer t = new Timer("initializing and linking cells");
    Cell[] temp1 = new Cell[0];
    Cell[] temp2 = new Cell[0];
    for(int i = 0 ; i < x ; i++) {
	    temp1 = new Cell[y];
	    for(int j = 0 ; j < y ; j++) {
        temp1[j] = new Cell(i, j);
        cells.add(temp1[j]);

        if (i > 0) {
          temp1[j].addNeighbor(temp2[j]);
          walls.add(new Wall(temp1[j], temp2[j]));
        }
        if (j > 0) {
          temp1[j].addNeighbor(temp1[j-1]);
          walls.add(new Wall(temp1[j], temp1[j-1]));
        }
	    }
	    temp2 = temp1;
    }
    t.Stop();
  }

  public void create() {
    createWilson();
    //createKruskal();
  }

  public void createWilson() {
    int stepsTaken = 0;
    int stepsUnwound = 0;
    Timer t = new Timer("random walking");

    Random r = new Random();

    Collection<Cell> todo = new HashSet<Cell>();
    todo.addAll(cells);

    Set<Cell> maze = new HashSet<Cell>();
    Iterator<Cell> it = todo.iterator();
    maze.add(it.next());
    it.remove();

    while (!todo.isEmpty()) {
      LinkedList<Cell> stack = new LinkedList<Cell>();
      Set<Cell> walked = new HashSet<Cell>();
      it = todo.iterator();
      Cell c = it.next();
      it.remove();
      stack.add(c);
      walked.add(c);

      while (!maze.contains(c)) {
        c = c.walls.get(r.nextInt(c.walls.size()));  stepsTaken++;
        while (walked.contains(c)) {
          walked.remove(stack.removeLast());  stepsUnwound++;
        }
        stack.add(c);
        walked.add(c);
      }

      while (stack.size() > 1) {
        Cell ultimate = stack.removeLast();
        Cell penultimate = stack.getLast();
        ultimate.removeNeighbor(penultimate);
        todo.remove(penultimate);
        maze.add(penultimate);
      }
    }

    t.Stop();
    System.out.println("Steps taken:\t" + stepsTaken);
    System.out.println("Steps unwound:\t" + stepsUnwound);
  }


  public void createKruskal() {
    Timer t = new Timer("knocking down walls");

    int numAreas = cells.size();
    UnionFind uf = new UnionFind();
    Collections.shuffle(walls);

    for (Wall w : walls) {
	    Cell c1 = w.c1;
	    Cell c2 = w.c2;

	    if (uf.equals(c1, c2)) { continue; }

	    uf.union(c1, c2);
	    c1.removeNeighbor(c2);

	    if (--numAreas == 0) break;
    }

    t.Stop();
  }

  public void outputText(String fileName, int xDim, int yDim) throws IOException {
    Timer t = new Timer("writing to text file: " + fileName);
    BufferedWriter bw = new BufferedWriter(new FileWriter(fileName + ".txt"));

    StringBuffer result = new StringBuffer();

    {
      // Draw a template, with no walls.
      StringBuffer border = new StringBuffer("1");
      for(int i = xDim ; i > 0 ; i--) {
        border.append("11");
      }
      border.append('\n');

      StringBuffer hallway = new StringBuffer("1");
      for(int i = xDim-1 ; i > 0 ; i--) {
        hallway.append("00");
      }
      hallway.append("01\n");

      StringBuffer columns = new StringBuffer("1");
      for(int i = xDim-1 ; i > 0 ; i--) {
        columns.append("01");
      }
      columns.append("01\n");

      result.append(border);
      for(int j = yDim-1 ; j > 0 ; j--) {
        result.append(hallway);
        result.append(columns);
      }
      result.append(hallway);
      result.append(border);
    }

    // Fill in walls.
    int initOffset = 2*xDim + 3;
    int rowOffset = 2*xDim + 2;
    for(Cell c1 : cells) {
	    for(Cell c2 : c1.walls) {
        int setX = c1.x + c2.x;
        int setY = c1.y + c2.y;
        result.setCharAt(initOffset + rowOffset*setY + setX, '1');
	    }
    }

    // Flag the start and exit of the maze.
    result.setCharAt(initOffset - 1, '2');
    result.setCharAt(initOffset + rowOffset*2*(yDim-1) + 2*(xDim-1) + 1, '3');

    bw.write("" + (2*yDim+1) + " " + (2*xDim+1) + "\n");
    bw.write(result.toString());
    bw.close();
    t.Stop();
  }

  public void paintRect(Graphics g, int xDim, int yDim) {
    // White background.
    g.setColor(Color.white);
    g.fillRect(0, 0, 2*xDim, 2*yDim);

    // Black border.
    g.setColor(Color.black);
    g.drawLine(0, 0, 2*xDim, 0);
    g.drawLine(2*xDim, 0, 2*xDim, 2*yDim);
    g.drawLine(2*xDim, 2*yDim, 0, 2*yDim);
    g.drawLine(0, 2*yDim, 0, 0);

    int x1, y1, x2, y2;
    for(Cell c1 : cells) {
	    x1 = 2*(c1.x)+1;
	    y1 = 2*(c1.y)+1;
	    for(Cell c2 : c1.walls) {
        x2 = 2*(c2.x)+1;
        y2 = 2*(c2.y)+1;
        if (x2 > x1)
          g.drawLine(x1+1, y1-1, x1+1, y1+1);
        if (x2 < x1)
          g.drawLine(x2+1, y2-1, x2+1, y2+1);
        if (y2 > y1)
          g.drawLine(x1+1, y1+1, x1-1, y1+1);
        if (y2 < y1)
          g.drawLine(x2+1, y2+1, x2-1, y2+1);
	    }
    }

    g.setColor(Color.white);
    g.drawLine(0, 1, 0, 1);
    g.drawLine(2*xDim, 2*yDim-1, 2*xDim, 2*yDim-1);
  }

  public void saveRectToPng(String fileName, int xDim, int yDim) throws IOException {
    Timer t = new Timer("creating image buffer");
    BufferedImage image = new BufferedImage(2 * xDim + 1, 2 * yDim + 1,
                                            BufferedImage.TYPE_INT_RGB);
    t.Stop();

    t = new Timer("painting");
    paintRect(image.getGraphics(), xDim, yDim);
    t.Stop();

    // Save as PNG
    t = new Timer("saving to PNG");
    File file = new File(fileName + ".png");
    ImageIO.write(image, "png", file);
    t.Stop();
  }

  public static void usage() {
    System.err.println("Usage:\tjava maze [-p][-t][-s xSize ySize]");
    System.err.println("-p = PNG, -t = TXT");
    System.err.println("Use at least one of the -p or -t options, or no output will be generated.");
    System.err.println("xSize and ySize default to 10, if you do not use the -s option.");
    System.exit(0);
  }

  public static void main(String[] args) throws IOException {
    int x = 10,
        y = 10;
    boolean
        text = false,
        png = false;

    for(int i = 0 ; i < args.length ; i++) {
	    if (args[i].charAt(0) == '-') {
        switch(args[i].charAt(1)) {
          case 's':
          case 'S':
            try {
              x = Integer.parseInt(args[++i])/2;
              y = Integer.parseInt(args[++i])/2;
            } catch (Exception e) {
              usage();
            }
            break;
          case 'p':
          case 'P':
            png = true;
            break;
          case 't':
          case 'T':
            text = true;
            break;
          default:
            usage();
        }
	    }
    }
    if (!png && !text) {
	    usage();
	    System.exit(0);
    }

    Maze m = new Maze();
    m.initRect(x, y);
    m.create();
    int x1 = x*2 + 1;
    int y1 = y*2 + 1;
    String fileName = "maze" + x1 + "x" + y1;

    if (text) m.outputText(fileName, x, y);
    if (png) m.saveRectToPng(fileName, x, y);
  }
}
