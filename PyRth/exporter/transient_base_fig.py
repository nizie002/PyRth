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

        total_calls = 10
        colormap = "viridis"

        self.module = module  # Store the module
        self.total_calls = total_calls
        self.colormap = colormap
        self.fig, self.ax = self._create_fig_ax()  # Create figure & axis here
        self.num_calls = 0
        self.colorlist = matplotlib.colormaps.get_cmap(colormap)(
            np.linspace(0, 1, total_calls)
        )
        self.label = module.label
        self.output_dir = module.output_dir

        # Automatically call the method that builds the figure.
        self.make_figure()
        self.add_legend()

    def _create_fig_ax(self):
        fig = Figure(figsize=(10, 6))
        FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        return fig, ax

    def add_legend(self):
        # Get legend entries from the primary axis
        handles, labels = self.ax.get_legend_handles_labels()
        # If a secondary y-axis exists, combine its legend entries
        if hasattr(self, "ax2"):
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            handles.extend(handles2)
            labels.extend(labels2)
        self.ax.legend(handles, labels)

    def make_figure(self):
        """Subclasses should override this to create their specific figure."""
        pass

    def close(self):
        self.fig.clf()  # Clear the figure
        plt.close(self.fig)  # Ensure the figure is closed

    def next_color(self):
        self.last_call = self.num_calls
        self.num_calls += 1
        self.num_calls = self.num_calls % self.total_calls
        return self.colorlist[self.last_call]

    def same_color(self):
        if self.num_calls == 0:
            raise IndexError("No colors available; num_calls is zero.")
        return self.colorlist[self.last_call]
