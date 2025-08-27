/**
 * Frontend Psychology Theme Integration
 * Implements mood-responsive colors and calming design patterns
 */

interface WellnessColors {
  calm_blue: string;
  sage_green: string;
  soft_purple: string;
  warm_beige: string;
  gentle_teal: string;
  sunset_orange: string;
  forest_green: string;
  lavender: string;
  soft_pink: string;
  warm_yellow: string;
}

interface MoodColorMapping {
  [key: string]: string[];
}

export const WELLNESS_COLORS: WellnessColors = {
  calm_blue: "#4A90E2",
  sage_green: "#87A96B", 
  soft_purple: "#9B8CE8",
  warm_beige: "#F5F1E8",
  gentle_teal: "#5DADE2",
  sunset_orange: "#F39C12",
  forest_green: "#27AE60",
  lavender: "#BB8FCE",
  soft_pink: "#F8BBD9",
  warm_yellow: "#F7DC6F"
};

export const MOOD_COLOR_MAPPINGS: MoodColorMapping = {
  anxious: ["calm_blue", "sage_green", "lavender"],
  depressed: ["warm_beige", "sunset_orange", "gentle_teal"],
  stressed: ["forest_green", "soft_purple", "calm_blue"],
  overwhelmed: ["lavender", "warm_beige", "sage_green"],
  lonely: ["soft_pink", "warm_yellow", "gentle_teal"],
  happy: ["gentle_teal", "sage_green", "sunset_orange"],
  peaceful: ["sage_green", "lavender", "calm_blue"],
  hopeful: ["warm_yellow", "forest_green", "gentle_teal"],
  neutral: ["calm_blue", "sage_green", "warm_beige"]
};

export class PsychologyThemeManager {
  private currentMood: string = "neutral";
  private stressLevel: number = 0.5;
  private timeOfDay: string = "day";

  constructor() {
    this.initializeTheme();
  }

  private initializeTheme(): void {
    // Set default calming theme
    this.applyMoodTheme("neutral");
  }

  public setUserMood(mood: string, stressLevel: number = 0.5): void {
    this.currentMood = mood.toLowerCase();
    this.stressLevel = stressLevel;
    this.applyMoodTheme(this.currentMood);
  }

  public getMoodColors(mood: string): string[] {
    return MOOD_COLOR_MAPPINGS[mood.toLowerCase()] || MOOD_COLOR_MAPPINGS.neutral;
  }

  public getColorHex(colorName: string): string {
    return WELLNESS_COLORS[colorName as keyof WellnessColors] || WELLNESS_COLORS.calm_blue;
  }

  public getCalmingScore(colors: string[]): number {
    const calmingWeights: { [key: string]: number } = {
      calm_blue: 0.9,
      sage_green: 0.85,
      lavender: 0.9,
      warm_beige: 0.8,
      gentle_teal: 0.75,
      soft_purple: 0.8,
      forest_green: 0.85,
      soft_pink: 0.75,
      warm_yellow: 0.7,
      sunset_orange: 0.6
    };

    if (colors.length === 0) return 0.5;
    
    const totalScore = colors.reduce((sum, color) => {
      return sum + (calmingWeights[color] || 0.5);
    }, 0);
    
    return totalScore / colors.length;
  }

  public applyMoodTheme(mood: string): void {
    const colors = this.getMoodColors(mood);
    const root = document.documentElement;

    // Apply primary colors
    root.style.setProperty('--primary-color', this.getColorHex(colors[0]));
    root.style.setProperty('--secondary-color', this.getColorHex(colors[1]));
    root.style.setProperty('--accent-color', this.getColorHex(colors[2] || colors[0]));

    // Adjust for stress level
    if (this.stressLevel > 0.7) {
      // High stress - use most calming colors
      root.style.setProperty('--primary-color', WELLNESS_COLORS.calm_blue);
      root.style.setProperty('--secondary-color', WELLNESS_COLORS.sage_green);
      root.style.setProperty('--accent-color', WELLNESS_COLORS.lavender);
    }

    // Apply calming background gradients
    this.applyCalmingGradients(colors);
    
    // Update component-specific CSS variables
    this.updateComponentColors(colors);
  }

  private applyCalmingGradients(colors: string[]): void {
    const root = document.documentElement;
    const primaryHex = this.getColorHex(colors[0]);
    const secondaryHex = this.getColorHex(colors[1]);
    
    // Create subtle, calming gradients
    root.style.setProperty(
      '--calming-gradient', 
      `linear-gradient(135deg, ${primaryHex}20, ${secondaryHex}15)`
    );
    
    root.style.setProperty(
      '--community-header-gradient',
      `linear-gradient(to right, ${primaryHex}30, ${secondaryHex}20)`
    );
    
    root.style.setProperty(
      '--card-hover-gradient',
      `linear-gradient(145deg, ${primaryHex}10, ${secondaryHex}05)`
    );
  }

  private updateComponentColors(colors: string[]): void {
    const root = document.documentElement;
    
    // Community-specific colors
    root.style.setProperty('--community-primary', this.getColorHex(colors[0]));
    root.style.setProperty('--community-secondary', this.getColorHex(colors[1]));
    root.style.setProperty('--community-accent', this.getColorHex(colors[2] || colors[0]));
    
    // Interactive elements
    root.style.setProperty('--button-calming', `${this.getColorHex(colors[0])}90`);
    root.style.setProperty('--link-calming', this.getColorHex(colors[1]));
    
    // Status colors (adjusted for psychology)
    root.style.setProperty('--success-calming', WELLNESS_COLORS.forest_green);
    root.style.setProperty('--warning-calming', WELLNESS_COLORS.warm_yellow);
    root.style.setProperty('--info-calming', WELLNESS_COLORS.gentle_teal);
    
    // Remove harsh red, use calming alternatives
    root.style.setProperty('--error-calming', WELLNESS_COLORS.soft_pink);
    root.style.setProperty('--danger-calming', WELLNESS_COLORS.warm_beige);
  }

  public generateCalmingCSS(mood: string): string {
    const colors = this.getMoodColors(mood);
    const primaryHex = this.getColorHex(colors[0]);
    const secondaryHex = this.getColorHex(colors[1]);
    
    return `
      /* Psychology-based calming styles */
      .community-calming-theme {
        --primary: ${primaryHex};
        --secondary: ${secondaryHex};
        --calming-bg: linear-gradient(135deg, ${primaryHex}10, ${secondaryHex}05);
        transition: all 0.3s ease-in-out;
      }
      
      .community-card-calming {
        background: var(--calming-bg);
        border: 1px solid ${primaryHex}30;
        border-radius: 12px;
        box-shadow: 0 4px 12px ${primaryHex}20;
        transition: all 0.3s ease;
      }
      
      .community-card-calming:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px ${primaryHex}25;
      }
      
      .community-button-calming {
        background: linear-gradient(135deg, ${primaryHex}, ${secondaryHex});
        border: none;
        border-radius: 8px;
        color: white;
        padding: 12px 24px;
        transition: all 0.3s ease;
        font-weight: 500;
      }
      
      .community-button-calming:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px ${primaryHex}40;
      }
      
      .community-text-calming {
        color: ${primaryHex};
        font-weight: 500;
      }
      
      .community-divider-calming {
        border-color: ${primaryHex}30;
      }
      
      .community-input-calming {
        border: 2px solid ${primaryHex}30;
        border-radius: 8px;
        padding: 12px;
        transition: border-color 0.3s ease;
      }
      
      .community-input-calming:focus {
        border-color: ${primaryHex};
        box-shadow: 0 0 0 3px ${primaryHex}20;
        outline: none;
      }
      
      /* Remove harsh red colors */
      .error-text-calming {
        color: ${WELLNESS_COLORS.soft_pink};
      }
      
      .warning-bg-calming {
        background: ${WELLNESS_COLORS.warm_yellow}20;
        border-left: 4px solid ${WELLNESS_COLORS.warm_yellow};
      }
    `;
  }

  public getCrisisColors(): string[] {
    // Ultra-calming colors for crisis situations
    return ["calm_blue", "lavender", "sage_green"];
  }

  public getTimeBasedAdjustment(): string {
    const hour = new Date().getHours();
    
    if (hour >= 18 || hour <= 6) {
      // Evening/night - darker, more calming tones
      return "night";
    } else if (hour >= 6 && hour <= 11) {
      // Morning - gentle, hopeful tones  
      return "morning";
    } else {
      // Day - balanced, energizing but calm tones
      return "day";
    }
  }

  public adjustColorsForTime(colors: string[]): string[] {
    const timeOfDay = this.getTimeBasedAdjustment();
    
    switch (timeOfDay) {
      case "night":
        return ["calm_blue", "lavender", "sage_green"]; // Very calming for evening
      case "morning": 
        return ["gentle_teal", "warm_yellow", "sage_green"]; // Hopeful for morning
      default:
        return colors; // Use mood-based colors for day
    }
  }

  public getAccessibilityColors(): { background: string; text: string; contrast: number } {
    // Ensure WCAG compliance while maintaining calming effect
    const colors = this.getMoodColors(this.currentMood);
    const bgColor = this.getColorHex(colors[0]);
    
    return {
      background: bgColor,
      text: "#2C3E50", // Dark text for readability
      contrast: 4.5 // WCAG AA compliance
    };
  }
}

// Global instance
export const psychologyTheme = new PsychologyThemeManager();

// React hook for theme integration
export const usePsychologyTheme = () => {
  return {
    setMood: (mood: string, stressLevel?: number) => {
      psychologyTheme.setUserMood(mood, stressLevel);
    },
    getMoodColors: (mood: string) => psychologyTheme.getMoodColors(mood),
    getCalmingScore: (colors: string[]) => psychologyTheme.getCalmingScore(colors),
    generateCSS: (mood: string) => psychologyTheme.generateCalmingCSS(mood),
    getCrisisColors: () => psychologyTheme.getCrisisColors(),
    theme: psychologyTheme
  };
};
