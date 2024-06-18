@echo off
sphinx-build -b latex . _build/latex
cd _build/latex
pdflatex forecastingapp.tex
pdflatex forecastingapp.tex
pdflatex forecastingapp.tex
cd ../..
