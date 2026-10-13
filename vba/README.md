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
- `SaveToDB` refers to `Workbooks("gccdbb.xls")` by name. If you convert `gccdbb.xls`, change that reference to the new file name.
- `flask init-ttparser` currently loads only `*.xls` files. It needs updating before it can read converted workbooks.
