<?php
/**
 * Created by PhpStorm.
 * User: alexandre
 * Date: 24/04/19
 * Time: 10:24
 */

if (isset($_FILES['my_file'])) {
    if (($fh = fopen($_FILES['my_file']['tmp_name'], "r")) !== FALSE) {

        $arrayKeys = array();
        while (($line = fgetcsv($fh, 1000, ";")) !== FALSE) {
            if($num = count($line) == 2) {
                $key = $line[0];
                $label = $line[1];
                $arrayKeys[$key] = $label;
            };

        }
        fclose($fh);

        // 2) Export to xliff format
        header("Content-type: application/xml");
        header("Content-Disposition: attachment; filename=translations.xliff");
        header("Pragma: no-cache");
        header("Expires: 0");

        $id = $_POST['my_idstart'];
        foreach($arrayKeys as $key => $label) {

            $xliffTag = <<<EOT
<trans-unit id="{$id}">
    <source><![CDATA[{$key}]]></source>
    <target><![CDATA[{$label}]]></target>
</trans-unit>

EOT;
            echo $xliffTag;
            $id++;
        }

        exit();
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
            <input type="submit" value="Upload">
        </form>
    </body>
</html>
