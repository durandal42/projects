public class VectorAverager implements MeanAngler {
  public double averageAngle(double maxAngle, double[] angles) {
    double sumX = 0.0;
    double sumY = 0.0;
    for (double angle: angles) {
      double radians = Math.toRadians(angle / maxAngle * 360.0);
      sumX += Math.cos(radians);
      sumY += Math.sin(radians);
    }
    return Math.toDegrees(Math.atan2(sumY / (double) angles.length,
                                     sumX / (double) angles.length)) / 360.0 * maxAngle;
  }
}