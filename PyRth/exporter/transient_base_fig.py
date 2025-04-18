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
        total_calls = 10  # Adjust if expecting more than 10 plots per figure
        colormap = "viridis"

        self.module = module  # Store the initial module for context (e.g., output_dir)
        self.total_calls = total_calls
        self.colormap = colormap
        self.fig, self.ax = self._create_fig_ax()  # Create figure & axis here
        self.num_calls = 0
        self.colorlist = matplotlib.colormaps.get_cmap(colormap)(
            np.linspace(0, 1, total_calls)
        )
        self.output_dir = module.output_dir
        # Axes titles and labels should be set ideally once, perhaps in the first plot_module_data call
        self._axis_initialized = False
        # Secondary axis handling
        self.ax2 = None

    def _create_fig_ax(self):
        fig = Figure(figsize=(10, 6))
        FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        return fig, ax

    def add_legend(self):
        """Adds a legend to the plot, combining entries from primary and secondary axes if present."""
        handles, labels = self.ax.get_legend_handles_labels()
        if hasattr(self, "ax2") and self.ax2:  # Check if ax2 exists and is not None
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            # Avoid duplicate labels if plotting same thing on both axes
            unique_labels = set(labels)
            for h, l in zip(handles2, labels2):
                if l not in unique_labels:
                    handles.append(h)
                    labels.append(l)
                    unique_labels.add(l)

        if handles:  # Only add legend if there are items to add
            # Place legend outside the plot area to avoid overlap
            self.ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1, 0.5))
            # Adjust layout to prevent legend cutoff
            self.fig.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust right boundary

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
        self.last_call = self.num_calls
        self.num_calls += 1
        # Ensure cycling wraps around correctly, handle potential > total_calls plots if needed
        self.num_calls = self.num_calls % self.total_calls
        return self.colorlist[self.last_call]

    def same_color(self):
        """Returns the last used color."""
        if (
            self.num_calls == 0 and self.last_call is None
        ):  # Check if a color has been used yet
            # Optionally, return the first color or raise error
            return self.next_color()  # Return the first color if none used yet
        return self.colorlist[self.last_call]
