# Beamer Presentation Templates and Guidelines

This directory contains templates and guidelines for generating academic presentations using Beamer.

## Template Types

### Academic Template
- Professional academic styling
- Clean blue color scheme
- Suitable for conferences and research presentations
- Includes navigation and section structure

### Corporate Template  
- Modern, professional business styling
- Clean, minimal design
- Suitable for industry presentations
- Corporate color schemes

### Minimal Template
- Simple, clean design
- Minimal visual elements
- Focus on content
- Suitable for technical presentations

## Beamer Best Practices

### Document Structure
```latex
\documentclass{beamer}
\usetheme{Madrid}  % or other theme
\usecolortheme{default}

% Packages
\usepackage{tikz}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amsfonts}

% TikZ libraries
\usetikzlibrary{shapes,arrows,positioning,fit,backgrounds}

% Title information
\title{Presentation Title}
\author{Author Names}
\institute{Institution}
\date{\today}

\begin{document}

\maketitle

% Content slides
\begin{frame}{Frame Title}
  Frame content
\end{frame}

\end{document}
```

### Slide Types

#### Title Slide
```latex
\begin{frame}[plain]
  \titlepage
\end{frame}
```

#### Content Slide
```latex
\begin{frame}{Title}
  \begin{itemize}
    \item Point 1
    \item Point 2
    \item Point 3
  \end{itemize}
\end{frame}
```

#### Two-Column Layout
```latex
\begin{frame}{Title}
  \begin{columns}
    \begin{column}{0.5\textwidth}
      Left content
    \end{column}
    \begin{column}{0.5\textwidth}
      Right content
    \end{column}
  \end{columns}
\end{frame}
```

#### TikZ Diagram Slide
```latex
\begin{frame}{Diagram Title}
  \begin{center}
    \begin{tikzpicture}
      % TikZ content
    \end{tikzpicture}
  \end{center}
\end{frame}
```

### Color Schemes

#### Academic (Blue)
- Primary: RGB(0,51,102)
- Secondary: RGB(0,102,153) 
- Accent: RGB(204,229,255)

#### Corporate (Gray/Blue)
- Primary: RGB(51,51,51)
- Secondary: RGB(0,123,191)
- Accent: RGB(242,242,242)

#### Minimal (Black/White)
- Primary: RGB(0,0,0)
- Secondary: RGB(102,102,102)
- Accent: RGB(248,248,248)

### Font Guidelines

- Main text: Use default Beamer fonts
- Code: Use `\texttt{}` or `\verb||`
- Math: Use `$...$` for inline, `\[...\]` for display
- Emphasis: Use `\textbf{}` for bold, `\emph{}` for italic

### Layout Guidelines

- Maximum 6-8 bullet points per slide
- Use consistent spacing
- Include slide numbers
- Add navigation if presentation is long
- Use consistent color scheme throughout
- Ensure good contrast for readability

### TikZ Integration

- Keep diagrams simple and clear
- Use consistent styling across diagrams
- Ensure diagrams fit within slide boundaries
- Use appropriate fonts and sizes
- Include proper labels and annotations
