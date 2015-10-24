from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow
import colors
from filter_changer import FilterChanger
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class FiltersView():
    """Provides filter controls for ignored and highlighted hashes and sources.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, range_selection):
        """Args:
          master(a UI container): Parent.
          filters(Filters): Filters for hashes and sources.
          range_selection(RangeSelection): The selected range.
         """

        # the filter changer helper
        self._fc = FilterChanger(identified_data, filters, range_selection)

        # state to prevent infinite filter change loop
        self._is_handle_filter_change = False

        # UI state
        self._ignore_flagged_blocks_trace_var = tkinter.IntVar()

        # local references
        self._filters = filters
        self._range_selection = range_selection

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # highlight and ignore frame
        highlight_and_ignore_frame = tkinter.Frame(self.frame,
                                                        bg=colors.BACKGROUND)
        highlight_and_ignore_frame.pack(side=tkinter.TOP, anchor="w")

        # Highlight frame
        highlight_frame = tkinter.LabelFrame(highlight_and_ignore_frame,
                      text="Highlight", bg=colors.BACKGROUND, padx=4, pady=4)
        highlight_frame.pack(side=tkinter.LEFT, anchor="n", padx=(0,4))

        # highlight buttons

        # highlight hashes in range
        self._highlight_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("highlight_hashes_in_range"))
        self._highlight_hashes_in_range_button = tkinter.Button(highlight_frame,
                           image=self._highlight_hashes_in_range_icon,
                           text="H",
                           compound="left", padx=4, pady=0,
                           command=self._fc.highlight_hashes_in_range,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._highlight_hashes_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._highlight_hashes_in_range_button,
                                      "Highlight hashes in selected range")

        # highlight sources with hashes in range
        self._highlight_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("highlight_sources_with_hashes_in_range"))
        self._highlight_sources_with_hashes_in_range_button = tkinter.Button(
                   highlight_frame,
                   image=self._highlight_sources_with_hashes_in_range_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._fc.highlight_sources_with_hashes_in_range,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._highlight_sources_with_hashes_in_range_button.pack(
                                               side=tkinter.LEFT)
        Tooltip(self._highlight_sources_with_hashes_in_range_button,
                          "Highlight sources with hashes in selected range")

        # clear highlighted hashes
        self._clear_highlighted_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_hashes"))
        self._clear_highlighted_hashes_button = tkinter.Button(highlight_frame,
                   image=self._clear_highlighted_hashes_icon,
                   text="H",
                   compound="left", padx=4, pady=0,
                   command=self._fc.clear_highlighted_hashes,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_highlighted_hashes_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_highlighted_hashes_button,
                                           "Clear all highlighted hashes")

        # clear highlighted sources
        self._clear_highlighted_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_sources"))
        self._clear_highlighted_sources_button = tkinter.Button(highlight_frame,
                   image=self._clear_highlighted_sources_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._fc.clear_highlighted_sources,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_highlighted_sources_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_highlighted_sources_button,
                                           "Clear all highlighted sources")

        # Ignore frame
        ignore_frame = tkinter.LabelFrame(highlight_and_ignore_frame,
                         text="Ignore", bg=colors.BACKGROUND, padx=4, pady=4)
        ignore_frame.pack(side=tkinter.LEFT, anchor="n")

        # ignore max same hashes text entry
        ignore_max_hashes_frame = tkinter.Frame(ignore_frame,
                                                bg=colors.BACKGROUND)
        ignore_max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(ignore_max_hashes_frame,
                      text="Max Duplicate Hashes:", padx=0, pady=0,
                      bg=colors.BACKGROUND).pack( side=tkinter.LEFT, anchor="w")
        self._ignore_max_hashes_entry = tkinter.Entry(ignore_max_hashes_frame,
                                                               width=6)
        self._ignore_max_hashes_entry.insert(0, "None")
        self._ignore_max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")

        # bind actions for ignore max hashes text entry
        self._ignore_max_hashes_entry.bind('<Return>',
                           self._handle_ignore_max_hashes_selection, add='+')
        self._ignore_max_hashes_entry.bind('<FocusOut>',
                           self._handle_ignore_max_hashes_selection, add='+')

        # ignore flagged blocks checkbutton
        self._ignore_flagged_blocks_checkbutton = tkinter.Checkbutton(
                        ignore_frame, text="Auto-filter",
                        variable=self._ignore_flagged_blocks_trace_var,
                        bd=0,
                        bg=colors.BACKGROUND,
                        activebackground=colors.ACTIVEBACKGROUND,
                        pady=4, highlightthickness=0)
        self._ignore_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                                 anchor="w")
        Tooltip(self._ignore_flagged_blocks_checkbutton,
                                         "Ignore flagged blocks")

        # bind actions for ignore_flagged_blocks checkbutton
        self._ignore_flagged_blocks_trace_var.set(filters.ignore_flagged_blocks)
        self._ignore_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_ignore_flagged_blocks_selection)

        # ignore buttons

        # ignore hashes in range
        self._ignore_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_hashes_in_range"))
        self._ignore_hashes_in_range_button = tkinter.Button(ignore_frame,
                           image=self._ignore_hashes_in_range_icon,
                           text="H",
                           compound="left", padx=4, pady=0,
                           command=self._fc.ignore_hashes_in_range,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._ignore_hashes_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._ignore_hashes_in_range_button,
                                         "Ignore hashes in selected range")

        # ignore sources with hashes in range
        self._ignore_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("ignore_sources_with_hashes_in_range"))
        self._ignore_sources_with_hashes_in_range_button = tkinter.Button(
                   ignore_frame,
                   image=self._ignore_sources_with_hashes_in_range_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._fc.ignore_sources_with_hashes_in_range,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._ignore_sources_with_hashes_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._ignore_sources_with_hashes_in_range_button,
                             "Ignore sources with hashes in selected range")

        # clear ignored hashes
        self._clear_ignored_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_hashes"))
        self._clear_ignored_hashes_button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_hashes_icon,
                   text="H",
                   compound="left", padx=4, pady=0,
                   command=self._fc.clear_ignored_hashes,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_ignored_hashes_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_ignored_hashes_button, "Clear all ignored hashes")

        # clear ignored sources
        self._clear_ignored_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_sources"))
        self._clear_ignored_sources_button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_sources_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._fc.clear_ignored_sources,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_ignored_sources_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_ignored_sources_button, "Clear all ignored sources")

        # register to receive highlight change events
        filters.set_callback(self._handle_filter_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set initial state
        self._handle_filter_change()
        self._handle_range_selection_change()

    def _handle_filter_change(self, *args):
        # set state for ignore max hashes entry and ignore
        # flagged blocks trace var without causing a circular
        # handle_filter_change loop
        self._is_handle_filter_change = True
        self._set_ignore_max_hashes_entry(self._filters.ignore_max_hashes)
        self._ignore_flagged_blocks_trace_var.set(
                                   self._filters.ignore_flagged_blocks)
        self._is_handle_filter_change = False

        # ignored hashes
        if len(self._filters.ignored_hashes):
            self._clear_ignored_hashes_button.config(state=tkinter.NORMAL)
        else:
            self._clear_ignored_hashes_button.config(state=tkinter.DISABLED)

        # ignored sources
        if len(self._filters.ignored_sources):
            self._clear_ignored_sources_button.config(state=tkinter.NORMAL)
        else:
            self._clear_ignored_sources_button.config(state=tkinter.DISABLED)

        # highlighted hashes
        if len(self._filters.highlighted_hashes):
            self._clear_highlighted_hashes_button.config(state=tkinter.NORMAL)
        else:
            self._clear_highlighted_hashes_button.config(state=tkinter.DISABLED)

        # highlighted sources
        if len(self._filters.highlighted_sources):
            self._clear_highlighted_sources_button.config(state=tkinter.NORMAL)
        else:
            self._clear_highlighted_sources_button.config(
                                                       state=tkinter.DISABLED)

    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            state = tkinter.NORMAL
        else:
            state = tkinter.DISABLED
        self._ignore_hashes_in_range_button.config(state=state)
        self._ignore_sources_with_hashes_in_range_button.config(state=state)
        self._highlight_hashes_in_range_button.config(state=state)
        self._highlight_sources_with_hashes_in_range_button.config(state=state)

    def _set_ignore_max_hashes_entry(self, ignore_max_hashes):
        self._ignore_max_hashes_entry.delete(0, tkinter.END)
        if ignore_max_hashes == 0:
            self._ignore_max_hashes_entry.insert(0, "None")
        else:
            self._ignore_max_hashes_entry.insert(0,
                                    "%s" % self._filters.ignore_max_hashes)

    def _handle_ignore_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            ignore_max_hashes = int(self._ignore_max_hashes_entry.get())
        except ValueError:
            ignore_max_hashes = 0

        # set entry to make sure it looks nice
        self._set_ignore_max_hashes_entry(ignore_max_hashes)

        # fire if change is from the user
        if not self._is_handle_filter_change:

            # only set if ignore_max_hashes changes
            if ignore_max_hashes != self._filters.ignore_max_hashes:
                self._filters.ignore_max_hashes = ignore_max_hashes
                self._filters.fire_change()

                # drop focus so it visually looks accepted
                # by giving focus to something that doesn't need or show it
                self.frame.focus()

    def _handle_ignore_flagged_blocks_selection(self, *args):
        self._filters.ignore_flagged_blocks = \
                               self._ignore_flagged_blocks_trace_var.get()

        # fire if change is from the user
        if not self._is_handle_filter_change:
            self._filters.fire_change()

