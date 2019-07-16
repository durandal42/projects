import java.awt.Color;

public enum TerrainType {
    EMPTY, PEAK, FOREST, FLATLAND, BEACH, MARSH, SHOAL, OPEN_WATER, CRAG, WHARF, COVE, ABBEY, FORT, SETTLEMENT;
    
    public Color getColor() {
	switch (this) {
	case EMPTY: return Color.white;
	case PEAK: return new Color(102,102,102); // dark gray
	case FOREST: return new Color(0,102,0); // dark green
	case FLATLAND: return new Color(0,255,0); // light green
	case BEACH: return new Color(255,255,0); // pale yellow
	case MARSH: return new Color(153,153,0); // olive green
	case SHOAL: return new Color(0,255,255); // light blue
	case OPEN_WATER: return new Color(0,0,255); // navy blue
	case CRAG: return new Color(51,0,0); // dark brown
	case WHARF: return new Color(102,51,0); // brown
	case COVE: return new Color(0,153,153); // sea green
	case ABBEY: return new Color(176,48,96); // maroon
	case FORT: return new Color(255,0,0); // varies! faction-specific?
	case SETTLEMENT: return new Color(204,153,102); // tan
	default: return null;
	}
    }
    
    public boolean isCivilized() {
	return (this == ABBEY ||
		this == FORT ||
		this == SETTLEMENT ||
		this == WHARF);
    }
    
    public boolean isLand() {
	return (this == PEAK ||
		this == FOREST ||
		this == FLATLAND ||
		this == BEACH ||
		this == MARSH ||
		isCivilized() ||
		isPort());
    }
    
    public boolean isWater() {
	return (this == OPEN_WATER ||
		this == SHOAL ||
		this == CRAG ||
		isPort());
    }
    public boolean isBorder() {
	return (this == BEACH || this == MARSH);
    }
    
    public boolean isPort() {
	return (this == COVE || this == WHARF);
    }
}
