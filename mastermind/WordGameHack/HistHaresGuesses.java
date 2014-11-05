// File: HistHaresGuesses.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: histogram the number of guesses taken by HaresStrategy
//          (use "hares" as the first guess and then use MinMax)
//          as a byproduct, report on cached second guesses for every
//          possible grade given to "hares" on the first guess
//          These will form the basis of our final Strategy
//          now commented out
import java.io.*;
import java.util.*;
public class HistHaresGuesses
{
    private static String[][] secondGuess;

    public static int guesses(FiveLetterWords flwIn, String answer)
    {
	FiveLetterWords flw = flwIn; // don't modify caller's version
	ArrayList<String> guesses = new ArrayList<String>();
	ArrayList<int[]> grades = new ArrayList<int[]>();
	while (true)
	    {
		String guess = "";
		int[] grade = {0,0};
		int guessN = guesses.size();
		if (0 == guessN) guess = "hares";
		if (1 == guessN)
		    {
			int[] firstGrade = grades.get(0);
			guess = secondGuess[firstGrade[0]][firstGrade[1]];
		    }
		if (guess.equals("")) 
		    {
			guess = flw.minMax();
			if (1 == guessN)
			    {
				int[] firstGrade = grades.get(0);
				secondGuess[firstGrade[0]][firstGrade[1]] = guess;
			//	System.err.printf("secondGuess[%d][%d] = \"%s\";\n",
			//                        firstGrade[0],firstGrade[1],guess);
			    }
		    }
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
	secondGuess = new String[6][6];
	for(int i = 0; i < 6; i++)
	    for(int j = 0; j < 6; j++)
		secondGuess[i][j] = "";
	for(int i = 0; i < flw.size(); i++)
	    {
		String answer = flw.word(i);
		int nGuesses = guesses(flw, answer);
		tally(nGuesses, answer);
	    }
	for(int i = histogramMin; i <= histogramMax; i++)
	    {
		System.out.printf("%5s %3d : %d\n",example[i],i,histogram[i]);
	    }
	System.out.printf("mean value = %f\n",
			  (double)histogramSum/(double)histogramN);
    }
}