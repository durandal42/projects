// File: HistSecondGuesses.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: histogram the number of guesses taken by the SecondGuess Strategy
//          use "hares" as the first guess and then use MinMax
//          use a table of secondGuesses based on the result of the first
import java.io.*;
import java.util.*;
public class HistSecondGuesses
{
    private static String[][] secondGuess;
    private static void initSecondGuess()
    {
	secondGuess = new String[6][6];
	for(int i = 0; i < 6; i++)
	    for(int j = 0; j < 6; j++) 
		secondGuess[i][j] = "";
	secondGuess[3][1] = "blahs";
	secondGuess[3][0] = "trade";
	secondGuess[2][0] = "blate";
	secondGuess[2][1] = "doats";
	secondGuess[3][2] = "ratel";
	secondGuess[1][0] = "boite";
	secondGuess[4][2] = "baser";
	secondGuess[4][3] = "races";
	secondGuess[4][1] = "dears";
	secondGuess[4][0] = "prase";
	secondGuess[2][2] = "dines";
	secondGuess[1][1] = "coins";
	secondGuess[3][3] = "dales";
	secondGuess[4][4] = "dares";
	secondGuess[0][0] = "dungy";
	secondGuess[5][2] = "hears";
	secondGuess[5][1] = "rheas";
	secondGuess[5][0] = "share";
    }
    public static int guesses(FiveLetterWords flw, String answer)
    {
	ArrayList<String> guesses = new ArrayList<String>();
	ArrayList<int[]> grades = new ArrayList<int[]>();
	while (true)
	    {
		String guess = "";
		int guessN = guesses.size();
		if (0 == guessN) guess = "hares";
		if (1 == guessN)
		    {
			int[] firstGrade = grades.get(0);
			guess = secondGuess[firstGrade[0]][firstGrade[1]];
		    }
		if (guess.equals("")) guess = flw.minMax();
		int[] grade = FiveLetterWords.grade(guess, answer);
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
	initSecondGuess();
	for(int i = 0; i < flw.size(); i++)
	    {
		String answer = flw.word(i);
		FiveLetterWords flwIn = flw;
		int nGuesses = guesses(flwIn, answer);
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