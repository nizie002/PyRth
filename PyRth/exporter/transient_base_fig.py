import numpy as np
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

plt.rcParams.update({"font.size": 13})
plt.rcParams["legend.fontsize"] = "small"


class StructureFigure:
    def __init__(self, module):
        """
        Initializes the figure structure. Stores the initial module for context
        like output directory, creates figure and axes, and sets up color mapping.
        """
        # Use a qualitative colormap for better distinction between plot lines
        colormap_name = "tab10"  # Or "tab20" if you expect > 10 plots often
        cmap = matplotlib.colormaps.get_cmap(colormap_name)
        total_colors = len(cmap.colors)  # Get the number of colors in the map

        self.module = module  # Store the initial module for context (e.g., output_dir)
        self.total_colors = total_colors
        self.colormap = cmap
        self.fig, self.ax = self._create_fig_ax()  # Create figure & axis here
        self.num_calls = 0
        self.colorlist = cmap.colors  # Use the discrete colors from the map
        self.output_dir = module.output_dir
        # Axes titles and labels should be set ideally once, perhaps in the first plot_module_data call
        self._axis_initialized = False
        # Secondary axis handling
        self.ax2 = None
        self.last_call_index = None  # Initialize index for last color used

    def _create_fig_ax(self):
        fig = Figure(figsize=(10, 6))
        FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        return fig, ax

    def add_legend(self):
        """Adds a legend to the plot, combining entries from primary and secondary axes if present,
        truncating long labels, and using multiple columns if needed."""
        handles, labels = self.ax.get_legend_handles_labels()
        if hasattr(self, "ax2") and self.ax2:  # Check if ax2 exists and is not None
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            unique_labels = set(labels)
            for h, l in zip(handles2, labels2):
                if l not in unique_labels:
                    handles.append(h)
                    labels.append(l)
                    unique_labels.add(l)

        if handles:  # Only add legend if there are items to add
            # Truncate labels longer than 25 characters (15 start + ... + 5 end)
            truncated_labels = []
            for label in labels:
                if len(label) > 25:
                    truncated_label = label[:15] + "..." + label[-5:]
                    truncated_labels.append(truncated_label)
                else:
                    truncated_labels.append(label)

            # Determine number of columns
            num_items = len(handles)
            ncol = 2 if num_items > 10 else 1

            # Place legend inside the plot area
            self.ax.legend(
                handles, truncated_labels, loc="best", fontsize="x-small", ncol=ncol
            )
            # A general tight_layout might still be useful
            self.fig.tight_layout()

    def plot_module_data(self, module):
        """
        Plots data for the given module onto the figure's axes.
        Subclasses must override this method.
        """
        # Example implementation in subclass:
        # if not self._axis_initialized:
        #     self.ax.set_title("My Plot Title")
        #     self.ax.set_xlabel("X-axis")
        #     self.ax.set_ylabel("Y-axis")
        #     self._axis_initialized = True
        # color = self.next_color()
        # self.ax.plot(module.x_data, module.y_data, color=color, label=module.label)
        raise NotImplementedError("Subclasses must implement plot_module_data")

    def close(self):
        self.fig.clf()  # Clear the figure
        plt.close(self.fig)  # Ensure the figure is closed

    def next_color(self):
        """Cycles through the color list."""
        color_index = (
            self.num_calls % self.total_colors
        )  # Cycle through available colors
        self.last_call_index = color_index
        self.num_calls += 1
        return self.colorlist[color_index]

    def same_color(self):
        """Returns the last used color."""
        if self.last_call_index is None:  # Check if a color has been used yet
            # Return the first color if none used yet
            return self.next_color()
        return self.colorlist[self.last_call_index]
