import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileReader;
import java.util.*;

public class WordTree {

  public static final int MIN_WORD_LENGTH = 4;

  WordTreeNode root = new WordTreeNode();

  public void addWord(String s) {
    String word = s.toLowerCase();
    String replaced = word.replaceAll("[^a-z]", "");
    if (word.length() < MIN_WORD_LENGTH || !word.equals(replaced)) {
      return;
    }
    root.addWord(word);
  }

  public void printWords() {
    root.printWords();
  }

  public static void main(String[] args) throws Exception {
    WordTree wt = new WordTree();

    System.out.println("Building word tree...");
    BufferedReader br = new BufferedReader(new FileReader(args[0]));
    String line;
    while ((line = br.readLine()) != null) {
      wt.addWord(line);
    }

    System.out.println("Calculating game tree...");
    wt.root.calculateWins();
    //	wt.printWords();

    System.out.println("Sample game:");
    WordTreeNode wtn = wt.root;
    while (!(wtn = play(wtn, true)).isWord) {}

    System.out.println("Your turn. Input a single letter or press enter to let the computer go first. Ctrl-D to quit.");
    br = new BufferedReader(new InputStreamReader(System.in));
    WordTreeNode node = wt.root;
    while ((line = br.readLine()) != null) {
      if (node == wt.root && line.length() == 0) {
        node = play(node, false);
        continue;
      }
      if (line.length() == 0) {
        System.out.println("The following are suffixes which complete that prefix:");
        node.printWords();
        System.out.println("(You lose.)");
        return;
      }

      char letter = line.toLowerCase().charAt(0);
      node = node.children[(int)(letter - 'a')];
      if (node == null) {
        System.out.println("No valid word with that prefix. You lose.");
        return;
      }
      if (node.isWord) {
        System.out.println("You have completed a word. You lose.");
        return;
      }
      node = play(node, false);
      if (node.isWord) {
        System.out.println("I have completed a word. I lose.");
        return;
      }
    }
  }

  static WordTreeNode play(WordTreeNode node, boolean random) {
    Map<Character, Integer> legal = new TreeMap<Character, Integer>();
    Map<Character, Integer> winning = new TreeMap<Character, Integer>();;
    boolean winPossible = false;

    for (int i = 0 ; i < 26 ; i++) {
      if (node.children[i] != null) {
        char letter = (char)('a' + i);
	int score = node.children[i].score;
	legal.put(letter, score);
      }
    }

    //	System.out.println("\tLegal moves: " + legal);
    //	System.out.println("\tWinning moves: " + winning);

    Map<Character, Integer> moves = (winning.size() > 0) ? winning : legal;
    String message = (winning.size() > 0)
	? "\t(My victory is assured.) "
	: "\t(Hurry up and beat me.) ";

    if (random) {
      Random r = new Random();
      for (Character c : legal.keySet()) {
	moves.put(c, r.nextInt());
      }
      message = "\t(I'm so random!) ";
    }

    int max_score = Integer.MIN_VALUE;
    char letter = ' ';
    if (moves.size() == 0) throw new RuntimeException();
    for (Character c : moves.keySet()) {
      int score = moves.get(c);
      System.out.println("\t" + c.charValue() + " -> " + score);
      if (score > max_score) {
	max_score = score;
	letter = c;
      }
    }
    System.out.println(letter + message + max_score);
    return node.children[(int) (letter - 'a')];
  }

}

class WordTreeNode {
  boolean winByPlaying = false;
  int score;

  boolean isWord = false;
  WordTreeNode[] children = new WordTreeNode[26];

  public void addWord(String word) {
    if (word.length() == 0) {
      isWord = true;
    }
    if (isWord) {
      for(int i = 0 ; i < 26 ; i++) {
        children[i] = null;
      }
      return;
    }
    char firstChar = word.charAt(0);
    String rest = word.substring(1);
    int index = (int) (firstChar - 'a');
    if (children[index] == null) {
      children[index] = new WordTreeNode();
    }
    children[index].addWord(rest);
  }

  public void printWords() {
    printWords("");
  }
  public void printWords(String prefix) {
    if (isWord) {
      System.out.println(prefix);
    }
    for (int i = 0 ; i < 26 ; i++) {
      if (children[i] != null) {
        children[i].printWords(prefix + (char)('a' + i));
      }
    }
  }

  boolean calculateWins() {
    if (isWord) {
      winByPlaying = false;
      score = 0;
      return false;
    }
    winByPlaying = true;
    int scoreFromWinning = Integer.MAX_VALUE;
    int scoreFromLosing = Integer.MAX_VALUE;
    for (WordTreeNode child : children) {
      if (child == null) continue;

      boolean childWins = child.calculateWins();
      if (childWins) winByPlaying = false;

      int scoreFromChild = 100 - child.score;
      if (childWins) {
	scoreFromLosing = Math.min(scoreFromLosing, scoreFromChild + 1);
      } else {
	scoreFromWinning = Math.min(scoreFromWinning, scoreFromChild - 1);
      }
    }
    score = winByPlaying ? scoreFromWinning : scoreFromLosing;
    return winByPlaying;
  }

}
