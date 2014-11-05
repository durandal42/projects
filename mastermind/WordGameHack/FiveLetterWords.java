// File: FiveLetterWords.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: maintain sets of 5-letter words (with no repeated letters)
//          and perform useful MasterMind-like operations on them
import java.io.*;
import java.util.*;
public class FiveLetterWords
{
    private ArrayList<String> words;
    public FiveLetterWords(InputStream is)
    {
	words = new ArrayList<String>();
	Scanner sc = new Scanner(is).useDelimiter("(\\s+)|(\\s*,\\s*)");
	while(sc.hasNext())
	    {
		String s = sc.next();
		if (5 != s.length()) continue;
		if (repeats(s)) continue;
		words.add(s);
	    }
    }
    public FiveLetterWords(File f)
	throws FileNotFoundException
    {
	words = new ArrayList<String>();
	Scanner sc = new Scanner(f).useDelimiter("(\\s+)|(\\s*,\\s*)");
	while(sc.hasNext())
	    {
		String s = sc.next();
		if (5 != s.length()) continue;
		if (repeats(s)) continue;
		words.add(s);
	    }
    }
    public FiveLetterWords(FiveLetterWords flw, 
			   String word, int[] LettersAndPlaces)
    {
	words = new ArrayList<String>();
	for(String s : flw.words) 
	    {
		if(word.equals(s)) continue; 
		int[] grade = grade(word,s);
		if ( (LettersAndPlaces[0] == grade[0])
		     && (LettersAndPlaces[1] == grade[1]))
		    this.words.add(s);
	    }
    }
    public static boolean repeats(String word)
    {
	for(int i = 0; i < word.length()-1; i++)
	    {
		char first = word.charAt(i);
		for(int j=i+1; j < word.length(); j++)
		    if (word.charAt(j) == first) return true;
	    }
	return false;
    }

    // return the word with the best MinMax score
    public String minMax()
    {
	String minMaxGuess = "";
	int n = this.size();
	int minMaxN = n;

	for(int g = 0; g < n; g++)
	    {
		int[][]buckets = new int[6][6];
		for(int i = 0; i < 6; i++)
		    for(int j = 0; j < 6; j++) buckets[i][j] = 0;
		String guess = this.word(g);
		int maxN = 0;
		for(int a = 0; a < n; a++)
		    {
			if (a == g) continue;
			String answer = this.word(a);
			int[] grade = this.grade(guess,answer);
			buckets[grade[0]][grade[1]]++;
		    }
		int thisMaxN = 0;
		for(int i = 0; i < 6; i++)
		    for(int j = 0; j < 6; j++)
			{
			    int thisN = buckets[i][j];
			    if (thisN > thisMaxN) thisMaxN = thisN;
			}
		if (thisMaxN < minMaxN)
		    {
			minMaxN = thisMaxN;
			minMaxGuess = guess;
		    }
	    }
	return minMaxGuess;
    }

    public int size()         { return words.size(); }
    public String word(int i) { return words.get(i); }

    public String toString()
    {
	StringBuffer result = new StringBuffer();
	for(String s : words) result = result.append(s+"\n");
	return result.toString();
    }
  public static int grades_performed = 0;
    public static int[] grade(String guess, String answer)
    {
	if (guess.equals("")) throw new RuntimeException("grade: guess is null");
	if (answer.equals("")) throw new RuntimeException("grade: answer is null");
	int[] result = {0,0};
	for(int i = 0; i < 5; i++)
	    {
		char guessC = guess.charAt(i);       
		for(int j = 0; j < 5; j++)
		    {
			char answerC = answer.charAt(j);
			if (guessC == answerC) 
			    {
				result[0]++;
				if (i == j) result[1]++;
			    }
		    }
	    }
        grades_performed++;
	return result;
    }
    public static void main(String[] args)
	throws FileNotFoundException
    {
	FiveLetterWords flw = new FiveLetterWords(new File("wordList.txt"));
	System.out.printf("word list contains %d five letter words\n",
			  flw.size());
	String guess = flw.minMax();
	System.out.printf("minMax says to guess \"%s\"\n",guess);
	String answer = "hasty";
	int[] LettersAndPlaces = grade(guess,answer);
	FiveLetterWords flw1 = new FiveLetterWords(flw,guess,LettersAndPlaces);
	System.out.printf(
	   "wordlist has %d MORE words which grade guess \"%s\" as [%d,%d]\n",
	   flw1.size(),guess,LettersAndPlaces[0],LettersAndPlaces[1]);
    }
}
