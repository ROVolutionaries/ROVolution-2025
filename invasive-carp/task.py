import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.animation import FuncAnimation
import matplotlib.patheffects as path_effects

# Load data
carp_data = pd.read_csv('data.csv', index_col=0)

# Load region coordinates
with open('river_coords.json', 'r') as f:
    region_coords = json.load(f)

# Load the river map image
river_map = Image.open('river_map.jpg')

# Create the animation
fig, ax = plt.subplots(figsize=(10, 8))

def update(frame):
    ax.clear()
    year = carp_data.index[frame]
    
    # Display the river map
    ax.imshow(river_map)
    
    # Plot each region as a line
    for region, coords in region_coords.items():
        region_number = int(region.split()[-1])
        column_name = f"Region {region_number}"
        
        # Skip if the region isn't in our data
        if column_name not in carp_data.columns:
            continue
            
        # Check if region is affected by carp in this year
        is_affected = carp_data.loc[year, column_name] == 'Y'
        
        # Extract x and y coordinates for line plotting
        coords_array = np.array(coords)
        x = coords_array[:, 0]
        y = coords_array[:, 1]
        
        # Plot the line with thicker width for affected regions
        line_width = 4 if is_affected else 1
        line_color = 'red' if is_affected else '#3baeff'
        line_alpha = 1.0 if is_affected else 1
        
        # Plot the line (note: not flipping coordinates as you indicated they're already flipped)
        ax.plot(x, y, '-', linewidth=line_width, color=line_color, alpha=line_alpha)
        
        # Add region label
        center = np.mean(coords_array, axis=0)
        """
        text = ax.text(center[0], center[1], region, 
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=12, 
                 color='white', 
                 fontweight='bold')
        text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='black')])
        """
    
    # Add year in the bottom right
    year_text = ax.text(0.95, 0.95, str(year), 
                         transform=ax.transAxes,
                         fontsize=20, 
                         fontweight='bold',
                         horizontalalignment='right',
                         verticalalignment='top',
                         color='white',
                         bbox=dict(facecolor='black', alpha=0.7, pad=10))
    
    # Remove axes
    ax.axis('off')
    
    # Set title
    ax.set_title("Regions Affected by Carp", fontsize=16)
    
    return ax.get_children()

# Create animation with 1 second delay between frames
ani = FuncAnimation(fig, update, frames=len(carp_data), interval=1000, blit=True)

# Save as GIF
ani.save('carp_spread.gif', writer='pillow', fps=1, dpi=river_map.info["dpi"][0]*2)

plt.close()

print("Animation saved as 'carp_spread.gif'")