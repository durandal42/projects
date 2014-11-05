// File: MinMaxStrategy.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: at each stage, select the word with the best MinMax score
//          as your guess
import java.io.*;
import java.util.*;
public class MinMaxStrategy
{
    public static void main(String[] args)
	throws FileNotFoundException
    {
	FiveLetterWords flw = new FiveLetterWords(new File("wordList.txt"));
	String answer;
	if (0 < args.length) answer = args[0];
	else answer = flw.word(new Random().nextInt(flw.size()));
	System.err.printf("secret answer is \"%s\"\n",answer);
	ArrayList<String> guesses = new ArrayList<String>();
	ArrayList<int[]> grades = new ArrayList<int[]>();
	while (true)
	    {
		String guess = flw.minMax();
		int[] grade = FiveLetterWords.grade(guess, answer);
		guesses.add(guess);	grades.add(grade);
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