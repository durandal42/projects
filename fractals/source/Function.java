// A differentiable function.
public interface Function {
  // Apply this function to an input.
  public Complex apply(Complex input);

  // The derivative of this function.
  public Function differentiate();
}
