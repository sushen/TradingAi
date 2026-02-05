[Setup]
AppName=TradingAi
AppVersion=1.0.0
DefaultDirName={pf}\TradingAi
DefaultGroupName=TradingAi
OutputDir=.
OutputBaseFilename=TradingAi_Setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\TradingAi.exe

[Files]
Source: "..\dist\TradingAi\TradingAi.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\TradingAi\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TradingAi"; Filename: "{app}\TradingAi.exe"
Name: "{commondesktop}\TradingAi"; Filename: "{app}\TradingAi.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\TradingAi.exe"; Description: "Launch TradingAi"; Flags: nowait postinstall skipifsilent
