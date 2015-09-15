import tkinter 
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip

class SourcesView():
    """Manages the view for the list of matched sources.

    The text view:
      The first line contains the column annotation.  It is non-selectable
        with a gray background.
      The remaining lines are sources, alternating colors.
      Source columns are tab-spaced and contain:
        Source ID, %match, #match, file size, repository name, filename.
      Mouse motion events change the Source line background color.
      Mouse click events toggle source filtering for that source ID.
      The background for the Source ID is red or green based on filter.

    Attributes:
      frame(Frame): the containing frame for this view.
      _source_text(Text): The Text widget to render sources in.
    """

    def __init__(self, master, identified_data, filters):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): The filters that controll the view.
        """

        # colors
        self.TITLE = "gray90"
        self.EVEN_FILTERED = "#ccffcc"
        self.ODD_FILTERED = "#aaffaa"
        self.HOVERED_FILTERED = "#006633"
        self.LEGEND_FILTERED = "#006633"
        self.EVEN_UNFILTERED = "#ffdddd"
        self.ODD_UNFILTERED = "#ffcccc"
        self.HOVERED_UNFILTERED = "#990000"
        self.LEGEND_UNFILTERED = "#990000"

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # cursor line or -1
        self._cursor_line = -1

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the title
        tkinter.Label(self.frame, text='All Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # add the color legend
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP)
        tkinter.Label(f,text="   ",background=self.LEGEND_UNFILTERED).pack(
                                                         side=tkinter.LEFT)
        tkinter.Label(f,text="Not filtered      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background=self.LEGEND_FILTERED).pack(
                                                         side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered      ").pack(side=tkinter.LEFT)

        # add the select all and clear all buttons
        select_clear_frame = tkinter.Frame(self.frame)
        select_clear_frame.pack(pady=8)

        # clear button
        self._clear_all_icon = tkinter.PhotoImage(file=icon_path("clear_all"))
        clear_all_button = tkinter.Button(select_clear_frame,
                       image=self._clear_all_icon,
                       command=self._handle_clear_all_sources)
        clear_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_all_button, "Do not filter any sources")

        # select button
        self._select_all_icon = tkinter.PhotoImage(file=icon_path("select_all"))
        select_all_button = tkinter.Button(select_clear_frame,
                       image=self._select_all_icon,
                       command=self._handle_set_all_sources)
        select_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(select_all_button, "Filter all sources")

        # scrolled frame for sources
        scrolled_text = ScrolledText(self.frame, width=60, height=60)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the text widget for the source view
        self._source_text = scrolled_text.text

        # text widget tab settng
        self._source_text.config(tabs=('1.0c', tkinter.RIGHT,
                                       '1.8c', tkinter.NUMERIC,
                                       '4.0c', tkinter.RIGHT,
                                       '6.1c', tkinter.RIGHT,
                                       '6.6c',
                                       '10.6c'))

        # text widget cursor setting
        self._source_text.config(cursor="arrow")

        # text widget mouse events
        self._source_text.bind('<Any-Motion>', self._handle_mouse_move)
        self._source_text.bind('<Button-1>', self._handle_b1_mouse_press)
        self._source_text.bind('<Enter>', self._handle_enter)
        self._source_text.bind('<Leave>', self._handle_leave)

        # set initial state
        self._fill_source_view()

        # register to receive identified data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

    def _get_sources_offsets(self):
        """Get the set of offsets for each source.  The length of a set
        indicates source fullness for that source."""
        # sources_offsets = dict<source ID, set<source offset int>>
        sources_offsets = defaultdict(set)

        # identify source offsets of every source of every matching hash
        for _, sources in self._identified_data.hashes.items():
            for source in sources:

                # set the offset for the source
                sources_offsets[source["source_id"]].add(source["file_offset"])

        return sources_offsets

    def _fill_source_view(self):

        # initialize the line and ID lookup dictionaries
        self._line_to_id = {}
        self._id_to_line = {}

        # set editable
        self._source_text.config(state=tkinter.NORMAL)

        # clear any existing text
        self._source_text.delete(1.0, tkinter.END)

        # delete any existing tags
        self._source_text.tag_delete(self._source_text.tag_names())

        # put in the title tag
        self._source_text.tag_config("title", background=self.TITLE)

        # put in the first line containing the column titles
        self._source_text.insert(tkinter.END,
                                 "\tID\t%Match\t#Match\tSize\t"
                                 "Repository Name\tFilename\n",
                                 "title")

        # get set of offsets for each source
        sources_offsets = self._get_sources_offsets()

        # local reference to filtered sources
        filtered_sources = self._filters.filtered_sources

        # put in source lines
        line = 2
        for source_id, source in self._identified_data.source_details.items():

            # set the tag for the source text
            self._set_tag(line, source_id)

            # compose the source text
            # handle missing fields, which can happen if an image was
            # imported instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                                 (int(source["filesize"] / 
                                 self._identified_data.sector_size)) * \
                                 100

                source_text = '\t%s\t%.2f%%\t%d\t%d\t%s\t%s\n' \
                                    %(source_id,
                                      percent_found,
                                      len(sources_offsets[source_id]),
                                      source["filesize"],
                                      source["repository_name"],
                                      source["filename"])

            else:
                source_text = '\t%s\t%.2f%%\t?%d\t?\t%s\t%s\n' \
                                    %(source_id,
                                      len(sources_offsets[source_id]),
                                      source["repository_name"],
                                      source["filename"])

            # add the source text
            tag_name = "line_%s" % line
            self._source_text.insert(tkinter.END, source_text, tag_name)

            # record the line and ID lookups
            self._line_to_id[line] = source_id
            self._id_to_line[source_id] = line

            # next line
            line += 1
 
        # set not editable
        self._source_text.config(state=tkinter.DISABLED)

    def _set_tag(self, line, source_id):
        # create the tag name for the line
        tag_name = "line_%s" % line

        # determine the background color
        if source_id in self._filters.filtered_sources:
            # use FILTERED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_FILTERED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_FILTERED
                else:
                    background = self.ODD_FILTERED
        else:
            # use UNFILTERED color scheme
            if line == self._cursor_line:
                foreground = "white"
                background = self.HOVERED_UNFILTERED
            else:
                foreground = "black"
                if line % 2 == 0:
                    background = self.EVEN_UNFILTERED
                else:
                    background = self.ODD_UNFILTERED

        # create or modify the tag
        self._source_text.tag_config(tag_name, background=background,
                                               foreground=foreground)

    def _set_tags(self):
        for line, source_id in self._line_to_id.items():
            self._set_tag(line, source_id)

    def _mouse_to_line(self, e):
        index = self._source_text.index("@%s,%s" % (e.x, e.y))
        line,_ = index.split('.')
        return int(line)

    def _handle_clear_all_sources(self, *args):
        # clear filtered sources and signal change
        self._filters.filtered_sources.clear()
        self._filters.fire_change()

    def _handle_set_all_sources(self, *args):
        # set filtered sources and signal change
        self._filters.filtered_sources.clear()
        for source_id in self._identified_data.source_details:
            self._filters.filtered_sources.add(source_id)
        self._filters.fire_change()

    def _handle_identified_data_change(self, *args):
        self._fill_source_view()

    def _handle_filter_change(self, *args):
        self._set_tags()

    def _handle_mouse_move(self, e):
        line = self._mouse_to_line(e)

        # no action
        if line == self._cursor_line:
            return

        # restore old cursor line
        old_cursor_line = self._cursor_line
        if old_cursor_line != -1:
            self._cursor_line = -1
            self._set_tag(old_cursor_line, self._line_to_id[old_cursor_line])

        # set new cursor line if the line is in bounds
        if line in self._line_to_id:
            self._cursor_line = line
            self._set_tag(line, self._line_to_id[line])

    def _handle_b1_mouse_press(self, e):
        line = self._mouse_to_line(e)

        # line must be in bounds
        if line not in self._line_to_id:
            return

        # toggle filter state for source
        source_id = self._line_to_id[line]
        if source_id in self._filters.filtered_sources:
            self._filters.filtered_sources.remove(source_id)
        else:
            self._filters.filtered_sources.add(source_id)

        # fire change
        self._filters.fire_change()

    def _handle_enter(self, e):
        self._handle_mouse_move(e)

    def _handle_leave(self, e):
        # restore old cursor line
        if self._cursor_line != -1:
            old_cursor_line = self._cursor_line
            self._cursor_line = -1
            self._set_tag(old_cursor_line, self._line_to_id[old_cursor_line])

