[Setup]
AppName=Aegis Cloud Windows Agent
AppVersion=1.2.4
AppPublisher=Aegis Cloud
AppPublisherURL=https://aegiscloud.in
DefaultDirName={autopf}\Aegis Cloud Agent
DefaultGroupName=Aegis Cloud
OutputBaseFilename=AegisAgentSetup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableWelcomePage=no
DisableDirPage=yes
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\aegis-agent.exe

[Files]
Source: "target\release\aegis-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Set global environment variable for the Server URL (defaults to production, easily changed in System Properties)
Root: HKLM; Subkey: "System\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "AEGIS_SERVER_URL"; ValueData: "wss://api.aegiscloud.in"; Flags: uninsdeletevalue
; Add to Startup so it runs silently in the background on login
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AegisCloudAgent"; ValueData: """{app}\aegis-agent.exe"""; Flags: uninsdeletevalue

[Icons]
Name: "{group}\Aegis Cloud Agent"; Filename: "{app}\aegis-agent.exe"
Name: "{group}\Uninstall Aegis Cloud Agent"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\aegis-agent.exe"; Description: "Start Aegis Cloud Agent now"; Flags: nowait postinstall skipifsilent
