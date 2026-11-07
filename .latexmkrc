# Use the project-local texmf tree (texmf/) ahead of the system TeX install.
# Packages in it come from the TeX Live 2019 archive to match the system kernel.
# The path is resolved from this file's location, so subfolders can load this
# file with: do '../.latexmkrc';
use Cwd 'abs_path';
use File::Basename 'dirname';
$ENV{TEXMFHOME} = dirname(abs_path(__FILE__)) . '/texmf';
$pdf_mode = 1;
