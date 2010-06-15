if !exists('g:toggl_api_key')
    finish
endif

if filereadable($VIMRUNTIME."/plugin/toggl.py")
  pyfile $VIMRUNTIME/plugin/toggl.py
elseif filereadable($HOME."/.vim/plugin/toggl.py")
  pyfile $HOME/.vim/plugin/toggl.py
else
  call confirm('toggl.vim: Unable to find toggl.py. Place it in either your home vim directory or in the Vim runtime directory.', 'OK')
  finish
endif

au VimEnter * silent let g:toggl_start_time=strftime("%FT%T")

exec "python toggl = Toggl('". g:toggl_api_key ."')"

au VimLeave * exec "python toggl.send_task('".g:toggl_start_time."','".strftime("%FT%T") ."')"

