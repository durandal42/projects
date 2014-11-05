// File: SecondGuessStrategy.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: first guess is "hares"
//          second guess is chosen based on the grade assigned to "hares"
//          at each subsequent stage, select the word with the best MinMax score
import java.io.*;
import java.util.*;
public class SecondGuessStrategy
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
    public static void main(String[] args)
	throws FileNotFoundException
    {
	FiveLetterWords flw = new FiveLetterWords(new File("wordList.txt"));
	initSecondGuess();
	String answer;
	if (0 < args.length) answer = args[0];
	else answer = flw.word(new Random().nextInt(flw.size()));
	System.err.printf("secret answer is \"%s\"\n",answer);
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
		guesses.add(guess);
		grades.add(grade);
		int n = guesses.size();
		System.err.printf("guess %d is \"%s\", grade = [%d,%d]",
				  n, guesses.get(n-1), 
				  grades.get(n-1)[0], grades.get(n-1)[1]);
		if ((5 == grade[0]) && (5 == grade[1])) break;
		flw = new FiveLetterWords(flw, guess, grade);
		System.err.printf(", size of new word list = %d\n",flw.size());
	    }
	System.err.printf(" ***BINGO***\n");
	int n = guesses.size();
	String myAnswer = guesses.get(n-1);
	System.out.printf("Guessed secret word \"%s\" in %d guesses\n",
			  myAnswer, n);
	if (answer.equals(myAnswer) )
	    System.err.printf("Answer is correct!\n");
	    else
		System.err.printf("but the right answer is \"%s\"\n",answer);
    }
}