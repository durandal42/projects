import java.util.LinkedList;
import java.util.HashSet;
import java.util.Collection;
import java.util.Iterator;
import java.util.Random;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

/*
  For current spec, see:
  http://cannonade.pbwiki.com/The%20Game%20Map
 */

public class Map {

  int height, width;
  TerrainSquare[][] grid;
  LinkedList<TerrainSquare> squares;

  public Map(int w, int h) {
    if (h % 50 != 0 || w % 50 != 0)
      throw new IllegalArgumentException();
    height = h;
    width = w;
    grid = new TerrainSquare[height][width];
    squares = new LinkedList<TerrainSquare>();
    for (int i = 0 ; i < height ; i++) {
      for (int j = 0 ; j < width ; j++) {
        grid[i][j] = new TerrainSquare(i, j);
        squares.add(grid[i][j]);
      }
    }
  }

  public void Genesis() {
    log("Initializing squares...");
    for (TerrainSquare ts : squares)
      ts.type = TerrainType.EMPTY;

    Random r = new Random();

    /*
      1.) The map is separated into 10x10 blocks of spaces. Each block has a 25% chance
      to contain land. If it does, one of the spaces of the block is randomly chosen to
      be the "pinnacle" of the island from which all generation will build outwards.
      There is a 5% chance that a second random space is also designated to be a pinnacle as well.
    */
    log("Seeding islands...");
    for (int i = 0 ; i < height ; i += 10) {
      for (int j = 0 ; j < width ; j += 10) {
        if (r.nextInt(4) == 0) { // contains land
          do {
            int x = i + r.nextInt(10);
            int y = j + r.nextInt(10);
            /*
              2.) The island pinnacle has a 50% chance of being a peak,
              and a 50% chance of being a forest.
            */
            switch (r.nextInt(2)) {
            case 0:
              grid[x][y].type = TerrainType.PEAK;
              break;
            case 1:
              grid[x][y].type = TerrainType.FOREST;
              break;
            }
          } while (r.nextInt(20) == 0);
        }
      }
    }

    /*
      3.) Each unfilled space surrounding a peak has a 75% chance of being a forest,
      and a 25% chance of being flatland.
    */
    log("Expanding from peaks...");
    LinkedList<TerrainSquare> todo;
    todo = WithEmptyNeighbors(WithType(TerrainType.PEAK, squares));
    while (todo.size() > 0) {
      TerrainSquare center = todo.removeFirst();
      for (TerrainSquare neighbor : EmptyNeighbors(center)) {
        if (r.nextInt(4) == 0)
          neighbor.type = TerrainType.FOREST;
        else
          neighbor.type = TerrainType.FLATLAND;
      }
    }
    todo.clear();

    /*
      4.) Each unfilled space surrounding a forest has a 10% chance of also being a forest,
      a 20% chance of being a marsh, and a 70% chance of being flatland.
    */
    log("Expanding from forests...");
    todo = WithEmptyNeighbors(WithType(TerrainType.FOREST, squares));
    while (todo.size() > 0) {
      TerrainSquare center = todo.removeFirst();
      for (TerrainSquare neighbor : EmptyNeighbors(center)) {
        switch (r.nextInt(10)) {
        case 0:
          neighbor.type = TerrainType.FOREST;
          todo.addLast(neighbor);
          break;
        case 1:
        case 2:
          neighbor.type = TerrainType.MARSH;
          break;
        default:
          neighbor.type = TerrainType.FLATLAND;
        }
      }
    }
    todo.clear();

    /*
      5.) Each unfilled space surrounding a flatland space has a 20% chance of also being flatland,
      a 10% chance of being a marsh, and a 70% chance of being a beach.
    */
    log("Expanding from flatlands...");
    todo = WithEmptyNeighbors(WithType(TerrainType.FLATLAND, squares));
    while (todo.size() > 0) {
      TerrainSquare center = todo.removeFirst();
      for (TerrainSquare neighbor : EmptyNeighbors(center)) {
        switch (r.nextInt(10)) {
        case 0:
        case 1:
          neighbor.type = TerrainType.FLATLAND;
          todo.addLast(neighbor);
          break;
        case 2:
          neighbor.type = TerrainType.MARSH;
          break;
        default:
          neighbor.type = TerrainType.BEACH;
        }
      }
    }
    todo.clear();

    /*
      6.) Marshland acts as a border to edge the island, and must be contiguous with at
      least two other marsh spaces (taking the shortest possible route to achieve that aim).
      Where it borders beach, beaches may be turned into marshes to satisfy this requirement.
    */
    log("Connecting marshes...");
    todo = WithType(TerrainType.MARSH, squares);
    while (todo.size() > 0) {
      TerrainSquare center = todo.removeFirst();
      LinkedList<TerrainSquare> marshyNeighbors = WithType(TerrainType.MARSH, Neighbors(center));
      if (marshyNeighbors.size() >= 2) continue;
      LinkedList<TerrainSquare> beachTargets = WithType(TerrainType.BEACH, Neighbors(center));
      boolean marshyEnough = false;
      for (TerrainSquare mn : marshyNeighbors) {
        LinkedList<TerrainSquare> marshyGrandNeighbors =
          WithType(TerrainType.MARSH, Neighbors(mn));
        if (marshyGrandNeighbors.size() >= 2) {
          marshyEnough = true;
          break;
        }
        beachTargets.addAll(WithType(TerrainType.BEACH, Neighbors(mn)));
      }
      if (marshyEnough) continue;
      if (beachTargets.size() == 0)
        continue;
      todo.addLast(center);
      RandomFrom(beachTargets, r).type = TerrainType.MARSH;
    }

    /*
      7.) Beaches also act as an island border.

      8.) Where borderland is surrounded by other land, it has a 90% chance of becoming
      flatland. Otherwise it remains as-is.
    */
    log("Flattening landlocked beaches/marshes...");
    for (TerrainSquare center : squares) {
      if (center.isBorder()) {
        boolean landLocked = true;
        for (TerrainSquare ts : Neighbors(center))
          landLocked &= ts.isLand();
        if (landLocked && r.nextInt(10) != 0)
          center.type = TerrainType.FLATLAND;
      }
    }

    /*
      9.) Each unfilled space surrounding a borderland-space has a 10% chance of being open
      water, and a 90% chance of being a shoal.
    */
    log("Expanding from borderlands...");
    for (TerrainSquare center : squares) {
      if (center.isBorder()) {
        for (TerrainSquare ts : EmptyNeighbors(center)) {
          if (r.nextInt(10) == 0)
            ts.type = TerrainType.OPEN_WATER;
          else
            ts.type = TerrainType.SHOAL;
        }
      }
    }

    /*
      10.) Open water bordering land must be contiguous with more open water. At least one
      unfilled space surrounding it must become open water. If this circumstance cannot be
      met, the open water becomes a shoal.
    */
    log("Ensuring open water is open...");
    for (TerrainSquare center : WithType(TerrainType.OPEN_WATER, squares)) {
      boolean nearLand = false;
      for (TerrainSquare ts : Neighbors(center))
        nearLand |= ts.isLand();
      if (!nearLand) continue;

      LinkedList<TerrainSquare> neighbors = EmptyNeighbors(center);
      if (neighbors.size() == 0) {
        center.type = TerrainType.SHOAL;
        continue;
      }
      RandomFrom(neighbors, r).type = TerrainType.OPEN_WATER;
    }

    /*
      11.) If a 10x10 block of spaces is determined to contain only water, it has a 30%
      chance of having a space inside it randomly-chosen to be a shoal.
    */
    log("Adding shoals to watery areas...");
    for (int i = 0 ; i < height ; i += 10) {
      for (int j = 0 ; j < width ; j += 10) {
        boolean hasLand = false;
        for (int x = 0 ; x < 10 ; x++) {
          for (int y = 0 ; y < 10 ; y++) {
            hasLand |= grid[i + x][j + y].isLand();
          }
        }
        if (!hasLand && r.nextInt(10) < 3) {
          int x = r.nextInt(10);
          int y = r.nextInt(10);
          grid[i + x][j + y].type = TerrainType.SHOAL;
        }
      }
    }

    /*
      12.) Shoal spaces must be contiguous with at least one other shoal space. They will
      transform open water or unfilled spaces into shoals to satisfy this requirement if
      it is not met. Unfilled spaces surrounding shoals have a 20% chance of being shoals,
      and an 80% chance of being open water.
    */
    log("Expanding shoals...");
    for (TerrainSquare center : WithType(TerrainType.SHOAL, squares)) {
      LinkedList<TerrainSquare> neighbors = Neighbors(center);
      if (WithType(TerrainType.SHOAL, neighbors).size() == 0) {
        LinkedList<TerrainSquare> targetNeighbors = EmptyNeighbors(center);
        if (targetNeighbors.size() == 0)
          targetNeighbors = WithType(TerrainType.OPEN_WATER, neighbors);
        if (targetNeighbors.size() == 0)
          continue; // nothing nearby to shoalify
        int index = r.nextInt(targetNeighbors.size());
        for (TerrainSquare ts : targetNeighbors) {
          if (index-- == 0) {
            ts.type = TerrainType.SHOAL;
            break;
          }
        }
      }
    }
    todo = WithEmptyNeighbors(WithType(TerrainType.SHOAL, squares));
    while (todo.size() > 0) {
      TerrainSquare center = todo.removeFirst();
      for (TerrainSquare ts : EmptyNeighbors(center)) {
        if (r.nextInt(5) == 0) {
          ts.type = TerrainType.SHOAL;
          todo.addLast(ts);
        } else {
          ts.type = TerrainType.OPEN_WATER;
        }
      }
    }
    todo.clear();

    /*
      13.) Everything else is open water.
    */
    log("Filling in water...");
    for (TerrainSquare ts : squares)
      if (ts.type == TerrainType.EMPTY)
        ts.type = TerrainType.OPEN_WATER;

    /*
      1) See details in TryCragify()
    */
    log("Adding crags...");
    for (TerrainSquare center : squares) {
      if (r.nextInt(100) != 0) continue;
      TryCragify(center, r, true);
    }

    /*
      2.) Where open water directly borders land, the square of borderland horizontally or
      vertically adjacent to the open water has a 25% chance of being a turned into a port.
      75% of the time these ports will be a cove, 25% of the time they will be a wharf
      instead. Otherwise there is a flat 1% chance of borderland adjacent to shoals becoming
      a cove. Coves may not be adjacent to any other port - if they would be so if created,
      the creation of the cove does not happen.
    */
    log("Adding ports...");
    LinkedList<TerrainSquare> futurePorts = new LinkedList<TerrainSquare>();
    for (TerrainSquare center : WithType(TerrainType.OPEN_WATER, squares)) {
      for (TerrainSquare ts : OrthoganalNeighbors(center)) {
        if (ts.isLand() && r.nextInt(4) == 0) {
          futurePorts.add(ts);
        }
      }
    }
    Iterator<TerrainSquare> portItr = futurePorts.iterator();
    while (portItr.hasNext()) {
      TerrainSquare port = portItr.next();
      if (r.nextInt(4) == 0) {
        port.type = TerrainType.WHARF;
        portItr.remove();
      }
    }
    for (TerrainSquare center : squares) {
      if (center.isBorder() &&
          WithType(TerrainType.SHOAL, Neighbors(center)).size() > 0 &&
          r.nextInt(100) == 0)
        futurePorts.add(center);
    }
    for (TerrainSquare port : futurePorts) {
      boolean nearbyPort = false;
      for (TerrainSquare ts : Neighbors(port)) {
        if (ts.isPort()) {
          nearbyPort = false;
          break;
        }
      }
      if (!nearbyPort)
        port.type = TerrainType.COVE;
    }
    futurePorts.clear();

    /*
      3.) The map will be divided into 50x50 blocks of squares, and each will have a abbey
      randomly place on the available land within that block.
    */
    log("Adding abbeys...");
    LinkedList<TerrainSquare> potentialAbbeys = new LinkedList<TerrainSquare>();
    for (int i = 0 ; i < height ; i += 50) {
      for (int j = 0 ; j < width ; j += 50) {
        potentialAbbeys.clear();
        for (int x = 0 ; x < 50 ; x++) {
          for (int y = 0 ; y < 50 ; y++) {
            TerrainSquare ts = grid[i + x][j + y];
            if (ts.isLand() && !ts.isCivilized())
              potentialAbbeys.add(ts);
          }
        }
        int index = r.nextInt(potentialAbbeys.size());
        for (TerrainSquare ts : potentialAbbeys) {
          if (index-- == 0) {
            ts.type = TerrainType.ABBEY;
            break;
          }
        }
      }
    }
    potentialAbbeys.clear();

    /*
      4.) There are 100 forts in the game, scattered semi-randomly. No fort may be more
      than 50 spaces in any direction from another fort, and no fort may be within 3
      spaces of another fort, but there are no further restrictions other than that forts
      must be placed on land.
    */
    log("Adding forts (randomly) ...");
    int numFortsDesired = height * width / 400;
    HashSet<TerrainSquare> potentialForts = new HashSet<TerrainSquare>();
    LinkedList<TerrainSquare> forts = new LinkedList<TerrainSquare>();
    for (TerrainSquare ts : squares) {
      if (ts.isWater()) continue;
      if (ts.isCivilized()) continue;
      if (ts.type == TerrainType.FLATLAND) // try only including flatland
        potentialForts.add(ts);
    }
    log("\tnumFortsDesired = " + numFortsDesired);
    log("\tpotentialForts = " + potentialForts.size());
    while (numFortsDesired > 0) {
      if (potentialForts.size() == 0) {
        log("WARNING: ran out of suitable fort locations with " + numFortsDesired + " unplaced forts.");
        break;
      }
      TerrainSquare fort = RandomFrom(potentialForts, r);

      potentialForts.remove(fort);
      potentialForts.removeAll(Neighbors(fort, 3));
      fort.type = TerrainType.FORT;
      forts.add(fort);
      numFortsDesired--;
      //      for (TerrainSquare ts : potentialForts) {
    }
    log("Sanity check for " + forts.size() + " forts.");
    for (TerrainSquare fort1 : forts) {
      int minDist = height;
      for (TerrainSquare fort2 : forts) {
        if (fort1 == fort2) continue;
        int dist = Distance(fort1, fort2);
        if (dist <= 3)
          log("WARNING: forts too close together: " + fort1 + fort2);
        if (dist < minDist) minDist = dist;
      }
      if (minDist > 50)
        log("WARNING: fort too far away: " + fort1);
    }


    /*
      5.) Any land space not an abbey, fort, or wharf has a .3% chance of becoming a settlement.
    */
    log("Adding settlements...");
    for (TerrainSquare ts : squares) {
      if (ts.isLand() && !ts.isCivilized() && r.nextInt(1000) < 3)
        ts.type = TerrainType.SETTLEMENT;
    }

  }


  /*
    1.) Every space of water not directly bordering land has a 1% chance to be a crag.
    If this transformation would violate any of the rules regarding continuity of water
    formations, it does not occur. Crags also cannot be directly horizontally or
    vertically adjacent to another crag. If neither of these negative conditions occur,
    the water space is replaced with a crag. Spaces surrounding these central crags to
    a distance of two squares then have a 10% chance of also being turned into crags,
    though this percentage chance does not extend outwards to the new satellite crags.
  */
  void TryCragify(TerrainSquare center, Random r, boolean chain) {
    if (center.isLand()) return;; // skip land
    boolean atSea = true;
    for (TerrainSquare ts : Neighbors(center)) {
      if (ts.isLand()) {
        atSea = false;
        break;
      }
    }
    if (!atSea) return; // skip touching land

    if (WithType(TerrainType.CRAG, OrthoganalNeighbors(center)).size() > 0)
      return;

    TerrainType oldType = center.type;
    center.type = TerrainType.CRAG; // try cragifying

    boolean waterwaysObstructed = false;
    for (TerrainSquare ts : WithType(oldType, Neighbors(center))) {
      if (WithType(oldType, Neighbors(ts)).size() == 0) {
        waterwaysObstructed = true;
        break;
      }
    }
    if (waterwaysObstructed) {
      center.type = oldType; // roll back
      return;
    }

    if (!chain) return; // no chaining, this was already a chained crag

    for (TerrainSquare ts : Neighbors(center, 2))
      if (r.nextInt(10) == 0)
        TryCragify(ts, r, false);
  }

  TerrainSquare RandomFrom(Collection<TerrainSquare> c, Random r) {
    int index = r.nextInt(c.size());
    for (TerrainSquare ts : c)
      if (index-- == 0)
        return ts;
    return null;
  }

  LinkedList<TerrainSquare> WithType(TerrainType type, LinkedList<TerrainSquare> input) {
    LinkedList<TerrainSquare> c = new LinkedList<TerrainSquare>();
    for (TerrainSquare ts : input)
      if (ts.type == type)
        c.add(ts);
    return c;
  }

  LinkedList<TerrainSquare> WithEmptyNeighbors(LinkedList<TerrainSquare> input) {
    LinkedList<TerrainSquare> c = new LinkedList<TerrainSquare>();
    for (TerrainSquare ts : input)
      if (EmptyNeighbors(ts).size() > 0)
        c.add(ts);
    return c;
  }

  LinkedList<TerrainSquare> EmptyNeighbors(TerrainSquare ts) {
    return WithType(TerrainType.EMPTY, Neighbors(ts));
  }

  LinkedList<TerrainSquare> OrthoganalNeighbors(TerrainSquare center) {
    LinkedList<TerrainSquare> neighbors = Neighbors(center);
    Iterator<TerrainSquare> itr = neighbors.iterator();
    while (itr.hasNext()) {
      TerrainSquare ts = itr.next();
      if (ts.x != center.x && ts.y != center.y)
        itr.remove();
    }
    return neighbors;
  }

  LinkedList<TerrainSquare> Neighbors(TerrainSquare ts) {
    return Neighbors(ts, 1);
  }
  LinkedList<TerrainSquare> Neighbors(TerrainSquare ts, int radius) {
    int minx = Math.max(ts.x - radius, 0);
    int maxx = Math.min(ts.x + radius, height - 1);
    int miny = Math.max(ts.y - radius, 0);
    int maxy = Math.min(ts.y + radius, width - 1);
    LinkedList<TerrainSquare> c = new LinkedList<TerrainSquare>();
    for (int i = minx ; i <= maxx ; i++)
      for (int j = miny ; j <= maxy ; j++)
        if (i != ts.x || ts.y != j)
          c.add(grid[i][j]);
    return c;
  }

  int Distance(TerrainSquare ts1, TerrainSquare ts2) {
    return Math.abs(ts1.x - ts2.x) + Math.abs(ts1.y - ts2.y);
  }

  public String toString() {
    StringBuffer buf = new StringBuffer();
    buf.append("+");
    for (int j = 0 ; j < width ; j++)
      buf.append("-");
    buf.append("+\n");
    for (int i = 0 ; i < height ; i++) {
      buf.append("|");
      for (int j = 0 ; j < width ; j++) {
        buf.append(grid[i][j]);
      }
      buf.append("|\n");
    }
    buf.append("+");
    for (int j = 0 ; j < width ; j++)
      buf.append("-");
    buf.append("+\n");
    return buf.toString();
  }

  public void Output(int blockSize) {
    int gridThreshold = 2;
    log("Creating image buffer...");
    BufferedImage image = new BufferedImage(width * blockSize + (blockSize > gridThreshold ? 1 : 0),
                                            height * blockSize + (blockSize > gridThreshold ? 1 : 0),
                                            BufferedImage.TYPE_INT_RGB);
    log("Painting...");
    Graphics g = image.getGraphics();
    for (TerrainSquare ts : squares) {
      g.setColor(ts.getColor());
      g.fillRect(ts.y * blockSize, ts.x * blockSize,
                 blockSize, blockSize);
      if (blockSize > gridThreshold) {
        g.setColor(Color.black);
        g.drawRect(ts.y * blockSize, ts.x * blockSize,
                   blockSize, blockSize);
      }
    }
    log("Saving to disk...");
    try {
      ImageIO.write(image, "png", new File("output.png"));
    } catch (IOException e) {
      log("ERROR: failed to output to file.");
    }
  }

  public String Histogram() {
    StringBuffer buf = new StringBuffer();
    for (TerrainType tt : TerrainType.values()) {
      buf.append(tt);
      buf.append(":\t");
      buf.append(WithType(tt, squares).size());
      buf.append("\n");
    }
    return buf.toString();
  }

  static void log(String msg) {
    System.out.println(msg);
  }

  public static void main(String[] args) {
    Map m = new Map(Integer.parseInt(args[0]),
                    Integer.parseInt(args[1]));
    m.Genesis();
    log(m.Histogram());
    m.Output(Integer.parseInt(args[2]));
    //  System.out.print(m);
  }

}
