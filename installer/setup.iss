[Setup]
AppName=TradingBotX
AppVersion=1.0.0
DefaultDirName={pf}\TradingBotX
DefaultGroupName=TradingBotX
OutputDir=.
OutputBaseFilename=TradingBotX_Setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\main.exe

[Files]
Source: "..\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TradingBotX"; Filename: "{app}\main.exe"
Name: "{commondesktop}\TradingBotX"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\main.exe"; Description: "Launch TradingBotX"; Flags: nowait postinstall skipifsilent
