import java.util.*;

public class UnionFind {

  public boolean equals(Object a, Object b) {
    return equals(getNode(a), getNode(b));
  }

  public void union(Object a, Object b) {
    union(getNode(a), getNode(b));
  }

  private static class UFNode {
    public UFNode parent = null;
  }

  private Map<Object, UFNode> nodes = new HashMap<Object, UFNode>();

  private UFNode getNode(Object o) {
    if (!nodes.containsKey(o)) {
      nodes.put(o, new UFNode());
    }
    return nodes.get(o);
  }

  private static boolean equals(UFNode a, UFNode b) {
    return find(a) == find(b);
  }

  private static void union(UFNode a, UFNode b) {
    a = find(a);
    b = find(b);
    if (a != b) a.parent = b;
  }

  private static UFNode find(UFNode a) {
    if (a.parent == null) return a;
    a.parent = find(a.parent);
    return a.parent;
  }

}
