; Script de Inno Setup para empaquetar el ejecutable creado por PyInstaller.
#define MyAppName "XIL-AC Puerta Local"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "XIL-AC"
#define MyAppExeName "XILAC-PuertaLocal.exe"

[Setup]
AppId={{A7C15A8A-23D2-4D73-A12C-8D96C45D6F42}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\XIL-AC Puerta Local
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=XILAC-PuertaLocal-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\XILAC-PuertaLocal.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\XIL-AC Puerta Local"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\XIL-AC Puerta Local"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir XIL-AC Puerta Local"; Flags: postinstall nowait skipifsilent
