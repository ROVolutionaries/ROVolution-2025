import matplotlib.pyplot as plt
import json

class Cursor:
    """
    A cross hair cursor.
    """
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])
            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
            self.ax.figure.canvas.draw()


img = plt.imread('river_map.jpg')

coords = []

def onclick(event):
    if event.inaxes: 
        ix, iy = event.xdata, event.ydata
        print(f"Clicked at x={ix}, y={iy}")
        coords.append([ix, iy])

fig, ax = plt.subplots(figsize=(10, 8))
cursor = Cursor(ax)
ax.imshow(img)

# Connect events
fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
fig.canvas.mpl_connect('button_press_event', onclick)

plt.title("Click to record coordinates (close window when done)")
plt.show()

with open('output.json', 'w') as f:
    json.dump(coords, f)
