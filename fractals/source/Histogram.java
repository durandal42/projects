import java.util.*;

public class Histogram<T extends Comparable<? super T>> {

  private List<T> values = new ArrayList<>();
  private Map<T, Double> normalized = null;

  // Add a point to the histogram.
  void add(T value) {
    values.add(value);
  }

  // Signal that we're done adding values.
  void done() {
    Collections.sort(values);
    double numValues = values.size();
    int valuesSeen = 0;
    normalized = new HashMap<>();
    for (T value : values) {
      normalized.put(value, ++valuesSeen / numValues);
    }
    values = null;
  }

  // What proportion of values seen so far are <= this value?
  double normalize(T value) {
    return normalized.get(value);
  }

  void clear() {
    values = new ArrayList<>();
    normalized = null;
  }
}
