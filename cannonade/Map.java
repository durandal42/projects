import java.util.*;
import java.util.stream.*;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

/*
  For current spec, see:
  http://cannonade.pbwiki.com/The%20Game%20Map
  (This is dead now. RIP.)
 */

public class Map {

  int height, width;
  TerrainSquare[][] grid;
  ArrayList<TerrainSquare> squares;
  Random r = new Random();

  public Map(int width, int height) {
    if (height % 50 != 0 || width % 50 != 0)
      throw new IllegalArgumentException("Map dimensions must be multiples of 50.");
    this.height = height;
    this.width = width;

    log("Initializing squares...");
    grid = new TerrainSquare[width][height];
    squares = new ArrayList<>(height * width);
    for (int x = 0 ; x < width ; x++) {
      for (int y = 0 ; y < height ; y++) {
        grid[x][y] = new TerrainSquare(x, y);
        squares.add(grid[x][y]);
      }
    }
  }

  /*
    1.) The map is separated into 10x10 blocks of spaces. Each block has a 25% chance
    to contain land. If it does, one of the spaces of the block is randomly chosen to
    be the "pinnacle" of the island from which all generation will build outwards.
    There is a 5% chance that a second random space is also designated to be a pinnacle as well.

    2.) The island pinnacle has a 50% chance of being a peak,
    and a 50% chance of being a forest.
   */
  void SeedIslands() {
    log("Seeding islands...");
    for (int x = 0 ; x < width ; x += 10) {
      for (int y = 0 ; y < height ; y += 10) {
        if (r.nextInt(4) == 0) { // contains land
          do {
            int dx = r.nextInt(10);
            int dy = r.nextInt(10);
            switch (r.nextInt(2)) {
            case 0:
              grid[x + dx][y + dy].type = TerrainType.PEAK;
              break;
            case 1:
              grid[x + dx][y + dy].type = TerrainType.FOREST;
              break;
            }
          } while (r.nextInt(20) == 0);  // TODO(durandal): stop after one bonus pinnacle.
        }
      }
    }
  }

  /*
    3.) Each unfilled space surrounding a peak has a 75% chance of being a forest,
    and a 25% chance of being flatland.
   */
  void ExpandFromPeaks() {
    log("Expanding from peaks...");
    WithType(TerrainType.PEAK, squares.stream())
    .flatMap(ts -> EmptyNeighbors(ts))
    .forEach(n -> {
      if (r.nextInt(4) == 0)
        n.type = TerrainType.FOREST;
      else
        n.type = TerrainType.FLATLAND;
    });

  }

  /*
    4.) Each unfilled space surrounding a forest has a 10% chance of also being a forest,
    a 20% chance of being a marsh, and a 70% chance of being flatland.
   */
  void ExpandFromForests() {
    log("Expanding from forests...");
    Queue<TerrainSquare> forests = new ArrayDeque<>();
    WithType(TerrainType.FOREST, squares.stream()).forEach(forests::offer);

    while (forests.size() > 0) {
      TerrainSquare forest = forests.poll();
      EmptyNeighbors(forest).forEach(neighbor -> {
        switch (r.nextInt(10)) {
        case 0:
          neighbor.type = TerrainType.FOREST;
          // Since this cell is now a forest, we need to expand from it as well.
          forests.offer(neighbor);
          break;
        case 1:
        case 2:
          neighbor.type = TerrainType.MARSH;
          break;
        default:
          neighbor.type = TerrainType.FLATLAND;
        }
      });
    }
  }

  /*
    5.) Each unfilled space surrounding a flatland space has a 20% chance of also being flatland,
    a 10% chance of being a marsh, and a 70% chance of being a beach.
   */
  void ExpandFromFlatlands() {
    log("Expanding from flatlands...");
    Queue<TerrainSquare> flatlands = new ArrayDeque<>();
    WithType(TerrainType.FLATLAND, squares.stream()).forEach(flatlands::offer);

    while (flatlands.size() > 0) {
      TerrainSquare flatland = flatlands.poll();
      EmptyNeighbors(flatland).forEach(neighbor -> {
        switch (r.nextInt(10)) {
        case 0:
        case 1:
          neighbor.type = TerrainType.FLATLAND;
          flatlands.offer(neighbor);
          break;
        case 2:
          neighbor.type = TerrainType.MARSH;
          break;
        default:
          neighbor.type = TerrainType.BEACH;
        }
      });
    }
  }

  /*
    6.) Marshland acts as a border to edge the island, and must be contiguous with at
    least two other marsh spaces (taking the shortest possible route to achieve that aim).
    Where it borders beach, beaches may be turned into marshes to satisfy this requirement.
   */
  void ConnectMarshes() {
    log("Connecting marshes...");
    Set<TerrainSquare> visitedMarshes = new HashSet<>();
    long tinyMarshes = WithType(TerrainType.MARSH, squares.stream())
                      .filter(ts -> !TryConnectMarsh(ts, visitedMarshes)).count();
    if (tinyMarshes > 0) {
      log(String.format("\tWARNING: Had to abandon %d tiny marsh(es).", tinyMarshes));
    }
  }
  // Returns true if this marsh is now connected (or part of a marsh region which we've already failed to connect)
  boolean TryConnectMarsh(TerrainSquare marshCenter, Set<TerrainSquare> visitedMarshes) {
    if (visitedMarshes.contains(marshCenter)) return true;

    // Find contiguious region of marsh, and any beaches which border it.
    Set<TerrainSquare> marshRegion = new HashSet<>();
    Set<TerrainSquare> beachBorder = new HashSet<>();
    Queue<TerrainSquare> frontier = new ArrayDeque<>();
    frontier.offer(marshCenter);
    while (!frontier.isEmpty()) {
      TerrainSquare marsh = frontier.poll();
      if (visitedMarshes.contains(marsh)) continue;
      marshRegion.add(marsh);
      visitedMarshes.add(marsh);
      // Bailing out early doesn't help, since we'll still have to check those marshes later.
      Neighbors(marsh).forEach(neighbor -> {
        if (neighbor.type == TerrainType.MARSH) frontier.offer(neighbor);
        if (neighbor.type == TerrainType.BEACH) beachBorder.add(neighbor);
      });
    }
    if (marshRegion.size() >= 3) return true; // Marsh is large enough; move on.

    // Look for beaches which could connect us to another marsh.
    List<TerrainSquare> marshConnectingBeaches = beachBorder.stream()
        .filter(beach -> WithType(TerrainType.MARSH, Neighbors(beach))
                .anyMatch(neighbor -> !marshRegion.contains(neighbor))).collect(Collectors.toList());
    if (marshConnectingBeaches.size() > 0) {
      RandomFrom(marshConnectingBeaches).type = TerrainType.MARSH;
      return true;
    }

    // If there are two nearby beaches, good enough.
    if (beachBorder.size() >= 2) {
      // Make two of them marshes, at random.
      List<TerrainSquare> shuffleableBeachBorder = new ArrayList<>(beachBorder);
      Collections.shuffle(shuffleableBeachBorder);
      shuffleableBeachBorder.get(0).type = TerrainType.MARSH;
      shuffleableBeachBorder.get(1).type = TerrainType.MARSH;
      return true;
    }

    // This solo marsh can't be connected to another marsh, and doesn't have two neighboring beaches.
    // Try chaining one adjacent beach into another.
    while (beachBorder.size() > 0 && marshRegion.size() < 3) {
      TerrainSquare beach = beachBorder.iterator().next();
      beach.type = TerrainType.MARSH;
      marshRegion.add(beach);
      beachBorder.clear();
      WithType(TerrainType.BEACH, Neighbors(beach)).forEach(beachBorder::add);
    }

    // If we still don't have a big enough marsh, we've run out of ideas. Give up. :(
    return marshRegion.size() >= 3;
  }
  
  /*
    7.) Beaches also act as an island border.

    8.) Where borderland is surrounded by other land, it has a 90% chance of becoming
    flatland. Otherwise it remains as-is.
   */
  void FlattenLandlockedBorders() {
    log("Flattening landlocked beaches/marshes...");
    squares.stream().filter(ts -> ts.isBorder())
    .filter(ts -> Neighbors(ts).allMatch(n -> n.isLand()) && r.nextInt(10) != 0)
    .forEach(ts -> ts.type = TerrainType.FLATLAND);
  }

  /*
    9.) Each unfilled space surrounding a borderland-space has a 10% chance of being open
    water, and a 90% chance of being a shoal.
   */
  void ExpandFromBorderlands() {
    log("Expanding from borderlands...");
    squares.stream().filter(ts -> ts.isBorder()).flatMap(ts -> EmptyNeighbors(ts)).forEach(n -> {
      if (r.nextInt(10) == 0)
        n.type = TerrainType.OPEN_WATER;
      else
        n.type = TerrainType.SHOAL;
    });

  }

  /*
     10.) Open water bordering land must be contiguous with more open water. At least one
     unfilled space surrounding it must become open water. If this circumstance cannot be
     met, the open water becomes a shoal.
   */
  void OpenWater() {
    log("Ensuring open water is open...");
    WithType(TerrainType.OPEN_WATER, squares.stream())
    .filter(ts -> Neighbors(ts).anyMatch(n -> n.isLand()))
    .forEach(ts -> {
      // TODO(durandal): if RandomFrom returns failure on empty list, use that here?
      List<TerrainSquare> neighbors = EmptyNeighbors(ts).collect(Collectors.toList());
      if (neighbors.size() > 0) {
        RandomFrom(neighbors).type = TerrainType.OPEN_WATER;
      } else {
        ts.type = TerrainType.SHOAL;
      }
    });
  }

  /*
    11.) If a 10x10 block of spaces is determined to contain only water, it has a 30%
    chance of having a space inside it randomly-chosen to be a shoal.
   */
  void SeedShoals() {
    log("Adding shoals to watery areas...");
    for (int i = 0 ; i < width ; i += 10) {
      for (int j = 0 ; j < height ; j += 10) {
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
  }

  /*
    12.) Shoal spaces must be contiguous with at least one other shoal space. They will
    transform open water or unfilled spaces into shoals to satisfy this requirement if
    it is not met. Unfilled spaces surrounding shoals have a 20% chance of being shoals,
    and an 80% chance of being open water.
   */
  void ConnectAndExpandFromShoals() {
    log("Expanding shoals...");
    WithType(TerrainType.SHOAL, squares.stream()).forEach(center -> {
      Collection<TerrainSquare> neighbors = Neighbors(center).collect(Collectors.toList());
      if (WithType(TerrainType.SHOAL, neighbors.stream()).count() == 0) {
        Collection<TerrainSquare> targetNeighbors = EmptyNeighbors(center).collect(Collectors.toList());
        if (targetNeighbors.size() == 0)
          targetNeighbors = WithType(TerrainType.OPEN_WATER, neighbors.stream()).collect(Collectors.toList());
        if (targetNeighbors.size() == 0) {
          log("WARNING: had to abandon an isolated shoal at: " + center);
          return;
        }
        RandomFrom(targetNeighbors).type = TerrainType.SHOAL;
      }
    });
    Queue<TerrainSquare> shoals = new ArrayDeque<>();
    WithType(TerrainType.SHOAL, squares.stream()).forEach(shoals::offer);
    while (shoals.size() > 0) {
      TerrainSquare center = shoals.poll();
      EmptyNeighbors(center).forEach(ts -> {
        if (r.nextInt(5) == 0) {
          ts.type = TerrainType.SHOAL;
          shoals.offer(ts);
        } else {
          ts.type = TerrainType.OPEN_WATER;
        }
      });
    }
  }

  /*
    13.) Everything else is open water.
   */
  void FillOpenWater() {
    log("Filling in water...");
    for (TerrainSquare ts : squares)
      if (ts.type == TerrainType.EMPTY)
        ts.type = TerrainType.OPEN_WATER;
  }

// Unclear why numbering in the spec resets to 1 here. /shrug

  /*
    1.) Every space of water not directly bordering land has a 1% chance to be a crag.
    If this transformation would violate any of the rules regarding continuity of water
    formations, it does not occur. Crags also cannot be directly horizontally or
    vertically adjacent to another crag. If neither of these negative conditions occur,
    the water space is replaced with a crag. Spaces surrounding these central crags to
    a distance of two squares then have a 10% chance of also being turned into crags,
    though this percentage chance does not extend outwards to the new satellite crags.
   */
  void SpawnCrags() {
    log("Adding crags...");
    for (TerrainSquare center : squares) {
      if (r.nextInt(100) == 0)
        TryCragify(center, true);
    }
  }
  void TryCragify(TerrainSquare center, boolean canSpawnSatelliteCrags) {
    // Crags can only spawn in water.
    if (!center.isWater()) return;

    // Don't spawn crags touching land.
    if (Neighbors(center).anyMatch(ts -> ts.isLand())) return;

    // Don't spawn crags horizontally or vertically adjacent to an existing crag.
    if (WithType(TerrainType.CRAG, OrthoganalNeighbors(center)).count() > 0)
      return;

    // Speculatively proceed, but remember what used to be here.
    TerrainType oldType = center.type;
    center.type = TerrainType.CRAG;
    // Check to see if adjacent neighbors with our old type are now stranded.
    // (Open water and shoals both need  to be contiguous with at least one other square of the same type.)
    if (WithType(oldType, Neighbors(center)).anyMatch(ts -> WithType(oldType, Neighbors(ts)).count() == 0)) {
      center.type = oldType;  // roll back
      return;
    }

    if (canSpawnSatelliteCrags)
      Neighbors(center, 2).filter(ts -> r.nextInt(10) == 0).forEach(ts -> TryCragify(ts, false));
  }


  /*
    2.) Where open water directly borders land, the square of borderland horizontally or
    vertically adjacent to the open water has a 25% chance of being a turned into a port.
    75% of the time these ports will be a cove, 25% of the time they will be a wharf
    instead. Otherwise there is a flat 1% chance of borderland adjacent to shoals becoming
    a cove. Coves may not be adjacent to any other port - if they would be so if created,
    the creation of the cove does not happen.
  */
  void SpawnPorts() {
    log("Adding ports...");
    ArrayList<TerrainSquare> candidateCoves = new ArrayList<>();
    WithType(TerrainType.OPEN_WATER, squares.stream())
    .flatMap(ts -> OrthoganalNeighbors(ts)).forEach(candidatePort -> {
      if (candidatePort.isLand() && r.nextInt(4) == 0) {
        if (r.nextInt(4) == 0) {
          candidatePort.type = TerrainType.WHARF;
        } else {
          // Cove spawning is more complicated.
          candidateCoves.add(candidatePort);
        }
      }
    });
    // ... and there are more ways to become a candidate cove.
    squares.stream().filter(ts -> ts.isBorder())
    .filter(ts -> WithType(TerrainType.SHOAL, Neighbors(ts)).count() > 0)
    .filter(ts -> r.nextInt(100) == 0)
    .forEach(ts -> candidateCoves.add(ts));

    // Evaluate candidate coves.
    candidateCoves.stream()
    .filter(cc -> !Neighbors(cc).anyMatch(n -> n.isPort()))
    .forEach(cc -> cc.type = TerrainType.COVE);
  }


  /*
    3.) The map will be divided into 50x50 blocks of squares, and each will have a abbey
    randomly place on the available land within that block.
  */
  void SpawnAbbeys() {
    log("Adding abbeys...");
    ArrayList<TerrainSquare> potentialAbbeys = new ArrayList<>();
    for (int x = 0 ; x < width ; x += 50) {
      for (int y = 0 ; y < height ; y += 50) {
        potentialAbbeys.clear();
        for (int dx = 0 ; dx < 50 ; dx++) {
          for (int dy = 0 ; dy < 50 ; dy++) {
            TerrainSquare ts = grid[x + dx][y + dy];
            if (ts.isLand() && !ts.isCivilized())
              potentialAbbeys.add(ts);
          }
        }
        RandomFrom(potentialAbbeys).type = TerrainType.ABBEY;
      }
    }
  }


  /*
    4.) There are 100 forts in the game, scattered semi-randomly. No fort may be more
    than 50 spaces in any direction from another fort, and no fort may be within 3
    spaces of another fort, but there are no further restrictions other than that forts
    must be placed on land.
   */
  void SpawnForts() {
    log("Adding forts...");
    int numFortsDesired = height * width / 400;  // Maintain same fort density regardless of map size.
    List<TerrainSquare> potentialForts = new ArrayList<>();
    Set<TerrainSquare> forbiddenForts = new HashSet<>();
    List<TerrainSquare> forts = new ArrayList<>();
    for (TerrainSquare ts : squares) {
      if (ts.isWater()) continue;
      if (ts.isCivilized()) continue;
      if (ts.type == TerrainType.FLATLAND) // Conservative: try only including flatland
        potentialForts.add(ts);
    }
    Collections.shuffle(potentialForts);  // Can't just sample numFortsDesired, might reject some and need more.
    log("\tnumFortsDesired = " + numFortsDesired);
    log("\tpotentialForts = " + potentialForts.size());
    for (TerrainSquare potentialFort : potentialForts) {
      if (forbiddenForts.contains(potentialFort)) continue;
      potentialFort.type = TerrainType.FORT;
      forts.add(potentialFort);
      if (--numFortsDesired == 0) break;
      Neighbors(potentialFort, 3).forEach(forbiddenForts::add);
    }
    if (numFortsDesired > 0) {
      log("WARNING: ran out of suitable fort locations with " + numFortsDesired + " unplaced forts.");
    }

    log(String.format("Sanity checking placement of %d forts...", forts.size()));
    for (TerrainSquare fort1 : forts) {
      int minDist = Integer.MAX_VALUE;
      for (TerrainSquare fort2 : forts) {
        if (fort1 == fort2) continue;
        int dist = Distance(fort1, fort2);
        if (dist <= 3)
          log("WARNING: forts too close together: " + fort1 + fort2);
        if (dist < minDist) minDist = dist;
      }
      if (minDist > 50)
        log("WARNING: fort too far away from nearest neighbor: " + fort1);
    }
  }

  /*
    5.) Any land space not an abbey, fort, or wharf has a .3% chance of becoming a settlement.
  */
  void SpawnSettlements() {
    log("Adding settlements...");
    for (TerrainSquare ts : squares) {
      if (ts.isLand() && !ts.isCivilized() && r.nextInt(1000) < 3)
        ts.type = TerrainType.SETTLEMENT;
    }
    // TODO(durandal): if no settlements spawned, spawn at least one? two? on different land masses?
  }

  public void Genesis() {
    SeedIslands();
    ExpandFromPeaks();
    ExpandFromForests();
    ExpandFromFlatlands();
    ConnectMarshes();
    FlattenLandlockedBorders();
    ExpandFromBorderlands();
    OpenWater();
    SeedShoals();
    ConnectAndExpandFromShoals();
    FillOpenWater();

    // Spec numbering reset here. Unclear what's the significance.

    SpawnCrags();
    SpawnPorts();
    SpawnAbbeys();
    SpawnForts();
    SpawnSettlements();
  }

  TerrainSquare RandomFrom(Collection<TerrainSquare> c) {
    int index = r.nextInt(c.size());
    for (TerrainSquare ts : c)
      if (index-- == 0)
        return ts;
    return null;
  }

  TerrainSquare RandomFrom(List<TerrainSquare> c) {
    return c.get(r.nextInt(c.size()));
  }

  Stream<TerrainSquare> WithType(TerrainType type, Stream<TerrainSquare> input) {
    return input.filter(ts -> ts.type == type);
  }

  Stream<TerrainSquare> WithEmptyNeighbors(Stream<TerrainSquare> input) {
    return input.filter(ts -> EmptyNeighbors(ts).count() > 0);
  }

  Stream<TerrainSquare> EmptyNeighbors(TerrainSquare ts) {
    return WithType(TerrainType.EMPTY, Neighbors(ts));
  }

  Stream<TerrainSquare> OrthoganalNeighbors(TerrainSquare center) {
    return Neighbors(center).filter(ts -> ts.x == center.x || ts.y == center.y);
  }

  Stream<TerrainSquare> Neighbors(TerrainSquare ts) {
    return Neighbors(ts, 1);
  }
  Stream<TerrainSquare> Neighbors(TerrainSquare ts, int radius) {
    int minx = Math.max(ts.x - radius, 0);
    int maxx = Math.min(ts.x + radius, width - 1);
    int miny = Math.max(ts.y - radius, 0);
    int maxy = Math.min(ts.y + radius, height - 1);
    List<TerrainSquare> c = new ArrayList<>();
    for (int x = minx ; x <= maxx ; x++)
      for (int y = miny ; y <= maxy ; y++)
        if (x != ts.x || y != ts.y)
          c.add(grid[x][y]);
    return c.stream();
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
      g.fillRect(ts.x * blockSize, ts.y * blockSize,
                 blockSize, blockSize);
      if (blockSize > gridThreshold) {
        g.setColor(Color.black);
        g.drawRect(ts.x * blockSize, ts.y * blockSize,
                   blockSize, blockSize);
      }
    }
    log("Saving to disk...");
    try {
      ImageIO.write(image, "png", new File(String.format("images/%dx%d.png", width, height)));
    } catch (IOException e) {
      log("ERROR: failed to output to file.");
    }
  }

  public String Histogram() {
    StringBuffer buf = new StringBuffer();
    buf.append("Terrain Type breakdown:\n");
    for (TerrainType tt : TerrainType.values()) {
      buf.append(String.format("\t%s:\t%d\n", tt, WithType(tt, squares.stream()).count()));
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
