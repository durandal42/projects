// File: HaresArray.java
// Author: K R Sloan
// Last Modified: 1 January 2014
// Purpose: enumerate grades for "hares"
// This version allows you to specify a word
//  other than "hares" on the command line
import java.io.*;
public class HaresArray
{
    public static void main(String[] args)
	throws FileNotFoundException
    {
	FiveLetterWords flw = new FiveLetterWords(new File("wordList.txt"));
	String guess = "hares";
	if (0 < args.length) guess = args[0];
	for(int correct = 0; correct <=5; correct++)
	    {
		for (int inPlace = 0; inPlace <= 5; inPlace++)
		    {
			int[] LettersAndPlaces = {correct,inPlace};
			FiveLetterWords flw1
			    = new FiveLetterWords(flw,guess,LettersAndPlaces);
			int size = flw1.size();
			System.out.printf(" %6d",size);
		    }
		System.out.printf("\n");
	    }
    }
}