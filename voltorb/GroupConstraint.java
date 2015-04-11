public class GroupConstraint {
  int coins;
  int orbs;
  int unknown;
  public GroupConstraint(int c, int o, int u) {
    coins = c;
    orbs = o;
    unknown = u;
  }
  public GroupConstraint(int c, int o) {
    coins = c;
    orbs = o;
    unknown = 0;
  }
  public String toString() {
    return "[" + coins + "," + orbs + " (" + unknown + ")]";
  }
}
