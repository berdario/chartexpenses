<style>
body {
  margin-left: auto;
  margin-right: auto;
  max-width: 8in;
  font-family: verdana, sans-serif;
}
code {
  font-family: andale mono, courier new, courier, monospace;
}
p {
  line-height: 150%;
}
iframe {
  width: 95%;
  height: 400px;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 2em;
}
.gallery iframe {
  width: 40%;
  height: 200px;
  margin: 1em;
  border: 0;
}
.gallery iframe.spark {
  display: block;
  width: 100px;
  height: 40px;
  margin-top: 0;
  margin-bottom: 0;
  margin-left: auto;
  margin-right: auto;
}
u {
  color: red;
}
</style>

# Afterquery: the json post-processor and graphing tool

## What does it do?

Afterquery is a pure-client-side javascript tool that downloads
[jsonp](http://en.wikipedia.org/wiki/JSONP)-formatted data from a
given URL, applies a configurable series of transformations, and then
renders the result as either a data table or a Google Visualizations
(gviz) chart.

Although the javascript file happens to be hosted on a server,
your data never gets uploaded; your browser handles all the
processing steps internally.  Also, the permissions to
download the jsonp data depends on the cookies in your
browser, so you can safely retrieve protected content
without granting authorization to an external server.

You can then embed it in an iframe to produce easy
dashboards like this:

<iframe
src="/?url=example1.json&group=ver,serial;&filter=ver>&order=ver&group=ver;serial&order=-serial&limit=4&chart=pie">
</iframe>

(That's actually a live graph generated by afterquery just
now.)

I wrote afterquery because I found that there are lots of
cool tools for extracting data from super huge databases
(so-called "big data") but those tools can take between a
few seconds and a few minutes to run.  Once you have a
smallish dataset produced by running your "big data" query
tools, it would be nice to be able to shrink, summarize,
and rotate the "not big data" as efficiently as possible. 
That's this.


## How to use

First, you need to find a service that produces data in
"rows and columns" jsonp format.  That is, the structure of
the object is [row1,row2,...,rown] where each row is
[col1,col2,col3,...,coln].

Then you construct a afterquery URL with the jsonp URL you
want to retrieve from, followed by the set of transforms
you want to apply.  You can just type it into your web
browser's URL bar while you experiment.  Then, once you
have the query the way you want it, paste it into a web
page inside an &lt;iframe&gt; tag (like the graph above) or
just [make a hyperlink to a full-screen
chart](/?url=example1.json&group=ver,serial;&filter=ver>&order=ver&group=ver;serial&order=-serial&limit=4&chart=pie).

The basic structure is:

        https://afterquery.appspot.com?url=http://wherever/my/page/is&<transform1>&<transform2>&<transform3>...

(The default with no transforms is to just show the data in
a handy table view without any changes.)

Available transforms:

 -  <b>&limit=<u>n</u></b>  
    Discard all data after <u>n</u> rows.

 -  <b>&filter=<u>key</u>>=<u>value1</u>,<u>value2</u>,...</b>  
    Show only rows where the column named <u>key</u> has a
    value >= <u>value1</u> or <u>value2</u> etc.  The
    operator (>= in this example) can be one
    of =, <, >, <=, >=, <>, or !=.  If you specify more
    than one value, they
    are combined in an OR configuration (ie. a row matches
    if any of the values match).  If you provide
    more than one &filter= clause, they are combined
    successively in an AND configuration (ie. a row matches
    only if all the filters are true).

 -  <b>&q=<u>value1</u>,<u>value2</u>,...</b>  
    Show only rows where any of the columns contain the
    substring <u>value1</u> or <u>value2</u> etc.  If more
    than one value is specified, they are combined in an OR
    configuration.  If you provide more than one &q= clause,
    they are combined successively in an AND configuration.

 -  <b>&order=<u>[-]key1</u>,<u>[-]key2</u></b>  
    Sort the table in order of <u>key1</u> and then (if key1
    is the same) by <u>key2</u> etc.  If a key starts with
    '-' that means to sort that key in descending order
    (largest to smallest).

 -  <b>&extract_regexp=<u>key</u>=<u>regexp(match)regexp</u></b>  
    Search for the given regular expression in each row in
    the column named <u>key</u>.  If it's found, replace the
    column with the substring in the <u>(match)</u> part of
    the regexp.  For example,
    `&extract_regexp=ver=version-(.*)` would replace a
    string `version-25.4` in column `ver` with the string `25.4`.

 -  <b>&group=<u>key1</u>,<u>key2</u>,...;<u>val1</u>,<u>val2</u>,...</b>  
    Summarize the table data by summing and counting.  This
    operation works like a simplified version of SQL's
    "group by" clause.  In the resulting output, the order
    of the columns will be
    <u>key1</u>,<u>key2</u>,...,<u>val1</u>,<u>val2</u>... 
    and there will only be at most one row with any
    particular combination of <u>key1</u>,<u>key2</u>,... 
    fields.  The <u>val</u> columns will be summed (if they
    were already numerical) or counted (if they were
    non-numeric).
    
    A clause like `&group=a,b;x,y` (if x is a string and y
    is a number) would be equivalent to this in SQL: `select
    a, b, count(x) x, sum(y) y from MyTable group by a, b`
   
    If you apply multiple <b>&group=</b> clauses, it works like
    using multiple nested subqueries in SQL.  (That is, the
    output of one <b>&group=</b> clause becomes the MyTable
    of the next one.)
   
    If you leave out the ';' and the <u>val</u> column
    names, the default is to automatically include all
    columns other than the <u>key</u> columns.
   
    If you include the ';' but leave out the <u>val</u>
    column names, that means you don't want any value
    columns (so only the key fields will be included, and
    nothing will be summed or counted at that step).  So
    `&group=a,b;` (with a trailing semicolon) is equivalent
    to this in SQL: `select a, b from MyTable group by a,
    b`.
 
 -  <b>&treegroup=<u>key1</u>,<u>key2</u>,...;[<u>val1</u>,[<u>val2</u>]]</b>  
    Like <b>&group=</b>, but produces an output table arranged hierarchically
    by each <u>key1</u>..<u>keyn</u>, so you can drill down.  There can be
    zero, one, or two <u>val</u> columns; the first value is the size of
    each box in the tree view (if omitted, they are all the same size), and
    the second value is the colour of each box (if omitted, the colour varies
    with the size).  <b>&treegroup=</b> isn't really useful unless you also
    use <b>&chart=tree</b>.

 -  <b>&pivot=<u>rowkeys...</u>;<u>colkeys...</u>;<u>valkeys...</u></b>  
    A <b>&pivot=</b> clause works like a <b>&group=</b>
    clause, but creates a
    [pivot table](http://en.wikipedia.org/wiki/Pivot_table). 
    Pivot tables are a bit complicated; the easiest way to
    learn about them is to play with an example.
    [Here's one to start
    with](/?url=example1.json&group=date,flag,ver,serial;&pivot=date,ver;flag;serial).
   
    The simplest way to think of a pivot table is like this:
    the values originally in the columns named by <u>rowkeys</u>
    end up down the left of the output table.  The values
    originally in the columns named by <u>colkeys</u> end up
    as headings across the top of the output table.  The values
    originally in the columns named by <u>valkeys</u> end up
    as values in the body section of the output table.  A
    pivot table is very handy when you have raw data in
    SQL-like format and you want to rearrange it to be
    suitable for charting (where each line in a line chart,
    say, is usually one column of the table).
   
    If the <u>rowkeys</u> section is empty, the output will
    have exactly one row (with all the value fields counted
    or summed into that one row).  If the <u>colkeys</u>
    section is empty, the <b>&pivot=</b> operation is
    essentially equivalent to a
    <b>&group=<u>rowkeys...</u>;<u>valkeys...</u></b> operation. 
    If the <u>valkeys</u> section is empty, there are no
    values used to calculate the table body, so it is
    equivalent to an <b>&group=<u>rowkeys...</u>;</b>
    operation.
 
 -  <b>&chart=<u>charttype</u></b>  
    Instead of showing a table of values, show a chart.  The
    available <u>charttypes</u> are currently: stacked (a
    stacked area chart), line, spark, column, bar, pie,
    tree (see <b>treegroup</b>), candle, timeline, dygraph, dygraph+errors.
 
 -  <b>&title=<u>title</u></b>  
    Add a title to the chart.


## Example 1

Here is some raw data [(source)](example2.json.txt) produced by an
analytics program:

<iframe src="example2.json.txt">
</iframe>

(Tip: in the tables and charts below, click the "Edit" link in the
upper-right corner to see how the query works.)

Afterquery can render it as a table like this:

<iframe src="/?url=example2.json">
</iframe>

Or pre-sort the table for you like this:

<iframe src="/?url=example2.json&order=state,-date">
</iframe>

Or filter it by date:

<iframe src="/?url=example2.json&filter=date<2012-11-10&filter=date>=2012-11-01">
</iframe>

Or summarize the results (like a "group by" in SQL):

<iframe src="/?url=example2.json&group=date">
</iframe>

Or summarize and display only a subset of columns:

<iframe src="/?url=example2.json&group=date;NumDevices">
</iframe>

Or do a [pivot table](http://en.wikipedia.org/wiki/Pivot_table)
(converting rows into columns):

<iframe src="/?url=example2.json&pivot=date;state;NumDevices">
</iframe>

Or filter, then pivot, and then make a chart!

<iframe
src="/?url=example2.json&order=date,state&filter=date>=2012-11-01&filter=date<2012-11-14&pivot=date;state;NumDevices&chart=stacked&title=Devices Rebooted/Upgraded by Date">
</iframe>


## Example 2

Here's another dataset:

<iframe src="/?url=example1.json">
</iframe>

We can use two consecutive grouping operations to first get
a list of serial numbers for each version, and then get the
count of serial numbers per version [(link)](/?url=example1.json&group=ver,serial;&group=ver;serial&order=ver):

<iframe src="/?url=example1.json&group=ver,serial;&group=ver;serial&order=ver">
</iframe>

Hmm, those version numbers are ugly because some of them
have extra debug information after them.  Let's trim it
out using a regex:

<iframe
src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=ver,serial;&group=ver;serial&order=ver">
</iframe>

And make a pivot table to easily show the pattern over
time:

<iframe
src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&pivot=date;ver;serial">
</iframe>

Trim out some outliers:

<iframe
src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&group=date,ver;serial&filter=serial&gt;10&filter=ver&gt;&pivot=date;ver;serial">
</iframe>

And graph it:

<iframe
src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&group=date,ver;serial&filter=serial&gt;10&filter=ver&gt;&pivot=date;ver;serial&chart=stacked">
</iframe>

Or graph a subset of the data:

<iframe
src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&q=v35,v37,v36&pivot=date;ver;serial&chart=line">
</iframe>

Or maybe show the top 4 versions:

<iframe
src="/?url=example1.json&group=ver,serial;&filter=ver&gt;&order=ver&group=ver;serial&order=-serial&limit=4&chart=pie">
</iframe>


## Chart gallery

<div class="gallery">
<iframe src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&group=date,ver;serial&filter=serial&gt;10&filter=ver&gt;&pivot=date;ver;serial&chart=stacked"></iframe>
<iframe src="/?url=example1.json&extract_regexp=ver=(v)ersion-([^-.]*)&group=date,ver,serial;&order=date,ver&group=date,ver;serial&filter=serial&gt;10&filter=ver&gt;&pivot=date;ver;serial&chart=line"></iframe>
<iframe src="/?url=example1.json&group=ver,serial;&filter=ver&gt;&order=ver&group=ver;serial&order=-serial&limit=4&chart=column"></iframe>
<iframe src="/?url=example1.json&group=ver,serial;&filter=ver&gt;&order=ver&group=ver;serial&order=-serial&limit=4&chart=bar"></iframe>
<iframe src="/?url=example1.json&group=ver,serial;&filter=ver&gt;&order=ver&group=ver;serial&order=-serial&limit=4&chart=pie"></iframe>
<iframe src="/?url=example1.json&group=flag,ver,serial;&treegroup=flag,ver;serial&chart=tree"></iframe>
<iframe src="/?url=example2.json&pivot=date;state;NumDevices&group=date,upgraded,rebooted,rebooted,idle&chart=candle"></iframe>
<iframe src="/?url=example2.json&pivot=date;state;NumDevices&chart=timeline"></iframe>
<iframe src="/?url=example2.json&pivot=date;state;NumDevices&chart=dygraph"></iframe>
<iframe src="/?url=example2.json&pivot=date;state;NumDevices&group=date,idle,rebooted,rebooted,upgraded&chart=dygraph+errors"></iframe>
<iframe class='spark' src="/?url=example1.json&filter=ver=oldversion-1&group=date,ver,serial;&pivot=date;ver;serial&chart=spark"></iframe>
<iframe class='spark' src="/?url=example1.json&filter=ver=oldversion-17&group=date,ver,serial;&pivot=date;ver;serial&chart=spark"></iframe>
<iframe class='spark' src="/?url=example1.json&filter=ver=oldversion-19&group=date,ver,serial;&pivot=date;ver;serial&chart=spark"></iframe>
</div>


## Where can I get a jsonp data source?

There are lots of them out on the web.  If your favourite
database query or reporting engine doesn't support jsonp,
ask them to add it!


## Need help?  Want to contribute?

Email <apenwarr@google.com>.  Probably there'll be a
mailing list eventually.

The complete source code is contained in <a
href="/render.js">render.js</a>.



<div style='padding-bottom: 5in;'></div>
