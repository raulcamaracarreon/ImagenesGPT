#define AppName "ImagenesGPT"
#define AppVersion "1.0.0"
#define AppExeName "ImagenesGPT.exe"

[Setup]
AppId={{A9D4B172-7B5F-4E70-A0DB-E3094E3E352A}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=ImagenesGPT
DefaultDirName={localappdata}\Programs\ImagenesGPT
DisableDirPage=no
UsePreviousAppDir=yes
DefaultGroupName=ImagenesGPT
PrivilegesRequired=lowest
OutputDir=..\dist\setup
OutputBaseFilename=ImagenesGPT-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
UninstallDisplayIcon={app}\{#AppExeName}
; El desinstalador conserva la carpeta de imágenes y la credencial de Windows.

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce

[Files]
Source: "..\dist\ImagenesGPT\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\ImagenesGPT"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\ImagenesGPT"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir ImagenesGPT"; Flags: nowait postinstall skipifsilent
