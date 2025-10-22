import * as React from 'react';
import { Label } from './ui/label';
import { Input } from './ui/input';
// --- CHANGE THIS LINE ---
import { Button } from "./ui/button"; // Changed from "react-day-picker"

export function ThemeCustomizer() {
    // 1. Store the user's chosen color in state
    const [fontColor, setFontColor] = React.useState<string | undefined>(undefined);

    // 2. When the color changes, apply it to the root <html> element
    React.useEffect(() => {
        if (fontColor) {
            // This sets the CSS variable: --custom-foreground: '#...'
            document.documentElement.style.setProperty('--custom-foreground', fontColor);
        } else {
            // If the color is cleared, remove the variable to use the default
            document.documentElement.style.removeProperty('--custom-foreground');
        }
    }, [fontColor]); // This effect runs every time 'fontColor' changes

    return (
        <div className="p-4 border rounded-lg dark w-full max-w-sm"> {/* Using .dark for the component itself */}
            <h3 className="text-lg font-medium">Customize Theme</h3>
            <p className="text-sm text-muted-foreground mb-4">
                Select a custom font color for the page.
            </p>
            <div className="flex items-center gap-4">
                <Label htmlFor="font-color" className="whitespace-nowrap">
                    Font Color
                </Label>
                <Input
                    id="font-color"
                    type="color" // This gives you a native browser color picker
                    value={fontColor || '#ffffff'} // Default the picker to white
                    onChange={(e) => setFontColor(e.target.value)}
                    className="w-16 h-10 p-1" // Basic styling for the color input
                />
                <Button variant="ghost" onClick={() => setFontColor(undefined)}>
                    Reset
                </Button>
            </div>
        </div>
    );
}

