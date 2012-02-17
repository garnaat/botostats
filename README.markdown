botostats
---------

Sometimes it's nice to know how many people are using your software.
It can be nice for your ego but, more importantly, it can allow you
to see how usage changes over time.  Is the customer base growing?
Shrinking? Are people downloading the newest release?  If not, I wonder
why?  And who the hell is still downloading that release from three
years ago?

The botostats package serves two main purposes:

1. Gather download statistics from as many places as possible.  This
currently includes PyPI stats (downloaded from crate.io but same info),
the Google Code downloads lists, and the github download tab.  Of these,
only github provides a true API so for the others I use BeautifulSoup to
grab the data from the HTML pages.

2. Create web pages that display the gathered information in a number of
(hopefully) interesting ways.

