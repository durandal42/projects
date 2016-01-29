import java.util.*;

public class MeanAnglerTest { 
  public static void main(String[] args) {
    exerciseAngler(new FirstDraftAverager(), "FirstDraftAverager");
    exerciseAngler(new VectorAverager(), "VectorAverager");
  }

  static void exerciseAngler(MeanAngler angler, String name) {
      System.out.println(name + ":");
      System.out.println("90:\t" + angler.averageAngle(180.0, new double[] {89.0, 91.0}));
      System.out.println("0:\t" + angler.averageAngle(180.0, new double[] {1.0, 179.0}));
      System.out.println("??:\t" + angler.averageAngle(180.0, new double[] {0.0, 90.0, 45.0, 135.0}));
  }
}