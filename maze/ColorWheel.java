import java.awt.Color;

public interface ColorWheel {
  Color colorAt(float f);
    
  public static ColorWheel white() {
    return (f) -> Color.white;
  }

  public static ColorWheel rainbow() {
    return (f) -> Color.getHSBColor(f, 1.0f, 1.0f);
  }

  public static ColorWheel tertiary() {
    float numColors = 12.0f;
    return (f) -> Color.getHSBColor((float) Math.floor(f*numColors)/numColors, 1.0f, 1.0f);
  }

  public static ColorWheel gradient(final Color[] colors) {
    return (f) -> {
      int firstIndex = ((int) Math.floor(f * colors.length) + colors.length) % colors.length;
      int secondIndex = (firstIndex + 1) % colors.length;
      float gradient = (f * colors.length) % 1.0f;
      return ColorWheel.interpolate(colors[firstIndex], colors[secondIndex], gradient);
    };
  }

  public static Color interpolate(Color c1, Color c2, float gradient) {
    float[] c1rgb = c1.getRGBColorComponents(null);
    float[] c2rgb = c2.getRGBColorComponents(null);
    float r = c1rgb[0] * (1.0f - gradient) + c2rgb[0] * gradient;
    float g = c1rgb[1] * (1.0f - gradient) + c2rgb[1] * gradient;
    float b = c1rgb[2] * (1.0f - gradient) + c2rgb[2] * gradient;
    if (r<0 || r > 1 || g < 0 || g > 1 || b < 0 || b > 1) {
      System.err.println(r + ", " + g + ", " + b);
    }
    return new Color(r, g, b);
  }

  public static ColorWheel nafi() {
    return (f) -> new Color(0.0f, f, 1.0f);
  }

  public static Color TAN = new Color(0xD2B48C);
  public static Color BROWN = new Color(0x4E2E28);
  public static Color FOREST_GREEN = new Color(0x228b22);
  public static Color DARK_FOREST_GREEN = new Color(0x114511);
  public static Color DARK_TAN = new Color(0x918151);
  public static Color KHAKI = new Color(0xC3B091);
  public static Color TEAL = new Color(0x008080);
  public static Color PURPLE = new Color(0x800080);
  

  public static ColorWheel fromName(String name) {
    if (name == null) return white();
    if (name.equals("rainbow")) return rainbow();
    if (name.equals("nafi")) return nafi();
    if (name.equals("tertiary")) return tertiary();
    if (name.equals("annie")) return gradient(new Color[] { new Color(0xb04127),
                                                            new Color(0xd09921),
                                                            new Color(0x76a52c),
                                                            new Color(0x10827b),
                                                            new Color(0x574090),
                                                            new Color(0x6c2e65)
                                                          });
    if (name.equals("yael")) return gradient(new Color[] { Color.yellow, Color.orange, Color.pink });
    if (name.equals("elwyn")) return gradient(new Color[] { Color.white, Color.yellow, Color.pink });
    if (name.equals("rgb")) return gradient(new Color[] { Color.red, Color.green, Color.blue });
    if (name.equals("camo_woodland")) return gradient(new Color[] { TAN, FOREST_GREEN, BROWN, Color.black });
    if (name.equals("camo_desert")) return gradient(new Color[] { TAN, DARK_TAN, KHAKI, BROWN});
    if (name.equals("kayli")) return gradient(new Color[] { TEAL, DARK_FOREST_GREEN, PURPLE});
    if (name.equals("becky")) return gradient(new Color[] { new Color(177, 140, 193),  // lavender
							    new Color(111, 210, 135),  // mint green
							    new Color( 36, 160, 209),  // muted blue
	});

    return white();
  }

}