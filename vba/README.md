# GCC workbook macros

`GCC_Helpers.bas` adds two batch helpers for folders of GCC truth-table workbooks:

- **`ConvertFolderToXlsx`** saves every `.xls` in a folder as `.xlsx`. A workbook that contains macros is saved as `.xlsm` instead, because `.xlsx` would drop them. The original `.xls` files are left in place, and a file that already has a converted copy is skipped.
- **`UploadFolder`** opens every `.xls`, `.xlsx` and `.xlsm` workbook in a folder, runs the Control Logix upload against it, and saves it. A file whose upload fails is closed without saving.

Both helpers write a timestamped log to `gcc_batch_log.txt` in the folder you pick.

## Installing

1. Open the workbook that holds the `Upload` macro and press Alt+F11.
2. Choose File > Import File and pick `GCC_Helpers.bas`.
3. In the module that contains `Upload`, split the confirmation prompt from the work so the batch can run without a Yes/No box for every file:

   ```vba
   Sub Upload()
   Answer = MsgBox(Prompt:="Upload Data from the Control Logix?", Title:="Upload?", Buttons:=vbYesNo + vbDefaultButton2 + vbQuestion)
   If Answer = vbYes Then Call RunUpload
   End Sub

   Sub RunUpload()
       ' everything that used to sit between "If Answer = vbYes Then" and the matching "End If" in Upload
   End Sub
   ```

   The menu still calls `Upload`, so it behaves exactly as before.

4. Optionally, add the helpers to the menu in `AddGCCMenu` (ThisWorkbook), after the last existing button:

   ```vba
       With .Controls.Add(Type:=msoControlButton)
           .Caption = "Convert &Folder to xlsx"
           .OnAction = "ConvertFolderToXlsx"
           .BeginGroup = True
       End With
       With .Controls.Add(Type:=msoControlButton)
           .Caption = "Upload &Whole Folder"
           .OnAction = "UploadFolder"
       End With
   ```

## Notes

- Upload works on whichever workbook is active, because the macros use unqualified `Range("...")` names. Each file therefore uploads from its own `RSTopic` and `CurrentUnit`.
- Converting `gccdbb.xls` breaks `SaveToDB` silently. Excel renames the names `FQI1`–`FQI3`, `SEQ1`–`SEQ10` and `TT1`–`TT8` to `FQI1_` and so on, because in `.xlsx` they are cell addresses (column FQI, row 1). `Range("FQI1")` then reads that empty cell instead of the setting, and `Workbooks("gccdbb.xls")` no longer finds the file. To fix it, replace every `Workbooks("gccdbb.xls").Worksheets(2).Range("X").Value` in `SaveToDB` with `DbSetting("X")`. `DbSetting` finds gccdbb under any extension and accepts either the old name or the underscored one, so it works before and after conversion. Keep the names Excel created; don't rename them back.
- `flask init-ttparser` currently loads only `*.xls` files. It needs updating before it can read converted workbooks.
