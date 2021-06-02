<?php
/**
 * Created by PhpStorm.
 * User: alexandre
 * Date: 02/06/2021
 * Time: 10:22
 */

include_once "./vendor/autoload.php";

if (isset($_FILES['my_file'])) {
    if (($fh = fopen($_FILES['my_file']['tmp_name'], "r")) !== FALSE) {

        $arrayKeys = array();
        $countLines = 0;
        $languagesOrder = array();
        while (($line = fgetcsv($fh, 1000, ";")) !== FALSE) {
            if($countLines === 0) {
                // Récupération des en-têtes
                foreach($line as $c => $headLabel) {
                    if($c > 0) {
                        $languagesOrder[] = strtolower($headLabel);
                    }
                }
                $countLines++;
                continue;
            }
            if($num = count($line) > 1) {
                $key = $line[0];
                foreach($line as $c => $val) {
                    if($c > 0) {
                        $language = $languagesOrder[$c-1];
                        $label = $val;
                        $arrayKeys[$language][$key] = $label;
                    }
                }
            }
            $countLines++;
        }
        fclose($fh);

        $domain = $_POST['domain'];

        $zip = new ZipArchive();
        $filename = sys_get_temp_dir()."/tmpziptranslator.zip";

        if(file_exists($filename)) {
            unlink($filename);
        }

        if ($zip->open($filename, ZipArchive::CREATE)!==TRUE) {
            exit("Impossible d'ouvrir le fichier <$filename>\n");
        }

        foreach($arrayKeys as $locale => $catalog) {
            $id = $_POST['my_idstart'];
            $xmlTags = '';

            foreach ($catalog as $key => $label) {

                $xmlTags .= <<<EOL
            <trans-unit id="$id" resname="$key">
                <source><![CDATA[$key]]></source>
                <target><![CDATA[$label]]></target>
            </trans-unit>

EOL;
                $id++;
            }

            $xmlContent = <<<EOL
<?xml version="1.0"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
    <file source-language="fr" target-language="$locale" datatype="plaintext" original="file.ext">
        <body>
$xmlTags
        </body>
    </file>
</xliff>

EOL;
            $zip->addFromString(sprintf('%s.%s.xliff', $domain, $locale), $xmlContent);
        }

        $zip->close();

        header("Content-type: application/zip");
        header("Content-Disposition: attachment; filename=translator.zip");
        header("Pragma: no-cache");
        header("Expires: 0");
        readfile($filename);

    }
}
?>

<!doctype html>
<html lang="fr">
<head>
    <title>CSV To XLIFF</title>
</head>
<body>
<ul class="menu">
    <li><a href="index.php">Xliff to CSV</a></li>
</ul>

<br/><br/>
<hr>
<br/><br/>

<form method="post" enctype="multipart/form-data">
    <label>Fichier csv : </label>
    <input type="file" name="my_file" required>
    <br/><br/>
    <label>Id de début : </label><input type="text" name="my_idstart" required/>
    <label>Domaine : </label><input type="text" name="domain" required/>
    <input type="submit" value="Upload">
</form>
</body>
</html>
