import java.util.*;

public class VoltorbBoard {

    public static final int SIZE = 5;

  int[][] board = new int[SIZE][SIZE];

  public String toString() {
    StringBuffer buf = new StringBuffer();
    for(int i = 0; i < SIZE; i++) {
      for(int j = 0; j < SIZE; j++) {
        buf.append(board[i][j]);
        buf.append('\t');
      }
      buf.append(constraints(true).get(i));
      buf.append('\n');
    }
    for(GroupConstraint gc : constraints(false)) {
      buf.append(gc);
      buf.append('\t');
    }
    return buf.toString();
  }

  VoltorbBoard() {
    for(int i = 0; i < SIZE; i++) {
      for(int j = 0; j < SIZE; j++) {
        board[i][j] = -1;  // unknown
      }
    }
  }

  VoltorbBoard copy() {
    VoltorbBoard v = new VoltorbBoard();
    for(int i = 0; i < SIZE; i++) {
      for(int j = 0; j < SIZE; j++) {
        v.board[i][j] = board[i][j];
      }
    }
    return v;
  }

  static Random r = new Random();
  static VoltorbBoard random() {
    VoltorbBoard v = new VoltorbBoard();
    for(int i = 0; i < SIZE; i++) {
      for(int j = 0; j < SIZE; j++) {
        v.board[i][j] = r.nextInt(4);
      }
    }
    return v;
  }

  List<GroupConstraint> constraints(boolean row) {
    List<GroupConstraint> result = new ArrayList<GroupConstraint>(SIZE);
    for(int i = 0; i < SIZE; i++) {
      int coins = 0;
      int orbs = 0;
      int unknown = 0;
      for(int j = 0; j < SIZE; j++) {
        int value = row ? board[i][j] : board[j][i];
        if (value < 0) {
          unknown++;
        } else if (value == 0) {
          orbs++;
        } else {
          coins += value;
        }
      }
      result.add(new GroupConstraint(coins, orbs, unknown));
    }
    return result;
  }
}