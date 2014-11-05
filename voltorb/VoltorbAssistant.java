import java.util.*;
import java.io.*;

public class VoltorbAssistant {

  static List<VoltorbBoard> fromConstraints(List<GroupConstraint> rows,
                                            List<GroupConstraint> cols,
                                            Map<Probe,Integer> discoveries) {
    List<VoltorbBoard> result = new LinkedList<VoltorbBoard>();
    VoltorbBoard v = new VoltorbBoard();
    for(Map.Entry<Probe,Integer> e : discoveries.entrySet()) {
	Probe p = e.getKey();
	v.board[p.row][p.col] = e.getValue();
    }
    fromConstraints(rows, cols, result, v, 0);
    return result;
  }

  static void fromConstraints(List<GroupConstraint> rows,
                              List<GroupConstraint> cols,
                              List<VoltorbBoard> result,
                              VoltorbBoard incomplete,
                              int filled) {
    int row = filled / VoltorbBoard.SIZE;
    int col = filled % VoltorbBoard.SIZE;
    if (inconsistent(incomplete, rows, cols)) {
      return;
    }
    if (filled == VoltorbBoard.SIZE * VoltorbBoard.SIZE) {
      result.add(incomplete);
      if ((result.size() & (result.size() - 1)) == 0) {
	  //	  System.out.println("Generated " + result.size() + " boards so far...");
      }
      return;
    }
    if (incomplete.board[row][col] != -1) {  // already filled this square
      fromConstraints(rows, cols, result, incomplete, filled+1);
      return;
    }
    for (int i = 0 ; i < 4; i++) {
      VoltorbBoard copy = (i < 3) ? incomplete.copy() : incomplete;
      copy.board[row][col] = i;
      fromConstraints(rows, cols, result, copy, filled+1);
    }
  }

  static boolean inconsistent(VoltorbBoard vb,
                              List<GroupConstraint> rows,
                              List<GroupConstraint> cols) {
    List<GroupConstraint> rowLowerBounds = vb.constraints(true);
    List<GroupConstraint> colLowerBounds = vb.constraints(false);
    for (int i = 0; i < VoltorbBoard.SIZE; i++) {
      if (!checkConstraint(rowLowerBounds.get(i), rows.get(i)) ||
          !checkConstraint(colLowerBounds.get(i), cols.get(i))) {
        return true;
      }
    }
    return false;
  }

  static boolean checkConstraint(GroupConstraint lower,
                                 GroupConstraint target) {
    int deltaCoins = target.coins - lower.coins;
    int deltaOrbs = target.orbs - lower.orbs;
    int unknowns = lower.unknown;
    if (deltaCoins < 0 || deltaOrbs < 0) {
      return false;  // exceeded target
    }
    if (unknowns == 0 &&
        (deltaCoins != 0 || deltaOrbs != 0)) {
      return false;  // didn't hit target
    }
    if (deltaCoins / 3 + deltaOrbs > unknowns) {
      return false;  // can't catch target
    }
    if (deltaCoins + deltaOrbs < unknowns) {
      return false;  // can't avoid going past target
    }
    return true;
  }

  static void filterByDiscovery(Discovery d, List<VoltorbBoard> list) {
      //    System.out.println("Removing possibilities where [" +
      //                       d.probe.row + "," + d.probe.col + "] does not equal " + d.val);
    Iterator<VoltorbBoard> itr = list.iterator();
    while(itr.hasNext()) {
      if (itr.next().board[d.probe.row][d.probe.col] != d.val) {
        itr.remove();
      }
    }
  }

    static void filterByLevel(int level, List<VoltorbBoard> list) {
	boolean removed = false;
	Iterator<VoltorbBoard> itr = list.iterator();
	while(itr.hasNext()) {
	    VoltorbBoard v = itr.next();
	    int score = 1;
	    for(Probe p : Probe.AllProbes()) {
		int val = v.board[p.row][p.col];
		if (val != 0) score *= val;
	    }
	    if (!possibleScoreAtLevel(score, level)) {
		removed = true;
		itr.remove();
	    }
	}
	if (removed) System.out.println("level filter still useful");
    }
    static boolean possibleScoreAtLevel(int score, int level) {
	switch(level) {
	case 1: return (20 <= score && score <= 50);
	case 2: return (50 <= score && score <= 100);
	case 3: return (100 <= score && score <= 200);
	case 4: return (200 <= score && score <= 400);
	case 5: return (384 <= score && score <= 600);
	case 6: return (600 <= score && score <= 1000);
	case 7: return (1000 <= score && score <= 2000);
	case 8: return (2000 <= score && score <= 3000);
	default: return true;
	}
    }
    
    static Map<Probe,Histogram> histo(List<VoltorbBoard> list) {
	return histo(list, Probe.AllProbes());
    }

    static Map<Probe,Histogram> histo(List<VoltorbBoard> list, Collection<Probe> probes) {
	Map<Probe,Histogram> result = new HashMap<Probe,Histogram>();
	for (Probe p : probes) {
	    Histogram h = new Histogram();
	    for(VoltorbBoard v : list) {
		h.inc(v.board[p.row][p.col]);
	    }
	    result.put(p, h);
	}
	return result;
    }

    static Evaluation bestProbe(List<VoltorbBoard> list, int level, Map<Probe,Integer> discoveries, double relevance) {
	final boolean covered = level <= discoveries.size();
	final Map<Probe,Histogram> histo = histo(list);
	Evaluation result = new Evaluation();
	TreeSet<Probe> sortedProbes = new TreeSet(new Comparator<Probe>() {
		public int compare(Probe p1, Probe p2) {
		    double delta = histo.get(p1).eval(covered) - histo.get(p2).eval(covered);
		    if (delta < 0) return 1;
		    if (delta > 0) return -1;
		    return p1.compareTo(p2);
		}
	    });
	sortedProbes.addAll(Probe.AllProbes());
	int probesConsidered = 0;
	for(Probe p : sortedProbes) {
	    double eval = histo.get(p).eval(covered);
	    if (eval <= 0.0 ||
		discoveries.containsKey(p)) {
		continue;
	    }
	    //	    if (relevance == 1.0 && eval >= 1.0) {
	    //		result.addScore(p, eval);
	    //		return result;
	    //	    }

	    probesConsidered++;
	    Histogram h = histo.get(p);
	    double score = 0.0;
	    double remainingProb = 1.0;
	    for(int i = 0; i < 4; i++) {
		double prob = h.getProbability(i);
		remainingProb -= prob;
		if (prob == 0.0) continue;
		if (i == 0) {
		    int delevel = level - discoveries.size();
		    if (delevel > 0) {
			score -= prob * delevel;
		    }
		    continue;
		}
		List<VoltorbBoard> hList = new LinkedList<VoltorbBoard>();
		hList.addAll(list);
		filterByDiscovery(new Discovery(p, i), hList);
		Map<Probe,Integer> hDisc = new HashMap<Probe,Integer>();
		hDisc.putAll(discoveries);
		hDisc.put(p, i);
		score += prob * bestProbe(hList, level, hDisc, relevance * prob).bestScore;

		//		if (result.bestScore - score > remainingProb) {
		//		    break;
		//		}
	    }
	    result.addScore(p, score);
	    int maxProbes = (int)(relevance * 4);
	    if (probesConsidered >= maxProbes) {
		break;
	    }
	}
	if (result.bestProbe == null) {
	    result.bestScore = 1.0;
	}
	return result;
    }

  static void printKnowledge(List<VoltorbBoard> list) {
    StringBuffer buf = new StringBuffer();

    buf.append("# of other boards that match these constraints:\t");
    buf.append(list.size());
    buf.append('\n');

    buf.append("% chance of making progress by exploring: ");
    Map<Probe,Histogram> histo = histo(list);
    for(int i = 0; i < VoltorbBoard.SIZE; i++) {
      for(int j = 0; j < VoltorbBoard.SIZE; j++) {
	  Histogram h = histo.get(new Probe(i,j));
        buf.append(h);
        buf.append('\t');
      }
      buf.append('\n');
    }

    VoltorbBoard v = list.get(0);
    int coins = 0;
    int orbs = 0;
    for(GroupConstraint gc : v.constraints(true)) {
      coins += gc.coins;
      orbs += gc.orbs;
    }
    buf.append("Total coins:\t");
    buf.append(coins);
    buf.append('\n');
    buf.append("Total orbs:\t");
    buf.append(orbs);

    System.out.println(buf);
  }
}
