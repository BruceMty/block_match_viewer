from fit_range_selection import FitRangeSelection
from image_hex_window import ImageHexWindow
import colors
from icon_path import icon_path
from tooltip import Tooltip
from histogram_bar import HistogramBar
from annotation_window import AnnotationWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramView():
    """Renders the Image Match Histogram view.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, annotation_filter,
                 range_selection, preferences):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
          preferences(Preferences): Includes the offset format preference.
        """

        # data variables
        self._range_selection = range_selection

        # the image hex window that the show hex view button can show
        self._image_hex_window = ImageHexWindow(master, identified_data,
                                                  filters, range_selection)

        # the fit byte range selection signal manager
        fit_range_selection = FitRangeSelection()

        # the annotation window
        self._annotation_window = AnnotationWindow(master, identified_data,
                                                          annotation_filter)

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # add controls frame
        controls_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        controls_frame.pack(side=tkinter.TOP, anchor="w")
#        controls_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        # button to zoom to fit image
        self._fit_image_icon = tkinter.PhotoImage(file=icon_path("fit_image"))
        self._fit_image_button = tkinter.Button(controls_frame,
                           image=self._fit_image_icon,
                           command=self._handle_fit_image,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._fit_image_button.pack(side=tkinter.LEFT)
        Tooltip(self._fit_image_button, "Zoom to fit image")

        # button to zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(controls_frame,
                              image=self._fit_range_icon,
                              command=fit_range_selection.fire_change,
                              bg=colors.BACKGROUND,
                              activebackground=colors.ACTIVEBACKGROUND,
                              highlightthickness=0)
        self._fit_range_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(self._fit_range_button, "Zoom to range")

        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        show_hex_view_button = tkinter.Button(controls_frame,
                              image=self._show_hex_view_icon,
                              command=self._image_hex_window.show,
                              bg=colors.BACKGROUND,
                              activebackground=colors.ACTIVEBACKGROUND,
                              highlightthickness=0)
        show_hex_view_button.pack(side=tkinter.LEFT)
        Tooltip(show_hex_view_button, "Show hex view of selection")

        # button to view annotations
        self._view_annotations_icon = tkinter.PhotoImage(file=icon_path(
                                                        "view_annotations"))
        view_annotations_button = tkinter.Button(controls_frame,
                           image=self._view_annotations_icon,
                           command=self._handle_view_annotations,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)

        view_annotations_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(view_annotations_button, "Manage annotations shown")

        # range selection
        range_selection_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        range_selection_frame.pack(side=tkinter.TOP, anchor="w")

        # add the histogram bar
        self._histogram_bar = HistogramBar(self.frame, identified_data,
                                    filters,
                                    range_selection, fit_range_selection,
                                    preferences, annotation_filter)
        self._histogram_bar.frame.pack(side=tkinter.TOP)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set to basic initial state
        self._handle_range_selection_change()

    def _handle_fit_image(self):
        self._histogram_bar.fit_image()

    def _handle_view_annotations(self):
        self._annotation_window.show()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # enable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.NORMAL)

        else:
            # disable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.DISABLED)

