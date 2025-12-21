"""Shared plotting helpers used by the exporter layer."""

import logging

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

plt.rcParams.update({"font.size": 13})
plt.rcParams["legend.fontsize"] = "small"

logger = logging.getLogger("PyRthLogger")


class StructureFigure:
    """Lightweight wrapper around Matplotlib figure/axes management."""

    def __init__(self, module):
        """Prepare shared figure state and color bookkeeping for a module."""
        colormap_name = "tab10"
        cmap = matplotlib.colormaps.get_cmap(colormap_name)
        total_colors = len(cmap.colors)

        self.module = module
        self.total_colors = total_colors
        self.colormap = cmap
        self.fig, self.ax = self._create_fig_ax()
        self.num_calls = 0
        self.colorlist = cmap.colors
        self.output_dir = module.output_dir
        self._axis_initialized = False
        self.ax2 = None
        self.last_call_index = None

    def _create_fig_ax(self):
        fig = Figure(figsize=(10, 6))
        FigureCanvas(fig)
        ax = fig.add_subplot(1, 1, 1)
        return fig, ax

    def add_legend(self):
        """Merge legend entries from both axes, truncating labels when needed."""
        handles, labels = self.ax.get_legend_handles_labels()
        if hasattr(self, "ax2") and self.ax2:
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            unique_labels = set(labels)
            for h, l in zip(handles2, labels2):
                if l not in unique_labels:
                    handles.append(h)
                    labels.append(l)
                    unique_labels.add(l)

        if handles:
            truncated_labels = []
            for label in labels:
                if len(label) > 25:
                    truncated_label = label[:15] + "..." + label[-5:]
                    truncated_labels.append(truncated_label)
                else:
                    truncated_labels.append(label)

            num_items = len(handles)
            ncol = 2 if num_items > 10 else 1

            self.ax.legend(
                handles, truncated_labels, loc="best", fontsize="x-small", ncol=ncol
            )
            self.fig.tight_layout()

    def plot_module_data(self, module):
        """Dispatch to subclass-specific plotting logic for ``module``.
        
        # Example implementation in subclass:
        # if not self._axis_initialized:
        #     self.ax.set_title("My Plot Title")
        #     self.ax.set_xlabel("X-axis")
        #     self.ax.set_ylabel("Y-axis")
        #     self._axis_initialized = True
        # color = self.next_color()
        # self.ax.plot(module.x_data, module.y_data, color=color, label=module.label)
        """
        raise NotImplementedError("Subclasses must implement plot_module_data")

    def close(self):
        """Release Matplotlib resources associated with this figure."""
        try:
            plt.close(self.fig)
        except (RuntimeError, ValueError) as e:
            plt.close("all")
            logger.warning(
                f"Issue closing figure: {e}, closed all figures as fallback"
            )

    def next_color(self):
        """Return the next color in the discrete colormap."""
        color_index = self.num_calls % self.total_colors
        self.last_call_index = color_index
        self.num_calls += 1
        return self.colorlist[color_index]

    def same_color(self):
        """Reuse the most recently issued color."""
        if self.last_call_index is None:
            return self.next_color()
        return self.colorlist[self.last_call_index]
