# Cutlist template

## TL;DR:

Download [blank-ledger.svg](blank-ledger.svg) or [blank-a3.svg](blank-a3.svg) and print it out.

Want to customize it? Keep reading.

## What is all this?

This repository contains Python code that creates an SVG file for a cut list template.

A cut list is a list of the individual pieces of wood that make up a piece of furniture (or some other wooden object). It's usually derived from a drawing. Making the cut list is a chance to double check the drawing for errors, and make a plan for how to turn rough lumber into the finished pieces. That plan rarely survives a trip to the lumber yard where none of the boards are the lengths or widths of the ones you hoped to find.


## Printing

SVG renderers vary somewhat in their ability to correctly render the .svg files the code generates. I recommend any modern browser for either printing or creating a PDF file.

## Using the included .svg files

### You don't need to download or run any code

If you just want a nice blank template, the blank files in either US Ledger or ISO A3 will work just fine.

### Customization without running the Python code

Download the blank .svg file of your choosing, and edit the title block content elements directly. You can find them by looking for lines that start with the following:

```xml
<text class="title-content"
```

This is obviously a pain in the ass and requires some knowledge of how svg and xml work. You also won't be able to (easily) change the number of rows in the address, for instance.

## Customizing a cut list template

The first time you run `make`, `make` will create a `private.mk` file for you. Edit the `private.mk` file, customizing it as you see fit, and re-run `make`. [private.mk.example](private.mk.example) includes information about what can be customized.

## Using this code

### Python version

The Python code probably requires Python 3.

### Dependencies

The dependencies are specified in [requirements.txt](requirements.txt). Nothing is pinned to a specific version.

### Output

The script defaults to writing the svg file to stdout, but you may specify an output file as a positional argument if you'd like to. 

### Linked stylesheet

The default cut list template embeds its stylesheet. `--link-style` will generate one with a linked stylesheet instead. This is nerd stuff. You probably want an embedded stylesheet. If you want a linked one, you probably don't need me to explain why.

Browsers and CorelDraw seem to understand external stylesheets. Other svg renderers are a crapshoot.

## License

The code in this repository is licensed under the terms of [WTFPL](http://wtfpl.net). This code is of no commercial value to me. I build [furniture](https://longwalkwoodworking.com).

## Q/A

### Why not an FAQ?

I haven't gotten enough questions to order them by frequency.

### What if there's a bug?

I'd be very surprised if there's only one.

If you find a bug, please open an issue and submit a pull request with a fix if you can. I reserve the right to close issues for bugs if there's no pull request and I can't be bothered to fix it myself.

### Will you add a feature?

I doubt it.

If it involves any sort of screwing around with pip, wheels, eggs, or anything else involved in distributing python code, absolutely not. Nor will I take a pull request. I have no desired to spend enough time getting familiar with pip, wheels, eggs, or whatever to review it intelligently.

### What kind of support is that?

The kind you get for zero dollars from a former programmer :-)

I build furniture. This code is good enough to enable me to do my job. Anything beyond that is my own professional courtesy as a recovering programmer.

### Are you really a Python programmer?

I gather you've looked at the code. I've primarily worked professionally writing C and Java. I've written Python as well, but a whole lot less of it.

### What's up with the git history?

It's hard to believe, but the original code was even rougher than it is now. Notably, it included my contact info in the Python code. I redacted it by blowing away the history and reinitializing the repository.

### Why SVG as an output format?

Because I was already using svgwrite for another project. Certainly not because I know it well.

### Are there any tests?

Nope. I'm assuming a great many people way smarter than I am are testing [svgwrite](https://svgwrite.readthedocs.io/en/latest/svgwrite.html). If the output looks right, it probably is right. If it's not, it's almost certainly my fault, not svgwrite's fault.

### Why are the generated files checked in to the repository?

So you don't have to run the python script if you just want to print a blank cut list template.

Also because there aren't any tests. If the generated files have changed, it's a reminder to make sure they still look right.

### Can I use this in a commercial product?

Commercial use is governed by the terms of the [license](LICENSE).
