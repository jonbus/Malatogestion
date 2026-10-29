param([string]$Ruta)

Add-Type -AssemblyName System.Runtime.WindowsRuntime

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    try { $netTask.Wait(-1) | Out-Null } catch {
        Write-Output "FALLO_AWAIT: $($_.Exception.InnerException.Message)"
        return $null
    }
    $netTask.Result
}

$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.DataWriter, Windows.Storage.Streams, ContentType = WindowsRuntime]

# Leer los bytes directamente: evita Windows.Storage.StorageFile y sus permisos
$bytes = [System.IO.File]::ReadAllBytes($Ruta)
Write-Output "BYTES: $($bytes.Length)"

$stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
$writer = New-Object Windows.Storage.Streams.DataWriter($stream)
$writer.WriteBytes($bytes)
$storeOp = $writer.StoreAsync()
$null = Await $storeOp ([uint32])
$writer.DetachStream() | Out-Null
$stream.Seek(0)

$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
if (-not $decoder) { Write-Output "DECODER_NULO"; exit 1 }
Write-Output "IMAGEN: $($decoder.PixelWidth) x $($decoder.PixelHeight)"

$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
if (-not $bitmap) { Write-Output "BITMAP_NULO"; exit 1 }

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) { Write-Output "SIN_MOTOR_OCR"; exit 1 }
Write-Output "IDIOMA: $($engine.RecognizerLanguage.LanguageTag)"
Write-Output "---TEXTO---"

$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
if (-not $result) { Write-Output "RESULTADO_NULO"; exit 1 }

foreach ($linea in $result.Lines) {
    $xs = @($linea.Words | ForEach-Object { $_.BoundingRect.X })
    $ys = @($linea.Words | ForEach-Object { $_.BoundingRect.Y })
    $hs = @($linea.Words | ForEach-Object { $_.BoundingRect.Height })
    $minx = [int](($xs | Measure-Object -Minimum).Minimum)
    $miny = [int](($ys | Measure-Object -Minimum).Minimum)
    $h = [int](($hs | Measure-Object -Maximum).Maximum)
    Write-Output ("{0}|{1}|{2}|{3}" -f $miny, $minx, $h, $linea.Text)
}
