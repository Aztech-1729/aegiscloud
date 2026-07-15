[Setup]
AppName=Aegis Cloud Agent
AppVersion=1.2.5
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
WizardStyle=modern

[Files]
Source: "target\release\aegis-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Set global environment variable for the Server URL
Root: HKLM; Subkey: "System\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "AEGIS_SERVER_URL"; ValueData: "wss://api.aegiscloud.in"; Flags: uninsdeletevalue

[Icons]
Name: "{group}\Aegis Cloud Agent"; Filename: "{app}\aegis-agent.exe"
Name: "{group}\Uninstall Aegis Cloud Agent"; Filename: "{uninstallexe}"

[Run]
; Install and start the Windows Service
Filename: "net"; Parameters: "start AegisCloudAgent"; Flags: runhidden postinstall skipifsilent; StatusMsg: "Starting Aegis Cloud Agent service..."

[UninstallRun]
; Stop and remove the service on uninstall
Filename: "net"; Parameters: "stop AegisCloudAgent"; Flags: runhidden
Filename: "sc"; Parameters: "delete AegisCloudAgent"; Flags: runhidden

[Code]
// Register as Windows Service on install
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create the Windows Service
    Exec(ExpandConstant('{app}\aegis-agent.exe'), '--install', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    // Start the service
    Exec('net', 'start AegisCloudAgent', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

// Remove service on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    Exec('net', 'stop AegisCloudAgent', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('sc', 'delete AegisCloudAgent', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
