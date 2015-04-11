public class Histogram {
  private int[] values = new int[4];
  private int total = 0;

  static java.text.DecimalFormat df = new java.text.DecimalFormat("0.00");
  public String toString() {
    StringBuffer buf = new StringBuffer();
    buf.append('[');
    for(int i = 0; i < values.length; i++) {
      if (i > 0) buf.append(',');
      buf.append(df.format((double) values[i] / (double) total));
    }
    return buf.toString();
  }

  public double getProbability(int index) {
    return (double) values[index] / (double) total;
  }
  public void inc(int index) {
    values[index]++;
    total++;
  }

  double eval(boolean covered) {
    if (values[0] == total) {
      return -1.0;
    }

    if (values[0] == 0 && values[1] < total) {
      // guaranteed non-orb
      return (1 * getProbability(1) +
              2 * getProbability(2) +
              3 * getProbability(3);
    }

    if (covered) {
      // chance of a mutliplier
      return getProbability(2) + getProbability(3);
    } else {
      // chance of a non-orb
      return 1.0 - getProbability(0);
    }
  }
}
