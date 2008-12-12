" Vim syntax file example
" Put it to ~/.vim/after/syntax/ and tailor to your needs.

" To make things fancier set
"    hi IncludedFunction gui=italic guifg=#9b00a6
"    hi IncludedFunction2 guifg=#7200c9
" in your theme file to appropriate colors.  IncludedFunction are 
" the build in functions like gtk.gdk.threads_init() and
" IncludedFunction2 are the objects like gtk.Widget 

if version < 600
  so <sfile>:p:h/pygtk_syntax.vim
else
  runtime! syntax/pygtk_syntax.vim
endif

" vim: set ft=vim :
