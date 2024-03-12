# Help menu

## Commands avalible for Windows and Linux:

### Standalone commands:
!ip = Get public and local ip of target  
!screenshot = Take a screenshot of the targets screens  

### Shell commands:
!shell = execute a shell command on the targets system  
Use "!shell -t 10" to set a timeout for your command. The default is 30 seconds

### File commands
!ls = Lists all the files in a directory
!cd directory = Changes directory
!delete path = Deletes a file
!download path = Downloads a file from the targets computer
!upload = Uploads an attachment to the targets computer

### Clipboard commands:
!clipboard get = Get the targets current clipboard  
!clipboard set = Set the targets clipboard to data of your choice  

### Clipboard Monitor:
The clipboard monitor is a background process that monitors for new items copied to the clipboard and sends them to you

!clipboard monitor start = Starts the Clipboard Monitor  
!clipboard monior stop = Stops the Clipboard Monitor  
!clipboard monitor status = See the status of the Clipboard Monitor  

### Clipboard Monitor URL:
THe clipboard monitor URL mode acts the same way as the normal monitor mode as it reports to you everytime a new item is copied. However in url mode it also listens for copied URLs which in return get switched out with your URL. This can be a great tool for phishing.

!clipboard monitor url start https://your-url-here.com = Starts the Clipboard Monitor in URL mode  
!clipboard monior url stop = Stops the Clipboard Monitor URL mode 
!clipboard monitor url status = See the status of the Clipboard Monitor URL mode

### Message commands
Different ways to deliver a messag box to the user

!message title message = Shows a generic message box on the targets computer
!message prompt title message = Shows a message box with a text input for the target to enter text which will be sent to you
!message password title message = Same as message prompt but with a password input field

### Keyboard commands:

!keyboard write = Use the keyboard to write  
!keyboard press = Press a key with the keyboard  
!keyboard hotkey = Execute a hotkey with the keyboard  

!keyboard duckyscript = Upload a duckyscript file that will get executed on the targets computer. Note that this only supports very simple duckyscript syntax like: REM, STRING, STRINGLN, DELAY, and hotkeys

## Linux commands:

### Sudo commands:

The sudo commands are used to either obtain the sudo password, run commands with sudo, escelate privileges, etc.  
To obtain the sudo password used for all these the RAT intercepts the sudo command with a function in the users .bashrc file. When the users enters their sudo password its get saved to a file which gets picked up by the RAT.

!sudo password = Obtain the sudo password
!sudo shell = Run a shell command with sudo (requires that the sudo password already has been gathered)

