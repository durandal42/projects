import java.time.*;
import java.util.*;
import java.util.stream.*;
import java.util.concurrent.ThreadLocalRandom;
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

  public Map(int width, int height) {
    if (height % 50 != 0 || width % 50 != 0)
      throw new IllegalArgumentException("Map dimensions must be multiples of 50.");
    this.height = height;
    this.width = width;

    log("Initializing squares...");
    grid = new TerrainSquare[width][height];
    for (int x = 0 ; x < width ; x++) {
      for (int y = 0 ; y < height ; y++) {
        grid[x][y] = new TerrainSquare(x, y);
      }
    }
  }

  Random r() {
    return ThreadLocalRandom.current();
  }

  Stream<TerrainSquare> squares() {
    return Arrays.stream(grid).parallel().flatMap(row -> Arrays.stream(row));
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
        if (r().nextInt(4) == 0) { // contains land
          do {
            int dx = r().nextInt(10);
            int dy = r().nextInt(10);
            switch (r().nextInt(2)) {
            case 0:
              grid[x + dx][y + dy].type = TerrainType.PEAK;
              break;
            case 1:
              grid[x + dx][y + dy].type = TerrainType.FOREST;
              break;
            }
          } while (r().nextInt(20) == 0);  // TODO(durandal): stop after one bonus pinnacle.
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
    WithType(TerrainType.PEAK, squares())
    .flatMap(ts -> EmptyNeighbors(ts))
    .forEach(n -> {
      if (r().nextInt(4) == 0)
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
    WithType(TerrainType.FOREST, squares()).forEach(f -> ExpandFromForest(f));
  }
  void ExpandFromForest(TerrainSquare f) {
    EmptyNeighbors(f).forEach(ts -> {
      switch (r().nextInt(10)) {
      case 0:
        ts.type = TerrainType.FOREST;
        // Since this cell is now a forest, we need to expand from it as well.
        ExpandFromForest(f);
        break;
      case 1:
      case 2:
        ts.type = TerrainType.MARSH;
        break;
      default:
        ts.type = TerrainType.FLATLAND;
      }
    });
  }

  /*
    5.) Each unfilled space surrounding a flatland space has a 20% chance of also being flatland,
    a 10% chance of being a marsh, and a 70% chance of being a beach.
   */
  void ExpandFromFlatlands() {
    log("Expanding from flatlands...");
    WithType(TerrainType.FLATLAND, squares()).forEach(f -> ExpandFromFlatland(f));
  }
  void ExpandFromFlatland(TerrainSquare f) {
    EmptyNeighbors(f).forEach(ts -> {
      switch (r().nextInt(10)) {
      case 0:
      case 1:
        ts.type = TerrainType.FLATLAND;
        ExpandFromFlatland(ts);
        break;
      case 2:
        ts.type = TerrainType.MARSH;
        break;
      default:
        ts.type = TerrainType.BEACH;
      }
    });
  }

  /*
    6.) Marshland acts as a border to edge the island, and must be contiguous with at
    least two other marsh spaces (taking the shortest possible route to achieve that aim).
    Where it borders beach, beaches may be turned into marshes to satisfy this requirement.
   */
  void ConnectMarshes() {
    log("Connecting marshes...");
    long tinyMarshes = WithType(TerrainType.MARSH, squares())
                       .filter(ts -> !TryConnectMarsh(ts)).count();
    if (tinyMarshes > 0) {
      log(String.format("\tWARNING: Had to abandon %d tiny marsh square(s).", tinyMarshes));
    }
  }
  // Returns true if this marsh is now connected.
  boolean TryConnectMarsh(TerrainSquare marshCenter) {
    // Find contiguious region of marsh, and any beaches which border it.
    Set<TerrainSquare> marshRegion = new HashSet<>();
    Set<TerrainSquare> beachBorder = new HashSet<>();
    Queue<TerrainSquare> frontier = new ArrayDeque<>();
    frontier.offer(marshCenter);
    while (!frontier.isEmpty()) {
      TerrainSquare marsh = frontier.poll();
      if (marshRegion.contains(marsh)) continue;
      marshRegion.add(marsh);
      // Bailing out early doesn't help, since we'll still have to check those marshes later.
      Neighbors(marsh).forEach(neighbor -> {
        if (neighbor.type == TerrainType.MARSH) frontier.offer(neighbor);
        if (neighbor.type == TerrainType.BEACH) beachBorder.add(neighbor);
      });
    }
    if (marshRegion.size() >= 3) return true; // Marsh is large enough; move on.

    // Look for beaches which could connect us to another marsh.
    Optional<TerrainSquare> marshConnectingBeach =
      RandomFrom(beachBorder.stream()
                 .filter(beach -> WithType(TerrainType.MARSH, Neighbors(beach))
                         .anyMatch(neighbor -> !marshRegion.contains(neighbor))));
    if (marshConnectingBeach.isPresent()) {
      marshConnectingBeach.get().type = TerrainType.MARSH;
      return true;
    }

    // If there are two nearby beaches, good enough.
    if (beachBorder.size() >= 2) {
      // Make two of them marshes, at random.
      List<TerrainSquare> chosenBeaches = sample(2, beachBorder.stream());
      chosenBeaches.get(0).type = TerrainType.MARSH;
      chosenBeaches.get(1).type = TerrainType.MARSH;
      return true;
    }

    // This solo marsh can't be connected to another marsh, and doesn't have two neighboring beaches.
    // Try chaining one adjacent beach into another.
    if (beachBorder.size() > 0) {
      TerrainSquare beach = beachBorder.iterator().next();
      beach.type = TerrainType.MARSH;
      marshRegion.add(beach);
      if (marshRegion.size() >= 3) return true;

      // TODO(durandal): sample one random element from this stream, instead of building a list.
      Optional<TerrainSquare> grandBeach = RandomFrom(WithType(TerrainType.BEACH, Neighbors(beach)));
      if (grandBeach.isPresent()) {
        grandBeach.get().type = TerrainType.MARSH;
        return true;
      }
    }

    // If we still don't have a big enough marsh, we've run out of ideas. Give up. :(
    return false;
  }

  /*
    7.) Beaches also act as an island border.

    8.) Where borderland is surrounded by other land, it has a 90% chance of becoming
    flatland. Otherwise it remains as-is.
   */
  void FlattenLandlockedBorders() {
    log("Flattening landlocked beaches/marshes...");
    squares().filter(ts -> ts.isBorder())
    .filter(ts -> Neighbors(ts).allMatch(n -> n.isLand()) && r().nextInt(10) != 0)
    .forEach(ts -> ts.type = TerrainType.FLATLAND);
  }

  /*
    9.) Each unfilled space surrounding a borderland-space has a 10% chance of being open
    water, and a 90% chance of being a shoal.
   */
  void ExpandFromBorderlands() {
    log("Expanding from borderlands...");
    squares().filter(ts -> ts.isBorder()).flatMap(ts -> EmptyNeighbors(ts)).forEach(n -> {
      if (r().nextInt(10) == 0)
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
    WithType(TerrainType.OPEN_WATER, squares())
    .filter(ts -> Neighbors(ts).anyMatch(n -> n.isLand()))
    .forEach(ts -> {
      Optional<TerrainSquare> emptyNeighbor = RandomFrom(EmptyNeighbors(ts));
      if (emptyNeighbor.isPresent()) {
        emptyNeighbor.get().type = TerrainType.OPEN_WATER;
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
        if (!hasLand && r().nextInt(10) < 3) {
          int x = r().nextInt(10);
          int y = r().nextInt(10);
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
  void ExpandShoals() {
    log("Expanding shoals...");
    long tinyShoals = WithType(TerrainType.SHOAL, squares()).filter(ts -> !TryExpandShoal(ts)).count();
    if (tinyShoals > 0) log(String.format("\tWARNING: Had to abandon %d tiny shoal(s).", tinyShoals));
    WithType(TerrainType.SHOAL, squares()).forEach(s -> ExpandFromShoal(s));
  }
  // Returns true if this shoal is now part of a size 2+ shoal cluster.
  boolean TryExpandShoal(TerrainSquare ts) {
    Collection<TerrainSquare> neighbors = Neighbors(ts).collect(Collectors.toList());
    if (WithType(TerrainType.SHOAL, neighbors.stream()).count() == 0) {
      // Try empty squares first.
      Optional<TerrainSquare> shoalableNeighbor = RandomFrom(EmptyNeighbors(ts));
      // Failing that, try open water.
      if (!shoalableNeighbor.isPresent())
        shoalableNeighbor = RandomFrom(WithType(TerrainType.OPEN_WATER, neighbors.stream()));
      // Failing that, fail.
      if (!shoalableNeighbor.isPresent()) {
        // log("\tWARNING: had to abandon an isolated shoal at: " + ts);
        return false;
      }
      shoalableNeighbor.get().type = TerrainType.SHOAL;
    }
    return true;
  }
  void ExpandFromShoal(TerrainSquare shoal) {
    EmptyNeighbors(shoal).forEach(ts -> {
      if (r().nextInt(5) == 0) {
        ts.type = TerrainType.SHOAL;
        ExpandFromShoal(ts);
      } else {
        ts.type = TerrainType.OPEN_WATER;
      }
    });
  }

  /*
    13.) Everything else is open water.
   */
  void FillOpenWater() {
    log("Filling in water...");
    WithType(TerrainType.EMPTY, squares()).forEach(ts -> ts.type = TerrainType.OPEN_WATER);
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
    squares().filter(ts -> r().nextInt(100) == 0).forEach(ts -> TryCragify(ts, true));
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
      Neighbors(center, 2).filter(ts -> r().nextInt(10) == 0).forEach(ts -> TryCragify(ts, false));
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
    WithType(TerrainType.OPEN_WATER, squares())
    .flatMap(ts -> OrthoganalNeighbors(ts)).forEach(candidatePort -> {
      if (candidatePort.isLand() && r().nextInt(4) == 0) {
        if (r().nextInt(4) == 0) {
          candidatePort.type = TerrainType.WHARF;
        } else {
          MaybeSpawnCove(candidatePort);
        }
      }
    });

    squares().filter(ts -> ts.isBorder())
    .filter(ts -> WithType(TerrainType.SHOAL, Neighbors(ts)).count() > 0)
    .filter(ts -> r().nextInt(100) == 0)
    .forEach(ts -> MaybeSpawnCove(ts));
  }
  void MaybeSpawnCove(TerrainSquare c) {
    if (!Neighbors(c).anyMatch(n -> n.isPort()))
      c.type = TerrainType.COVE;
  }


  /*
    3.) The map will be divided into 50x50 blocks of squares, and each will have a abbey
    randomly place on the available land within that block.
  */
  void SpawnAbbeys() {
    log("Adding abbeys...");
    IntStream.range(0, width / 50).parallel().forEach(x -> {
      IntStream.range(0, height / 50).parallel().forEach(y -> {
        Optional<TerrainSquare> abbey = RandomFrom(
          IntStream.range(0, 50).boxed().flatMap(
            dx -> IntStream.range(0, 50).boxed().map(
              dy -> grid[x * 50 + dx][y * 50 + dy]))
          .filter(ts -> ts.isLand() && !ts.isCivilized())
        );
        if (abbey.isPresent())
          abbey.get().type = TerrainType.ABBEY;
        else
          log(String.format("\tWARNING: 50x50 square contained no eligible abbey locations: %d, %d", x * 50, y * 50));
      });
    });
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
    Set<TerrainSquare> forbiddenForts = new HashSet<>();

    // Can't just sample numFortsDesired, might reject some and need more.
    List<TerrainSquare> potentialForts =
      sample(
        numFortsDesired * 2,
        squares().filter(ts -> !ts.isWater() && !ts.isCivilized())
        .filter(ts -> ts.type == TerrainType.FLATLAND) // Conservative: try only including flatland
      );

    log("\tnumFortsDesired = " + numFortsDesired);
    log("\tpotentialForts = " + potentialForts.size());
    int fortsConsidered = 0;
    List<TerrainSquare> forts = new ArrayList<>();
    for (TerrainSquare potentialFort : potentialForts) {
      fortsConsidered++;
      if (forbiddenForts.contains(potentialFort)) continue;
      potentialFort.type = TerrainType.FORT;
      forts.add(potentialFort);
      if (--numFortsDesired == 0) break;
      Neighbors(potentialFort, 3).forEach(forbiddenForts::add);
    }
    if (numFortsDesired > 0) {
      log(String.format("\tWARNING: ran out of suitable fort locations with %d unplaced forts.", numFortsDesired));
    } else {
      log(String.format("\tFinished placing forts with %d potential locations remaining.",
                        potentialForts.size() - fortsConsidered));
    }

    log(String.format("\tSanity checking placement of %d forts...", forts.size()));
    // Collections.sort(forts);  // Make nearby forts marginally closer to each other in the list.
    forts.parallelStream().forEach(fort1 -> {
      if (!forts.stream().anyMatch(fort2 -> Distance(fort1, fort2) <= 50))
        log("\tWARNING: fort too far away from nearest neighbor; could be bad luck: " + fort1);
    });
  }

  /*
    5.) Any land space not an abbey, fort, or wharf has a .3% chance of becoming a settlement.
  */
  void SpawnSettlements() {
    log("Adding settlements...");
    squares().filter(ts -> ts.isLand() && !ts.isCivilized() && r().nextInt(1000) < 3)
    .forEach(ts -> ts.type = TerrainType.SETTLEMENT);
    // TODO(durandal): if no settlements spawned, spawn at least one? two? on different land masses?
  }

  public void Genesis() {
    Runnable[] steps = {
      this::SeedIslands,
      this::ExpandFromPeaks,
      this::ExpandFromForests,
      this::ExpandFromFlatlands,
      this::ConnectMarshes,
      this::FlattenLandlockedBorders,
      this::ExpandFromBorderlands,
      this::OpenWater,
      this::SeedShoals,
      this::ExpandShoals,
      this::FillOpenWater,
      // Spec numbering reset here. Unclear what's the significance.
      this::SpawnCrags,
      this::SpawnPorts,
      this::SpawnAbbeys,
      this::SpawnForts,
      this::SpawnSettlements,
    };
    for (Runnable step : steps) {
      Instant start = Instant.now();
      step.run();
      Instant finish = Instant.now();
      log(String.format("\t%d ms", Duration.between(start, finish).toMillis()));
    }
  }

  <T> List<T> sample(int k, Stream<? extends T> stream) {
    List<T> pool = new ArrayList<>(k);
    int n = 0;
    Iterator<? extends T> it = stream.iterator();
    while (it.hasNext()) {
      T e = it.next();
      if (n < k) {
        pool.add(e);
      } else {
        int i = r().nextInt(n);
        if (i < k) {
          pool.set(i, e);
        }
      }
      ++n;
    }
    return pool;
  }

  <T> Optional<T> RandomFrom(Stream<? extends T> input) {
    List<T> sample = sample(1, input);
    if (sample.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(sample.get(0));
    }
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
    squares().forEach(ts -> {
      g.setColor(ts.getColor());
      g.fillRect(ts.x * blockSize, ts.y * blockSize,
      blockSize, blockSize);
      if (blockSize > gridThreshold) {
        g.setColor(Color.black);
        g.drawRect(ts.x * blockSize, ts.y * blockSize,
        blockSize, blockSize);
      }
    });
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
      buf.append(String.format("\t%s:\t%d\n", tt, WithType(tt, squares()).count()));
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
