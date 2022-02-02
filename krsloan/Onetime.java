// File: Onetime.java
// Author: K R Sloan
// Last Modified: 2 December 2021
// Purpose: investigate gambling game
import java.util.*;
public class Onetime
{
    public static void main(String[] args)
    {
        for (int i = 0 ; i < 1000; i++) {
            Random random = new Random();

            double stake = 1000.0;
            if(1 <= args.length) stake = Double.parseDouble(args[0]);

            int iteration;
            for(iteration=1;stake>=1.0;iteration++)
                {
                    double r = random.nextDouble();
                    if(r <= 2.0/3.0)
                        {
                            stake *= 5.0/3.0;
                        }
                    else
                        {
                            stake *= 1.0/3.0;
                        }
                }
            // System.out.printf("%5d %22.19f\n",iteration,stake);
            // System.out.printf("BUST\n");
            System.out.println(iteration);
        }
    }
}
