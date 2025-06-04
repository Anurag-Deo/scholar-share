<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# The tikzposter class *

**Authors:** Pascal Richter, Elena Botoeva, Richard Barnard, Dirk Surmann
**Contact:** tikzposter@mathcces.rwth-aachen.de
**Wiki:** https://bitbucket.org/surmann/tikzposter/wiki/
**Date:** January 17, 2014

---

## Abstract

This document class aims to provide a simple way of using LaTeX and TikZ for generating good looking scientific posters.

---

## Contents

1. Introduction
2. Creating a Poster
3. Options for the Document Class
4. The Poster Contents
 4.1 Title Matter
 4.2 Blocks
 4.3 Notes
 4.4 Columns and Subcolumns
5. Poster Layout
 5.1 Setting the colors
 5.2 Setting the layout
 5.3 Background style
 5.4 Title style
 5.5 Block style
 5.6 Inner Block styles
 5.7 Note style
6. Poster template
7. Poster example
8. Appendix
 8.1 Available variables

---

## 1 Introduction

The `tikzposter` document class simplifies formatting and generating scientific posters in PDF format using the TikZ package. Posters are composed of blocks arranged in aligned columns over a background. It automatically manages spacing and block lengths, while allowing user control over column widths. Only PDF output is supported due to TikZ reliance.

Users can start with the included template `tikzposter-template.tex`, the minimal example in Section 2, or the example file `tikzposter-example.tex` which shows formatting options. Section 3 describes the `\documentclass` options. Inside the document environment, title and blocks are created with commands explained in Section 4. Section 5 explains appearance customization. Section 8 lists useful variables.

**Required packages:** LaTeX2e, tikz, calc, ifthen, ae, xstring, etoolbox, xkeyval.

**Changes from previous versions:** Background and title formatting customization, block shifting and formatting, introduction of note objects, and modified color themes. Backwards compatibility is not guaranteed for some formatting options.

---

## 2 Creating a Poster

Minimal example:

```latex
\documentclass{tikzposter} % See Section 3
\title{Title} \institute{Inst} % See Section 4.1
\author{Auth} \titlegraphic{Logo}
\usetheme{Basic} % See Section 5
\begin{document}
    \maketitle % See Section 4.1
    \block{BlocktitleA}{Blocktext} % See Section 4.2
    \begin{columns} % See Section 4.4
        \column{0.3} % See Section 4.4
        \block{BlocktitleB}{Blocktext}
        \column{0.7}
        \block{BlocktitleC}{Blocktext}
        \note{Notetext} % See Section 4.3
    \end{columns}
\end{document}
```


---

## 3 Options for the Document Class

Declare the class with options:

```latex
\documentclass[options]{tikzposter}
```


### Page geometry options:

- **Font size:** 12pt, 14pt, 17pt, 20pt, or 25pt
- **Paper size:** a0paper, a1paper, or a2paper
- **Orientation:** landscape or portrait


### Additional spacing options (format: `<variable>=<value>`):

- `margin`: Margin between poster edge and paper edge
- `innermargin`: Margin from poster edge to outermost block edge
- `colspace`: Horizontal spacing between columns
- `subcolspace`: Horizontal spacing between subcolumns (see Section 4.4)
- `blockverticalspace`: Vertical spacing between blocks

Example usage:

```latex
\documentclass[25pt, a0paper, portrait, margin=0mm, innermargin=15mm,
    blockverticalspace=15mm, colspace=15mm, subcolspace=8mm]{tikzposter}
```

To disable the "how the poster was created" comment in the lower right, add `\tikzposterlatexaffectionproofoff` in the preamble.

---

## 4 The Poster Contents

### 4.1 Title Matter

Use `\author{}`, `\institute{}`, and `\title{}` as usual. Add a logo with `\titlegraphic{}`.

Create the title with:

```latex
\maketitle[options]
```

Options include:

- `width`: Width of the title area
- `roundedcorners`, `linewidth`, `innersep`: TikZ box parameters for the title box
- `titletotopverticalspace`, `titletoblockverticalspace`: Vertical spaces around title
- `titlegraphictotitledistance`: Vertical distance between logo and title text
- `titletextscale`: Scale factor for title text size

Default title format example:

```latex
\settitle{ \centering \vbox{
    \@titlegraphic \\[\TP@titlegraphictotitledistance] \centering
    \color{titlefgcolor} {\bfseries \Huge \sc \@title \par}
    \vspace*{1em}
    {\huge \@author \par} \vspace*{1em} {\LARGE \@institute}
}}
```


---

### 4.2 Blocks

Create blocks with:

```latex
\block[options]{title}{text}
```

- By default, block width equals page or column width minus margins.
- Title is shown in a smaller block above the content.
- Multiline titles are supported.
- Block length adjusts automatically to content.
- Multiple blocks can be stacked in columns; beware of overflow.

**Block options:**

- `titleoffsetx`, `titleoffsety`: Shift title block position
- `bodyoffsetx`, `bodyoffsety`: Shift body block position
- `titlewidthscale`, `bodywidthscale`: Scale widths relative to default (e.g., 0.5 halves width)
- `titleleft`, `titlecenter`, `titleright`: Title text alignment (default center)
- `bodyverticalshift`: Extra vertical space between title and body
- `roundedcorners`, `linewidth`: Corner roundness and border thickness
- `titleinnersep`, `bodyinnersep`: Inner spacing between edges and content

Example:

```latex
\block[titleleft,titleoffsetx=2em,titleoffsety=1em,bodyoffsetx=2em,
    bodyoffsety=1em,titlewidthscale=.6, bodywidthscale=.8, roundedcorners=14,
    linewidth=8mm, bodyinnersep=4em, titleinnersep=2em]
    {Sample Block}{Text\\Text\\Text Text}
```


---

### Block objects

- **Inner blocks:** Use `\innerblock[options]{Heading}{Text}` inside blocks.
Options include width, scaling, alignment, offsets, rounded corners, line width, inner spacing.
- **Colored boxes:** Use `\coloredbox[options]{Text}` to highlight parts of block body.
Options: width, linewidth, roundedcorners, bgcolor, fgcolor, framecolor.
- **Figures:** Use `tikzfigure` environment instead of standard `figure`:

```latex
\begin{tikzfigure}[Caption of the figure]
    \label{fig:fig1}
    Figure content
\end{tikzfigure}
```


---

### 4.3 Notes

Notes are small objects attached to blocks, created with:

```latex
\note[options]{contents}
```

**Placement options:**

- `targetoffsetx`, `targetoffsety`: Shift the target point (center of previous block)
- `angle`, `radius`: Position note at distance `radius` and angle `angle` from target
- `width`: Width of the note
- `connection`: Draw connection line/arrow from note to target
- `rotate`: Rotate entire note by angle
- `roundedcorners`, `linewidth`, `innersep`: Appearance options

Notes appear over background and blocks; manual placement is needed.

Example:

```latex
\note[targetoffsetx=2cm, targetoffsety=-1cm, angle=90, radius=3cm,
    width=5cm, rotate=30, connection, linewidth=.2cm,
    roundedcorners=30, innersep=1cm]{Text}
```


---

### 4.4 Columns and Subcolumns

- Use the `columns` environment to create multiple columns:

```latex
\begin{columns}
    \column{<width>}
    % Blocks here
    \column{<width>}
    % Blocks here
\end{columns}
```

- Column widths are relative or absolute; sum should not exceed `\textwidth`.
- Use `\colwidth` to refer to current column width.
- Use `subcolumns` environment inside a column for subcolumns:

```latex
\begin{subcolumns}
    \subcolumn{<width>}
    % Blocks here
    \subcolumn{<width>}
    % Blocks here
\end{subcolumns}
```

- `\subcolwidth` refers to current subcolumn width.

---

## 5 Poster Layout

Poster appearance can be customized in:

- Colors
- Background
- Title style
- Block style
- Inner block style
- Note style

Use `\usetheme{layout style}` to load predefined or custom themes. Predefined themes include Default, Rays, Basic, Simple, Envelope, Wave, Board, Autumn, Desert.

---

### 5.1 Setting the colors

Colors are defined by:

- **Palette:** Defines three base colors. Use `\usecolorpalette{}`. Included palettes: Default, BlueGrayOrange, GreenGrayViolet, PurpleGrayBlue, BrownBlueOrange.
- **Style:** Defines how palette colors are applied. Use `\usecolorstyle[options]{style name}`. Included styles: Default, Australia, Britain, Sweden, Spain, Russia, Denmark, Germany.

**Color components:**

- Background: `backgroundcolor`, `framecolor`
- Title: `titlefgcolor`, `titlebgcolor`
- Block: `blocktitlebgcolor`, `blocktitlefgcolor`, `blockbodybgcolor`, `blockbodyfgcolor`
- Inner block: `innerblocktitlebgcolor`, `innerblocktitlefgcolor`, `innerblockbodybgcolor`, `innerblockbodyfgcolor`
- Colored boxes: Use note background color by default
- Notes: `notebgcolor`, `notefgcolor`, `noteframecolor`
- Text colors as above

**Define custom palette:**

```latex
\definecolorpalette{sampleColorPalette} {
    \definecolor{colorOne}{named}{green}
    \definecolor{colorTwo}{named}{black}
    \definecolor{colorThree}{named}{cyan}
}
```

**Define custom style:**

```latex
\definecolorstyle{sampleColorStyle} {
    \definecolor{colorOne}{named}{blue}
    \definecolor{colorTwo}{named}{yellow}
    \definecolor{colorThree}{named}{orange}
}{
    % Background Colors
    \colorlet{backgroundcolor}{colorOne}
    \colorlet{framecolor}{black}
    % Title Colors
    \colorlet{titlefgcolor}{black}
    \colorlet{titlebgcolor}{colorOne}
    % Block Colors
    \colorlet{blocktitlebgcolor}{colorThree}
    \colorlet{blocktitlefgcolor}{white}
    \colorlet{blockbodybgcolor}{white}
    \colorlet{blockbodyfgcolor}{black}
    % Innerblock Colors
    \colorlet{innerblocktitlebgcolor}{white}
    \colorlet{innerblocktitlefgcolor}{black}
    \colorlet{innerblockbodybgcolor}{colorThree!30!white}
    \colorlet{innerblockbodyfgcolor}{black}
    % Note colors
    \colorlet{notefgcolor}{black}
    \colorlet{notebgcolor}{colorTwo!50!white}
    \colorlet{noteframecolor}{colorTwo}
}
```


---

### 5.2 Setting the layout

Poster components: title, blocks, notes.

Use `\definelayouttheme{name}{...}` to define a theme that sets styles for colors, background, title, blocks, inner blocks, and notes.

Example:

```latex
\definelayouttheme{sample}{
    \usecolorstyle[colorPalette=sampleColorPalette]{sampleColorStyle}
    \usebackgroundstyle{sample}
    \usetitlestyle{Test}
    \useblockstyle{sample}
    \useinnerblockstyle{sample}
    \usenotestyle{Corner}
}
```


---

### 5.3 Background style

Default background is a vertical gradient based on `backgroundcolor`.

Use `\usebackgroundstyle{style name}` to select a predefined style (Default, Rays, VerticalGradation, BottomVerticalGradation, Empty).

Define custom background:

```latex
\definebackgroundstyle{samplebackgroundstyle}{
    \draw[inner sep=0pt, line width=0pt, color=red, fill=backgroundcolor!30!black]
        (bottomleft) rectangle (topright);
}
```

Then call `\usebackgroundstyle{samplebackgroundstyle}`.

**Variables available:**

- `\textwidth`, `\textheight` (poster content size after margins)
- `\titlegraphicheight`, `\titletotopverticalspace`, `\titleinnersep`
- `backgroundcolor`
- `topright`, `bottomleft` (TikZ nodes for poster corners)

---

### 5.4 Title style

Use `\usetitlestyle[options]{style name}` to select predefined styles: Default, Basic, Envelope, Wave, VerticalShading, Filled, Empty.

Define custom title style:

```latex
\definetitlestyle{sampletitle}{
    width=500mm, roundedcorners=20, linewidth=2pt, innersep=5pt,
    titletotopverticalspace=15mm, titletoblockverticalspace=30mm
}{
    \begin{scope}[line width=\titlelinewidth, rounded corners=\titleroundedcorners]
        \draw[color=blocktitlebgcolor, fill=titlebgcolor]
            (\titleposleft,\titleposbottom) rectangle (\titleposright,\titlepostop);
    \end{scope}
}
```

Call with `\usetitlestyle{sampletitle}`.

**Useful variables:**

- `\textwidth`, `\textheight`
- `\titlewidth`, `\titlegraphicheight`
- `\titlelinewidth`, `\titleinnersep`
- `\titletotopverticalspace`
- `titlebgcolor`
- `\titleposleft`, `\titleposright`, `\titleposbottom`, `\titlepostop`

---

### 5.5 Block style

Use `\useblockstyle[options]{style name}` to select predefined styles: Default, Basic, Minimal, Envelope, Corner, Slide, TornOut.

Define custom block style:

```latex
\defineblockstyle{sampleblockstyle}{
    titlewidthscale=0.9, bodywidthscale=1,titleleft,
    titleoffsetx=0pt, titleoffsety=0pt, bodyoffsetx=0mm, bodyoffsety=15mm,
    bodyverticalshift=10mm, roundedcorners=5, linewidth=2pt,
    titleinnersep=6mm, bodyinnersep=1cm
}{
    \draw[color=framecolor, fill=blockbodybgcolor,
        rounded corners=\blockroundedcorners] (blockbody.south west)
        rectangle (blockbody.north east);
    \ifBlockHasTitle
        \draw[color=framecolor, fill=blocktitlebgcolor,
            rounded corners=\blockroundedcorners] (blocktitle.south west)
            rectangle (blocktitle.north east);
    \fi
}
```

Parameters available:

- `\ifBlockhasTitle` (boolean)
- `blocktitle`, `blockbody` (TikZ nodes)
- `\blockroundedcorners`, `\blocklinewidth`, `\blockbodyinnersep`, `\blocktitleinnersep`
- `framecolor`, `blocktitlebgcolor`, `blockbodybgcolor`

---

### 5.6 Inner Block styles

Use `\useinnerblockstyle{style name}` to select styles: Default, Table, or copies of block styles.

Define custom inner block style:

```latex
\defineinnerblockstyle{stylename}{default values}{commands}
```

Parameters:

- `\ifInnerblockHasTitle` (boolean)
- `innerblocktitle`, `innerblockbody` (TikZ nodes)
- `\innerblockroundedcorners`, `\innerblocklinewidth`, `\innerblockbodyinnersep`, `\innerblocktitleinnersep`
- `innerblockbodybgcolor`, `innerblocktitlebgcolor`, `framecolor`

---

### 5.7 Note style

Use `\usenotestyle[options]{style name}` to select included note styles: Default, Corner, VerticalShading, Sticky.

Define custom note style:

```latex
\definenotestyle{samplenotestyle}{
    targetoffsetx=0pt, targetoffsety=0pt, angle=45, radius=8cm,
    width=6cm, connection=true, rotate=0, roundedcorners=0, linewidth=1pt,
    innersep=0pt%
}{
    \ifNoteHasConnection
        \draw[thick] (notecenter) -- (notetarget) node{$\bullet$};
    \fi
    \draw[draw=notebgcolor,fill=notebgcolor,rotate=\noterotate]
        (notecenter.south west) rectangle (notecenter.north east);
}
```

Parameters:

- `\ifNoteHasConnection` (boolean)
- `notetarget`, `notecenter` (TikZ nodes)
- `\noterotate`, `\notelinewidth`, `\noteroundedcorners`, `\noteinnersep`
- `noteframecolor`, `notefgcolor`, `notebgcolor`

---

## 6 Poster template

Minimal template example:

```latex
\documentclass{tikzposter} % Options can be included here

% Title, Author, Institute
\title{Template Poster}
\author{Author(s)}
\institute{Institute}
\titlegraphic{LogoGraphic Inserted Here}

% Choose Layout
\usetheme{Default}

\begin{document}

% Title block
\maketitle

\block{Basic Block}{Text}

\begin{columns}

% FIRST column
\column{0.6} % Width relative to text width
\block{Large Column}{Text\\Text\\Text Text Text}
\note{Note with default behavior}
\note[targetoffsetx=12cm, targetoffsety=-1cm, angle=20, rotate=25]{Note \\ offset and rotated}

\block{Block titles with enough text will automatically obey spacing requirements}{Text\\Text}
\block{Sample Block 4}{T\\E\\S\\T}

% SECOND column
\column{0.4}
\block[titleleft]{Smaller Column}{Test}
\block[titlewidthscale=0.6, bodywidthscale=0.8]{Variable width title}{Block with smaller width.}
\block{}{Block with no title}

% Subcolumns
\begin{subcolumns}
    \subcolumn{0.27} \block{1}{First block.} \block{2}{Second block}
    \subcolumn{0.4} \block{Sub-columns}{Sample subblocks\\Second subcolumn}
    \subcolumn{0.33} \block{4}{Fourth} \block{}{Final Subcolumn block}
\end{subcolumns}

% Bottom block
\block{Final Block in column}{Sample block.}

\end{columns}

\block[titleleft, titleoffsetx=2em, titleoffsety=1em, bodyoffsetx=2em,
    bodyoffsety=-2cm, roundedcorners=10, linewidth=0mm, titlewidthscale=0.7,
    bodywidthscale=0.9, bodyverticalshift=2cm, titleright]
{Block outside of Columns}{Along with several options enabled}

\end{document}
```


---

## 7 Poster example

An extended example file `tikzposter-example.tex` is included with the package, demonstrating various options beyond the minimal template.

---

## 8 Appendix

### 8.1 Available variables

Useful variables for creating custom themes/styles:

- `\TP@visibletextwidth`, `\TP@visibletextheight`: Width and height of poster area excluding margins
- `\TP@titleinnersep`, `\TP@titletoblockverticalspace`: Spacing options
- `\titlewidth`, `\titleheight`: Title block dimensions
- `\titlegraphicheight`: Height of title graphic
- `\titletotopverticalspace`: Vertical space from top
- `\TP@colspace`, `\TP@coltop`, `\TP@colbottom`, `\TP@colcenter`, `\TP@colwidth`: Column spacing and dimensions
- `\TP@subcolspace`, `\TP@subcoltop`, `\TP@subcolbottom`, `\TP@subcolcenter`, `\subcolwidth`: Subcolumn equivalents
- `\TP@blockverticalspace`, `\TP@blocktitleinnersep`, `\TP@blockbodyinnersep`: Block spacing
- `\TP@blockcenter`: Horizontal center of current block
- `\blockwidth`, `\blockbodyheight`, `\blocktitleheight`: Current block dimensions
- `\TP@blocktop`: Y-coordinate of block top edge
- `\TP@blocktitleoffsetx`, `\TP@blocktitleoffsety`: Title block position shifts
- `\TP@blockbodyoffsetx`, `\TP@blockbodyoffsety`: Body block position shifts
- `\blockroundedcorners`, `\blocklinewidth`, `\blockbodyinnersep`, `\blocktitleinnersep`: Block style parameters
- `\TP@noteinnersep`: Note inner separation
- `\TP@noteradius`, `\TP@notetargetoffsetx`, `\TP@notetargetoffsety`, `\notewidth`: Note placement parameters
- `\noteheight`: Note height
- `\noteroundedcorners`, `\notelinewidth`, `\noteinnersep`: Note style parameters

**Nodes for styles:**

- Title node covers entire title area; edges stored in `\titlepostop`, `\titleposbottom`, `\titleposleft`, `\titleposright`.
- For blocks, `blocktitle` and `blockbody` nodes cover respective areas.

---

*This document corresponds to tikzposter v2.0, dated 2014/01/15.*

<div style="text-align: center">⁂</div>

[^1]: tikzposter.pdf

