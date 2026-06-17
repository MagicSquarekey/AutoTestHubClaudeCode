' AutoTest Hub 鏃犵獥鍙ｅ惎鍔ㄨ剼鏈?/ AutoTest Hub windowless startup script
' 鍙屽嚮杩愯锛屼笉浼氬脊鍑轰换浣曠粓绔獥鍙?/ Double-click to run, no terminal windows will appear

' 鍒涘缓鏂囦欢绯荤粺鍜孲hell瀵硅薄 / Create filesystem and shell objects
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' 鑾峰彇椤圭洰鏍圭洰褰?/ Get project root directory
rootDir = fso.GetParentFolderName(WScript.ScriptFullName)
backendDir = rootDir & "\backend"
frontendDir = rootDir & "\frontend"
pythonExe = rootDir & "\.venv\Scripts\python.exe"

' 妫€鏌ヨ櫄鎷熺幆澧冩槸鍚﹀瓨鍦?/ Check if virtual environment exists
If Not fso.FileExists(pythonExe) Then
    MsgBox "Virtual env not found. Run: python -m venv .venv", 16, "AutoTest Hub"
    WScript.Quit 1
End If

' 娓呯悊鏃ц繘绋?/ Clean up old processes
shell.Run "cmd /c " & rootDir & "\stop.bat", 0, True

' 鍚庡彴鍚姩鍚庣鏈嶅姟 / Start backend service in background
shell.Run "cmd /c cd /d " & backendDir & " && " & pythonExe & " main.py", 0, False

' 鍚庡彴鍚姩鍓嶇鏈嶅姟 / Start frontend service in background
shell.Run "cmd /c cd /d " & frontendDir & " && npm run dev", 0, False

' 绛夊緟鍓嶇鏈嶅姟灏辩华 / Wait for frontend service to be ready
Dim maxWait, i, ready, http
maxWait = 30
ready = False

For i = 1 To maxWait
    WScript.Sleep 1000
    On Error Resume Next
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", "http://localhost:5173", False
    http.Send
    ' 妫€鏌ュ墠绔槸鍚﹀搷搴?/ Check if frontend is responding
    If Err.Number = 0 And http.Status = 200 Then
        ready = True
        On Error GoTo 0
        Exit For
    End If
    Err.Clear
    On Error GoTo 0
    Set http = Nothing
Next

' 鏍规嵁缁撴灉鎵撳紑娴忚鍣ㄦ垨鎻愮ず閿欒 / Open browser or show error based on result
If ready Then
    ' 鎵撳紑娴忚鍣?/ Open browser
    shell.Run "http://localhost:5173"
Else
    MsgBox "Service start timeout. Check logs.", 16, "AutoTest Hub"
End If