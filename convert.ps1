function convertWord($filePath, $pdfPath) {
  # initialize
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false

  # convert
  $document = $word.Documents.Open($filePath)
  $document.ExportAsFixedFormat($pdfPath, 17)
  $document.Close()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($document)

  # release
  $word.Quit()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word)
  Remove-Variable word
}

function convertExcel($filePath, $pdfPath) {
  # initialize
  $excel = New-Object -ComObject Excel.Application
  $excel.Visible = $false

  # convert
  $workbook = $excel.Workbooks.Open($filePath)
  $workbook.ExportAsFixedFormat(0, $pdfPath)
  $workbook.Close()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook)
  
  # release
  $excel.Quit()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel)
  Remove-Variable excel
}

function convertPowerpoint($filePath, $pdfPath) {
  # initialize
  $powerpoint = New-Object -ComObject Powerpoint.Application

  # convert
  $presentation = $powerpoint.Presentations.Open($filePath, $null, $null, $false)
  $presentation.SaveAs($pdfPath, 32)
  $presentation.Close()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($presentation)
  
  # release
  $powerpoint.Quit()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($powerpoint)
  Remove-Variable powerpoint
}

# Main

$filePath = $args[0]
$pdfPath = $args[1]

$extension = (Split-Path -Path $filePath -Leaf).Split(".")[1]

if (Test-Path $pdfPath) {
  Remove-Item $pdfPath
}

if (($extension -eq 'doc') -Or ($extension -eq 'docx')) {
  convertWord $filePath $pdfPath
} elseif (($extension -eq 'xls') -Or ($extension -eq 'xlsx')) {
  convertExcel $filePath $pdfPath
} elseif ((($extension -eq 'ppt') -Or ($extension -eq 'pptx'))) {
  convertPowerpoint $filePath $pdfPath
}