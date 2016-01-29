public class FirstDraftAverager implements MeanAngler {

  double distance(double a, double b, double maxAngle) {
    double diff = b - a;
    if (diff < -maxAngle / 2.0) diff += maxAngle;
    if (diff >= maxAngle / 2.0) diff -= maxAngle;
    return diff;
  }

  public double averageAngle(double maxAngle, double[] angles) {
    double sum = 0.0;
    for (double angle : angles) {
      sum += angle;
    }
    double naiveMean = sum / (double) angles.length;
    double adjust = 180.0 / (double) angles.length;

    double bestVariance = Double.POSITIVE_INFINITY;
    double bestCandidate = 0.0;
    for (int i = 0; i < angles.length; i++) {
      double candidate = (naiveMean + (i * adjust)) % maxAngle;

      double leftDistance = 0.0;
      double rightDistance = 0.0;

      for (double angle : angles) {
        double dist = distance(angle, candidate, maxAngle);
        if (dist < 0) leftDistance -= dist;
        if (dist > 0) rightDistance += dist;
      }

      if (leftDistance != rightDistance) continue;

      if (leftDistance < bestVariance) {
        bestVariance = leftDistance;
        bestCandidate = candidate;
      }
    }

    return bestCandidate;
  }
}