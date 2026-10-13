Attribute VB_Name = "GCC_Helpers"
'Batch helpers for folders of GCC truth-table workbooks.
'
'ConvertFolderToXlsx - saves every .xls in a folder as .xlsx, or .xlsm when the
'                      workbook carries macros. The original .xls files are kept.
'UploadFolder        - opens every truth-table workbook in a folder, runs the
'                      Control Logix upload against it and saves it.
'
'Import this module into the same workbook as the Upload macro. UploadFolder
'calls RunUpload, which is the body of Upload without its Yes/No prompt.
'
'Workbooks are opened with events off so they do not add or remove the
'GCC_Macros menu while the batch runs. Each run appends to gcc_batch_log.txt
'in the chosen folder.

Option Explicit

Private Const LOG_FILE As String = "gcc_batch_log.txt"

Private blnOldScreenUpdating As Boolean
Private blnOldEnableEvents As Boolean
Private blnOldDisplayAlerts As Boolean


Public Sub ConvertFolderToXlsx()

    Dim strFolder As String
    Dim colFiles As Collection
    Dim varFile As Variant
    Dim strResult As String
    Dim intDone As Integer
    Dim intSkipped As Integer
    Dim intFailed As Integer
    Dim strFailures As String

    strFolder = PickFolder("Select the folder of .xls files to convert")
    If strFolder = "" Then Exit Sub

    Set colFiles = ListFiles(strFolder, ".xls")
    If colFiles.Count = 0 Then
        MsgBox "No .xls files found in" & vbCr & strFolder, vbInformation, "Convert to xlsx"
        Exit Sub
    End If

    If MsgBox("Convert " & colFiles.Count & " .xls file(s) in" & vbCr & strFolder & vbCr & _
              "to .xlsx (.xlsm if the file has macros)?" & vbCr & "The original files are kept.", _
              vbYesNo + vbDefaultButton2 + vbQuestion, "Convert to xlsx") <> vbYes Then Exit Sub

    WriteLog strFolder, "Convert started: " & colFiles.Count & " file(s)"
    BeginBatch

    For Each varFile In colFiles
        Application.StatusBar = "Converting " & varFile & "..."
        strResult = ConvertOne(strFolder, CStr(varFile))

        If strResult = "" Then
            intDone = intDone + 1
        ElseIf Left$(strResult, 8) = "Skipped:" Then
            intSkipped = intSkipped + 1
        Else
            intFailed = intFailed + 1
            strFailures = strFailures & vbCr & varFile & ": " & strResult
        End If
        WriteLog strFolder, varFile & " - " & IIf(strResult = "", "converted", strResult)
    Next varFile

    EndBatch
    WriteLog strFolder, "Convert finished: " & intDone & " converted, " & intSkipped & " skipped, " & intFailed & " failed"

    ShowSummary "Convert to xlsx", strFolder, intDone & " converted, " & intSkipped & _
                " skipped (already converted), " & intFailed & " failed.", strFailures

End Sub


Public Sub UploadFolder()

    Dim strFolder As String
    Dim colFiles As Collection
    Dim varFile As Variant
    Dim strResult As String
    Dim intDone As Integer
    Dim intFailed As Integer
    Dim strFailures As String

    strFolder = PickFolder("Select the folder of truth-table workbooks to upload")
    If strFolder = "" Then Exit Sub

    Set colFiles = ListFiles(strFolder, ".xls", ".xlsx", ".xlsm")
    If colFiles.Count = 0 Then
        MsgBox "No truth-table workbooks found in" & vbCr & strFolder, vbInformation, "Upload Folder"
        Exit Sub
    End If

    If MsgBox("Upload from the Control Logix into " & colFiles.Count & " workbook(s) in" & vbCr & _
              strFolder & vbCr & "and save each one?", _
              vbYesNo + vbDefaultButton2 + vbQuestion, "Upload Folder") <> vbYes Then Exit Sub

    WriteLog strFolder, "Upload started: " & colFiles.Count & " file(s)"
    BeginBatch

    For Each varFile In colFiles
        Application.StatusBar = "Uploading " & varFile & " (" & (intDone + intFailed + 1) & _
                                " of " & colFiles.Count & ")..."
        strResult = UploadOne(strFolder & varFile)

        If strResult = "" Then
            intDone = intDone + 1
            WriteLog strFolder, varFile & " - uploaded"
        Else
            intFailed = intFailed + 1
            strFailures = strFailures & vbCr & varFile & ": " & strResult
            WriteLog strFolder, varFile & " - FAILED: " & strResult

            'if the very first file fails RSLinx is probably down, so don't grind through the rest
            If intDone = 0 And intFailed = 1 And colFiles.Count > 1 Then
                If MsgBox("The first upload failed:" & vbCr & strResult & vbCr & vbCr & _
                          "Check RSLinx is running. Keep going with the other files?", _
                          vbYesNo + vbDefaultButton2 + vbExclamation, "Upload Folder") <> vbYes Then Exit For
            End If
        End If
    Next varFile

    EndBatch
    WriteLog strFolder, "Upload finished: " & intDone & " uploaded, " & intFailed & " failed"

    ShowSummary "Upload Folder", strFolder, intDone & " uploaded, " & intFailed & " failed.", strFailures

End Sub


'Saves one .xls as .xlsx/.xlsm next to it. Returns "" on success, "Skipped: ..." or an error message.
Private Function ConvertOne(strFolder As String, strFile As String) As String

    Dim wb As Workbook
    Dim strTarget As String
    Dim lngFormat As Long

    On Error GoTo Failed

    Set wb = Workbooks.Open(Filename:=strFolder & strFile, UpdateLinks:=0, ReadOnly:=True)

    If wb.HasVBProject Then 'keep the macros, .xlsx would silently drop them
        lngFormat = xlOpenXMLWorkbookMacroEnabled
        strTarget = strFolder & BaseName(strFile) & ".xlsm"
    Else
        lngFormat = xlOpenXMLWorkbook
        strTarget = strFolder & BaseName(strFile) & ".xlsx"
    End If

    If Dir(strTarget) <> "" Then
        ConvertOne = "Skipped: " & Mid$(strTarget, Len(strFolder) + 1) & " already exists"
    Else
        wb.SaveAs Filename:=strTarget, FileFormat:=lngFormat
    End If

    wb.Close SaveChanges:=False
    Exit Function

Failed:
    ConvertOne = Err.Description
    If Not wb Is Nothing Then wb.Close SaveChanges:=False

End Function


'Opens one workbook, uploads into it from the PLC and saves it. Returns "" on success or an error message.
Private Function UploadOne(strPath As String) As String

    Dim wb As Workbook

    On Error GoTo Failed

    Set wb = Workbooks.Open(Filename:=strPath, UpdateLinks:=0)
    If wb.ReadOnly Then
        UploadOne = "file is read-only or open by someone else"
        wb.Close SaveChanges:=False
        Exit Function
    End If

    wb.Activate 'the upload macros read and write whichever workbook is active
    Call RunUpload

    wb.Save
    wb.Close SaveChanges:=False
    Exit Function

Failed:
    UploadOne = Err.Description
    If Not wb Is Nothing Then wb.Close SaveChanges:=False 'don't save a half-filled upload

End Function


Private Function PickFolder(strTitle As String) As String

    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = strTitle
        .AllowMultiSelect = False
        If .Show = -1 Then
            PickFolder = .SelectedItems(1)
            If Right$(PickFolder, 1) <> Application.PathSeparator Then
                PickFolder = PickFolder & Application.PathSeparator
            End If
        End If
    End With

End Function


'Returns the names of files in strFolder whose extension exactly matches one of varExtensions.
'Dir("*.xls") also matches .xlsx on Windows, so the extension is checked by hand.
Private Function ListFiles(strFolder As String, ParamArray varExtensions() As Variant) As Collection

    Dim colFiles As New Collection
    Dim strFile As String
    Dim strExt As String
    Dim varExt As Variant

    strFile = Dir(strFolder & "*.xls*")
    Do While strFile <> ""
        strExt = LCase$(Mid$(strFile, InStrRev(strFile, ".")))

        'skip Excel lock files and the workbook running this macro
        If Left$(strFile, 2) <> "~$" And strFile <> ThisWorkbook.Name Then
            For Each varExt In varExtensions
                If strExt = varExt Then
                    colFiles.Add strFile
                    Exit For
                End If
            Next varExt
        End If

        strFile = Dir()
    Loop

    Set ListFiles = colFiles

End Function


Private Function BaseName(strFile As String) As String
    BaseName = Left$(strFile, InStrRev(strFile, ".") - 1)
End Function


Private Sub BeginBatch()
    blnOldScreenUpdating = Application.ScreenUpdating
    blnOldEnableEvents = Application.EnableEvents
    blnOldDisplayAlerts = Application.DisplayAlerts

    Application.ScreenUpdating = False
    Application.EnableEvents = False 'stops Workbook_Open / BeforeClose firing on each file
    Application.DisplayAlerts = False 'stops compatibility and overwrite prompts
End Sub


Private Sub EndBatch()
    Application.ScreenUpdating = blnOldScreenUpdating
    Application.EnableEvents = blnOldEnableEvents
    Application.DisplayAlerts = blnOldDisplayAlerts
    Application.StatusBar = False
End Sub


Private Sub WriteLog(strFolder As String, strLine As String)

    Dim intFile As Integer

    On Error Resume Next 'a log we can't write should never stop the batch
    intFile = FreeFile
    Open strFolder & LOG_FILE For Append As #intFile
    Print #intFile, Format$(Now, "yyyy-mm-dd hh:nn:ss") & "  " & strLine
    Close #intFile

End Sub


Private Sub ShowSummary(strTitle As String, strFolder As String, strCounts As String, strFailures As String)

    Dim strMessage As String

    strMessage = strCounts
    If strFailures <> "" Then
        If Len(strFailures) > 700 Then strFailures = Left$(strFailures, 700) & vbCr & "..."
        strMessage = strMessage & vbCr & vbCr & "Failures:" & strFailures
    End If
    strMessage = strMessage & vbCr & vbCr & "Details in " & strFolder & LOG_FILE

    MsgBox strMessage, IIf(strFailures = "", vbInformation, vbExclamation), strTitle

End Sub
