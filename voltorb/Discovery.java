import java.util.*;

public class Discovery {
    Probe probe;
    int val;
    public Discovery(int r, int c, int v) {
        this(new Probe(r, c), v);
    }
    public Discovery(Probe p, int v) {
        probe = p;
        val = v;
    }
}

class Probe implements Comparable<Probe> {
    int row;
    int col;
    public Probe(int r, int c) {
        row = r;
        col = c;
    }
    public int compareTo(Probe other) {
        return hashCode() - other.hashCode();
    }
    public int hashCode() {
        return row + VoltorbBoard.SIZE * col;
    }
    public boolean equals(Object other) {
        return hashCode() == ((Probe) other).hashCode();
    }
    static List<Probe> AllProbes() {
        List<Probe> probes = new ArrayList<Probe>(VoltorbBoard.SIZE * VoltorbBoard.SIZE);
        for(int i = 0; i < VoltorbBoard.SIZE; i++) {
            for(int j = 0; j < VoltorbBoard.SIZE; j++) {
                probes.add(new Probe(i,j));
            }
        }
        return probes;
    }
}

class Evaluation {
    Probe bestProbe = null;
    double bestScore = Double.MIN_VALUE;;
    Map<Probe,Double> scores = new HashMap<Probe,Double>();
    boolean addScore(Probe p, double score) {
        scores.put(p, score);
        if (bestProbe == null || score > bestScore) {
            bestProbe = p;
            bestScore = score;
            return true;
        }
        return false;
    }
}