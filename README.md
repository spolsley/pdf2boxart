# pdf2boxart

In an effort to save some old VHS and CD box art that could otherwise be lost to time, I found myself searching for an easy way to convert multi-page PDFs of scanned images into a box art spread.  Even though there are many pdf2-somethings out there for all types of PDF processing, I couldn't find one to do all of the steps I wanted.  This script is a very simple collection of steps.  It reads a PDF into images, auto-segments each page into an image, and then joins the images into a spread.  The segmentation assumes one image per page and a relatively consistent backdrop.  It uses a sliding window and averaging to downsample the image for a quick threshold comparison, of which each parameter can be optionally adjusted.  It's not particularly complicated, but hopefully parts of it prove useful to others.