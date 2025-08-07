; Maintenance Goblin NSIS installer
!define APP_NAME "Maintenance Goblin"
!define APP_VERSION "0.2.0"

OutFile "MaintenanceGoblinSetup.exe"
InstallDir "$PROGRAMFILES32\Maintenance Goblin"
RequestExecutionLevel admin

!include "MUI2.nsh"
!define MUI_ICON "goblin.ico"
!define MUI_HEADERIMAGE
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchApp

Var StartOnBoot

Page directory
Page instfiles
Page custom StartOnBootPage StartOnBootPageLeave
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\MaintenanceGoblin.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\Maintenance Goblin.lnk" "$INSTDIR\MaintenanceGoblin.exe"
  CreateDirectory "$SMPROGRAMS\Maintenance Goblin"
  CreateShortcut "$SMPROGRAMS\Maintenance Goblin\Maintenance Goblin.lnk" "$INSTDIR\MaintenanceGoblin.exe"
SectionEnd

Section -post
  ${If} $StartOnBoot == 1
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}" '"$INSTDIR\MaintenanceGoblin.exe" --silent'
  ${EndIf}
SectionEnd

Function StartOnBootPage
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}
  ${NSD_CreateCheckbox} 0 0 100% 12u "Launch at startup"
  Pop $StartOnBoot
  nsDialogs::Show
FunctionEnd

Function StartOnBootPageLeave
  ${NSD_GetState} $StartOnBoot $StartOnBoot
FunctionEnd

Function LaunchApp
  Exec "$INSTDIR\MaintenanceGoblin.exe"
FunctionEnd

SilentInstall silent
