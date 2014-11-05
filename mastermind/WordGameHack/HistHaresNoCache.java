// File: HistHaresNoCache.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: histogram the number of guesses taken by a really dumb method:
//          use "hares" as the first guess and then use MinMax
//          with NO CACHING
import java.io.*;
import java.util.*;
public class HistHaresNoCache
{
    public static int guesses(FiveLetterWords flw, String answer)
    {
	ArrayList<String> guesses = new ArrayList<String>();
	ArrayList<int[]> grades = new ArrayList<int[]>();
	while (true)
	    {
		String guess = "";
		int[] grade = {0,0};
		int guessN = guesses.size();
		if (0 == guessN) guess = "hares";
		if (guess.equals("")) guess = flw.minMax();
		grade = FiveLetterWords.grade(guess, answer);
		guesses.add(guess);	grades.add(grade);
		if ((5 == grade[0]) && (5 == grade[1])) break;
		flw = new FiveLetterWords(flw, guess, grade);
	    }
	return guesses.size();
    }
    private static int[] histogram = new int[100]; // big enough
    private static String[] example = new String[100];
    private static int histogramSum = 0;
    private static int histogramN = 0;
    private static int histogramMin = 100;
    private static int histogramMax = -1;
    private static void tally(int n, String answer)
    {
      System.out.println(answer + ": " + n);
	if (example[n].equals("")) example[n] = answer;
	histogram[n]++;
	histogramSum += n;
	histogramN++;
	if (n < histogramMin) histogramMin = n;
	if (n > histogramMax) histogramMax = n;
    }
    public static void main(String[] args)
	throws FileNotFoundException
    {
	for(int i = 0; i < 100; i++) example[i] = "";
	FiveLetterWords flw = new FiveLetterWords(new File("wordList.txt"));
	for(int i = 0; i < 10 /* flw.size()*/; i++)
	    {
		String answer = flw.word(i);
		int nGuesses = guesses(flw, answer);
		tally(nGuesses, answer);
	    }
        System.out.println("Grades performed: " + flw.grades_performed);
	for(int i = histogramMin; i <= histogramMax; i++)
	    {
		System.out.printf("%5s %3d : %d\n",example[i],i,histogram[i]);
	    }
	System.out.printf("mean value = %f\n",
			  (double)histogramSum/(double)histogramN);
    }
}