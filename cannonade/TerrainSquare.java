import java.awt.Color;

public class TerrainSquare implements Comparable<TerrainSquare> {

  TerrainType type = TerrainType.EMPTY;
  int x, y;

  public TerrainSquare(int h, int w) {
    x = h;
    y = w;
  }

  public boolean isCivilized() { return type.isCivilized(); }
  public boolean isLand() { return type.isLand(); }
  public boolean isWater() { return type.isWater(); }
  public boolean isBorder() { return type.isBorder(); }
  public boolean isPort() { return type.isPort(); }
  public Color getColor() { return type.getColor(); }

  public String toString() {
    return String.format("(%s,%s)", x, y);
  }

  public int compareTo(TerrainSquare ts) {
    if (ts.x != x) return ts.x - x;
    return ts.y - y;
  }

  public boolean equals(Object other) {
    if (!(other instanceof TerrainSquare)) {
      return false;
    }
    TerrainSquare ts = (TerrainSquare) other;
    return (ts.x == x && ts.y == y);
  }

  public int hashCode() {
    return x + 3749 * y;
  }
}
