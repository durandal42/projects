import java.awt.Color;

public class TerrainSquare implements Comparable {

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
    StringBuffer buf = new StringBuffer();
    buf.append("(");
    buf.append(x);
    buf.append(",");
    buf.append(y);
    buf.append(")");
    return buf.toString();
  }

  public int compareTo(Object other) {
    if (other instanceof TerrainSquare) {
      TerrainSquare ts = (TerrainSquare) other;
      if (ts.x != x) return ts.x - x;
      return ts.y - y;
    } else {
      return -1;
    }
  }

  public boolean equals(Object other) {
    if (other instanceof TerrainSquare) {
      TerrainSquare ts = (TerrainSquare) other;
      return (ts.x == x && ts.y == y);
    } else {
      return false;
    }
  }

  public int hashCode() {
    return x + 3749 * y;
  }
}
