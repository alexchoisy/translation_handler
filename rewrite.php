<?php
/**
 * Created by PhpStorm.
 * User: alexandre
 * Date: 23/04/19
 * Time: 11:27
 */

include_once "./vendor/autoload.php";

use Symfony\Component\Translation\Translator;
use Symfony\Component\Translation\Loader\XliffFileLoader;

if (isset($_FILES['my_file'])) {

    $translator = new Translator('fr');
    $translator->addLoader('xlf', new XliffFileLoader());
    $loader = new XliffFileLoader();

    $globalCatalog = array();
    $globalLocales = array();
    $xmls = array();


    $files = $_FILES['my_file'];

    $mappedFiles = array();
    if(array_key_exists('name', $files) && count($files['name']) > 0) {
        for($i=0;$i<count($files['name']); $i++) {
            $mappedFiles[] = array(
                'name' => $files['name'][$i],
                'type' => $files['type'][$i],
                'tmp_name' => $files['tmp_name'][$i],
                'error' => $files['error'][$i],
                'size' => $files['size'][$i]
            );
        }
    }

    $zip = new ZipArchive();
    $filename = sys_get_temp_dir()."/tmpziptranslator.zip";

    if(file_exists($filename)) {
        unlink($filename);
    }

    if ($zip->open($filename, ZipArchive::CREATE)!==TRUE) {
        exit("Impossible d'ouvrir le fichier <$filename>\n");
    }

    foreach($mappedFiles as $file) {
        preg_match("/(.*)\.([a-zA-Z]{2})\.xliff/", $file['name'], $domain);

        if(count($domain) != 3) {
            continue;
        }
        $domainName = $domain[1];
        $locale = $domain[2];
        if(!in_array($locale, $globalLocales)) {
            $globalLocales[] = $locale;
        }

        $catalog = $loader->load($file['tmp_name'], $domain[2], $domain[1]);

        if(!array_key_exists($domainName, $globalCatalog)) {
            $globalCatalog[$domainName] = array();
        }

        $catalogArray = $catalog->all($domainName);

        foreach($catalogArray as $key => $label) {
            if(!array_key_exists($key, $globalCatalog[$domainName])) {
                $globalCatalog[$domainName][$key] = array(
                    $locale => $label
                );
            } else {
                $globalCatalog[$domainName][$key][$locale] = $label;
            }
        }

        $xmlTags = '';
        foreach($catalogArray as $key => $label) {
            if($locale == 'fr') {
                $xmlTags .= <<<EOL
      <trans-unit id="$key" resname="$key">
        <source><![CDATA[$label]]></source>
        <target><![CDATA[$label]]></target>
      </trans-unit>

EOL;
            } else {
                $xmlTags .= <<<EOL
      <trans-unit id="$key" resname="$key">
        <source><![CDATA[$key]]></source>
        <target><![CDATA[$label]]></target>
      </trans-unit>

EOL;

            }
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

        $zip->addFromString($file['name'], $xmlContent);
    }

    var_dump($globalCatalog);die();

    foreach($globalCatalog as $domain => $item) {
        foreach($item as $label => $locales) {
            $line = array(
                $domain,
                $label
            );
            $error = false;
            foreach($globalLocales as $currentLocale) {
                if(array_key_exists($currentLocale, $locales)) {
                    $line[] = $locales[$currentLocale];
                } else {
                    $line[] = '';
                    $error = true;
                }
            }
            if($error) {
                $line[] = 'E';
            }
            fputcsv($fp, $line, ";");
        }

        $zip->addFromString(file['name'], $xmlContent);
    }


    $zip->close();

    header("Content-type: application/zip"); 
    header("Content-Disposition: attachment; filename=translator.zip"); 
    header("Pragma: no-cache"); 
    header("Expires: 0"); 
    readfile($filename);
}
?>

<!doctype html>
<html lang="fr">
    <head>
        <title>Traductions manquantes</title>
    </head>
    <body>
        <ul class="menu">
            <li><a href="xliff.php">CSV To xliff</a></li>
        </ul>

        <br/><br/>
        <hr>
        <br/><br/>

        <form method="post" enctype="multipart/form-data">
            <label>Fichiers xliff : </label>
            <input type="file" name="my_file[]" multiple>
            <input type="submit" value="Upload">
        </form>

    </body>
</html>