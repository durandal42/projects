public class Timer {

  String description;
  long startTime;
  boolean running;
  
  public Timer(String d) {
    description = d;
    System.out.print("[" + description + "]");
    startTime = System.currentTimeMillis();
    running = true;
  }
  
  public void Stop() {
    if (!running) return;
    long stopTime = System.currentTimeMillis();
    running = false;
    System.out.println(" " + (stopTime - startTime) + "ms.");
  }
}