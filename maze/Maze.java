import java.util.*;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.io.*;
import javax.imageio.ImageIO;
import java.util.concurrent.*;

public class Maze {

  private class Cell {
    public final int x, y;
    private List<Cell> neighbors = new ArrayList<>(4);
    private List<Cell> doors = new ArrayList<>(4);
    public int depth = Integer.MAX_VALUE;

    public Cell(int x, int y) { this.x = x; this.y = y; }

    // Adds another cell as a neighbor of this cell, and vice versa.
    // By default, no door connects to this neighbor.
    void addNeighbor(Cell c) {
      neighbors.add(c);
      c.neighbors.add(this);
    }

    // Opens a door between this cell and another.
    // These cells must alread be neighbors.
    void openDoor(Cell c) {
      doors.add(c);
      c.doors.add(this);
    }
  }

  private class Wall {
    Cell c1, c2;

    public Wall(Cell cell1, Cell cell2) { c1 = cell1; c2 = cell2; }

    public int hashCode() {
      return c1.hashCode() + 31 * c2.hashCode();
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
    cells = new ArrayList<>(x * y);
    walls = new ArrayList<>(x * y * 2);

    Timer t = new Timer("initializing and linking cells");
    Cell[] temp1 = new Cell[0];  // the current row, being initialized
    Cell[] temp2 = new Cell[0];  // the previous row, for linking vertical walls
    for (int i = 0; i < x; i++) {
      temp1 = new Cell[y];
      for (int j = 0; j < y; j++) {
        temp1[j] = new Cell(i, j);
        cells.add(temp1[j]);

        if (i > 0) {
          temp1[j].addNeighbor(temp2[j]);
          walls.add(new Wall(temp1[j], temp2[j]));
        }
        if (j > 0) {
          temp1[j].addNeighbor(temp1[j - 1]);
          walls.add(new Wall(temp1[j], temp1[j - 1]));
        }
      }
      temp2 = temp1;
    }
    t.Stop();
  }

  public void create(String algorithm) {
    if (algorithm.equals("wilson")) createWilson();
    else if (algorithm.equals("kruskal")) createKruskal();
    else throw new IllegalArgumentException("algorithm name not implemented: '" + algorithm + "'");
  }

  public void createWilson() {
    int stepsTaken = 0;
    int stepsUnwound = 0;
    Timer t = new Timer("random walking");

    Random r = new Random();

    // Cells that are connected to the maze.
    Set<Cell> maze = new HashSet<>();

    int nextStepsTakenReport = 10;
    int nextStepsUnwoundReport = 10;

    Stack<Cell> path = new Stack<>();
    Set<Cell> walked = new HashSet<>();
    for (Cell c : cells) {
      if (maze.isEmpty()) maze.add(c);  // Connect an arbitrary cell; it doesn't need to be random.
      if (maze.contains(c)) continue;  // Skip cells we've already connected.

      path.clear();
      path.add(c);

      walked.clear();
      walked.add(c);

      // Random walk until we bump into the maze.
      while (!maze.contains(c)) {
        // Pick a random next cell to step into.
        c = c.neighbors.get(r.nextInt(c.neighbors.size()));  stepsTaken++;

        // If this is part of the current path already, erase the loop.
        // Unwind the path until our new cell isn't in it...
        while (walked.contains(c)) {
          walked.remove(path.pop());  stepsUnwound++;
        }
        // ... then carry on.

        path.push(c);
        walked.add(c);
      }

      // Carve the entire walked path into the maze.
      while (path.size() > 1) {
        Cell ultimate = path.pop();
        Cell penultimate = path.peek();
        ultimate.openDoor(penultimate);
        maze.add(penultimate);
      }
    }

    t.Stop();
    System.err.println("Steps taken:\t" + stepsTaken);
    System.err.println("Steps unwound:\t" + stepsUnwound);
  }


  public void createKruskal() {
    Timer t = new Timer("shuffling walls");
    Collections.shuffle(walls);
    t.Stop();

    t = new Timer("knocking down walls");
    int numAreas = cells.size();
    UnionFind uf = new UnionFind();
    for (Wall w : walls) {
      Cell c1 = w.c1;
      Cell c2 = w.c2;

      if (uf.equals(c1, c2)) { continue; }

      uf.union(c1, c2);
      c1.openDoor(c2);

      if (--numAreas == 0) break;
    }

    t.Stop();
  }

  public void solve(Cell start) {
    Timer t = new Timer("solving via BFS");

    // BFS traversal from the first cell.
    Queue<Cell> frontier = new LinkedList<>();
    frontier.add(start);
    start.depth = 0;

    while (!frontier.isEmpty()) {
      Cell c = frontier.poll();
      for (Cell next : c.doors) {
        if (next.depth <= c.depth) continue;
        next.depth = c.depth + 1;
        frontier.add(next);
      }
    }

    t.Stop();
  }

  interface DoorPainter {
    void paintDoor(Cell c1, Cell c2);
  }

  public DoorPainter paintDoor(Graphics g) {
    return (c1, c2) -> g.drawLine(2 * (c1.x) + 1, 2 * (c1.y) + 1,
                                  2 * (c2.x) + 1, 2 * (c2.y) + 1);
  }

  public DoorPainter paintDoorNoWalls(Graphics g) {
    return (c1, c2) -> g.drawLine(c1.x, c1.y, c2.x, c2.y);
  }


  public void paintDoorsWhite(Graphics g, DoorPainter dp) {
    g.setColor(Color.white);
    // Carve out open doors.
    for (Cell c1 : cells) {
      for (Cell c2 : c1.doors) {
        dp.paintDoor(c1, c2);
      }
    }
  }

  public void paintDoorsRainbow(Graphics g, DoorPainter dp, ColorWheel cw,
                                float stepsPerColorSpin, float colorSpinOffset) {
    for (Cell c : cells) {
      for (Cell n : c.doors) {
        if (c.depth > n.depth) continue;
        float progress = colorSpinOffset + c.depth / stepsPerColorSpin;
        g.setColor(cw.colorAt(progress));
        dp.paintDoor(c, n);
      }
    }
  }

  public void saveRectToPng(String fileLabel,
                            int xRes, int yRes,
                            boolean hideWalls,
                            int frames, ColorWheel cw) throws IOException {
    if (frames > 1) {
      new File("images/" + fileLabel).mkdirs();
      System.out.println(fileLabel);
    }

    // Solve the maze and find the depth of the exit.
    solve(cells.get(0));
    int solutionLength = cells.get(cells.size() - 1).depth - cells.get(0).depth;
    for (Cell c : cells) {
      solutionLength = Math.max(solutionLength, c.depth - cells.get(0).depth);
    }
    int stepsPerColorSpin = solutionLength * 1;  // TODO: tune for aesthetics, or add a flag

    List<Callable<Void>> renderThreads = new LinkedList<>();
    for (int f = 0; f < frames; f++) {
      final int frame = f;
      renderThreads.add(new Callable<Void>() {
        public Void call() throws IOException {
          float colorSpinOffset = 1.0f - (float) frame / (float) frames;
          //      Timer t = new Timer("creating image buffer");
          BufferedImage image = new BufferedImage(xRes, yRes, BufferedImage.TYPE_INT_RGB);
          //      t.Stop();

          //      t = new Timer("painting");
          Graphics g = image.getGraphics();

          // Black background.
          g.setColor(Color.black);
          g.fillRect(0, 0, xRes, yRes);

          DoorPainter dp = hideWalls ? paintDoorNoWalls(g) : paintDoor(g);

          paintDoorsRainbow(g, dp, cw, (float) stepsPerColorSpin, colorSpinOffset);
          //      t.Stop();

          String fileName = fileLabel;
          if (frames > 1) {
            fileName += "/" + frame;
          }
          fileName += ".png";

          // Save as PNG
          //      Timer t = new Timer("saving to PNG: " + fileName);
          File file = new File("images/" + fileName);
          ImageIO.write(image, "png", file);
          //      t.Stop();

          return null;
        }
      });
    }
    ExecutorService pool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors() * 2);
    Timer t = new Timer("rendering " + renderThreads.size() + " frames at once.");
    try {
      for (Future<Void> f : pool.invokeAll(renderThreads)) f.get();
    } catch (InterruptedException | ExecutionException e) {
      e.printStackTrace();
      System.exit(-1);
    }
    t.Stop();
    pool.shutdown();
  }

  public static void usage() {
    System.err.println("Usage:\tjava maze [-r xRes yRes][-a algorithm][-w][-f frames][-c colorWheelName]");
    System.err.println("-w = hide walls; only useful with special cell coloring");
    System.exit(0);
  }

  public static void main(String[] args) throws IOException {
    int xRes = 10,
        yRes = 10;
    String algorithm = "wilson";
    boolean hideWalls = false;
    int frames = 1;
    String colorWheelName = "rainbow";

    for (int i = 0 ; i < args.length ; i++) {
      if (args[i].charAt(0) == '-') {
        switch (args[i].charAt(1)) {
        case 'c':
        case 'C':
          colorWheelName = args[++i];
          break;
        case 'r':
        case 'R':
          try {
            xRes = Integer.parseInt(args[++i]);
            yRes = Integer.parseInt(args[++i]);
          } catch (Exception e) {
            usage();
          }
          break;
        case 'f':
        case 'F':
          try {
            frames = Integer.parseInt(args[++i]);
          } catch (Exception e) {
            usage();
          }
          break;
        case 'a':
        case 'A':
          algorithm = args[++i];
          break;
        case 'w':
        case 'W':
          hideWalls = true;
          break;
        default:
          usage();
        }
      }
    }

    int xSize = hideWalls ? xRes : (xRes - 1) / 2;
    int ySize = hideWalls ? yRes : (yRes - 1) / 2;
    Maze m = new Maze();
    m.initRect(xSize, ySize);
    m.create(algorithm);

    new File("images").mkdirs();
    String fileLabel = algorithm + "_" + colorWheelName;
    if (hideWalls) fileLabel += "_nowalls";
    fileLabel += "_" + xRes + "x" + yRes;

    ColorWheel cw = ColorWheel.fromName(colorWheelName);
    m.saveRectToPng(fileLabel, xRes, yRes, hideWalls, frames, cw);
  }
}
