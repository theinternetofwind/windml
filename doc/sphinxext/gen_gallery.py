# -*- coding: UTF-8 -*-

# generate a thumbnail gallery of examples
template = """\
{%% extends "layout.html" %%}
{%% set title = "Thumbnail gallery" %%}


{%% block body %%}

<h3>Click on any image to see full size image and source code</h3>
<br/>

<li><a class="reference internal" href="#">Gallery</a><ul>
%s
</ul>
</li>

%s
{%% endblock %%}
"""

import os, glob, re, sys, warnings
import matplotlib.image as image

multiimage = re.compile('(.*?)(_\d\d){1,2}')

def make_thumbnail(args):
    image.thumbnail(args[0], args[1], 0.3)

def out_of_date(original, derived):
    return (not os.path.exists(derived) or
            os.stat(derived).st_mtime < os.stat(original).st_mtime)

def gen_gallery(app, doctree):
    if app.builder.name != 'html':
        return

    outdir = app.builder.outdir
    rootdir = 'plot_directive/mpl_examples'

    # images we want to skip for the gallery because they are an unusual
    # size that doesn't layout well in a table, or because they may be
    # redundant with other images or uninteresting
    skips = set([
        'mathtext_examples',
        'matshow_02',
        'matshow_03',
        'matplotlib_icon',
        ])

    thumbnails = {}
    rows = []
    toc_rows = []

    link_template = """\
    <a href="%s"><img src="%s" border="0" alt="%s"/></a>
    """

    header_template = """<div class="section" id="%s">\
    <h4>%s<a class="headerlink" href="#%s" title="Permalink to this headline">¶</a></h4>"""

    toc_template = """\
    <li><a class="reference internal" href="#%s">%s</a></li>"""

    dirs = ('api', 'pylab_examples', 'mplot3d', 'widgets', 'axes_grid' )

    for subdir in dirs :
        rows.append(header_template % (subdir, subdir, subdir))
        toc_rows.append(toc_template % (subdir, subdir))

        origdir = os.path.join('build', rootdir, subdir)
        thumbdir = os.path.join(outdir, rootdir, subdir, 'thumbnails')
        if not os.path.exists(thumbdir):
            os.makedirs(thumbdir)

        data = []

        for filename in sorted(glob.glob(os.path.join(origdir, '*.png'))):
            if filename.endswith("hires.png"):
                continue

            path, filename = os.path.split(filename)
            basename, ext = os.path.splitext(filename)
            if basename in skips:
                continue

            # Create thumbnails based on images in tmpdir, and place
            # them within the build tree
            orig_path = str(os.path.join(origdir, filename))
            thumb_path = str(os.path.join(thumbdir, filename))
            if out_of_date(orig_path, thumb_path) or True:
                thumbnails[orig_path] = thumb_path

            m = multiimage.match(basename)
            if m is not None:
                basename = m.group(1)

            data.append((subdir, basename,
                         os.path.join(rootdir, subdir, 'thumbnails', filename)))




        for (subdir, basename, thumbfile) in data:
            if thumbfile is not None:
                link = 'examples/%s/%s.html'%(subdir, basename)
                rows.append(link_template%(link, thumbfile, basename))

        if len(data) == 0:
            warnings.warn("No thumbnails were found in %s" % subdir)

        # Close out the <div> opened up at the top of this loop
        rows.append("</div>")

    content = template % ('\n'.join(toc_rows),
                          '\n'.join(rows))

    # Only write out the file if the contents have actually changed.
    # Otherwise, this triggers a full rebuild of the docs

    gallery_path = os.path.join(app.builder.srcdir, '_templates', 'gallery.html')
    if os.path.exists(gallery_path):
        with open(gallery_path, 'r') as fh:
            regenerate = fh.read() != content        
    else:
        regenerate = True
    if regenerate:
        with open(gallery_path, 'w') as fh: 
            fh.write(content)        
    for key in app.builder.status_iterator(
        thumbnails.iterkeys(), "generating thumbnails... ",
        length=len(thumbnails)):
        image.thumbnail(key, thumbnails[key], 0.3)

def setup(app):
    app.connect('env-updated', gen_gallery)
