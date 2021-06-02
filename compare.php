<?php


?>

<!doctype html>
<html lang="fr">
    <head>
        <title>Comparaison traductions/title>
    </head>
    <body>
        <ul class="menu">
            <li><a href="xliff.php">CSV To xliff</a></li>
        </ul>

        <br/><br/>
        <hr>
        <br/><br/>

        <form method="post" enctype="multipart/form-data">
            <p>
            	<label>Fichiers Branche 1 : </label>
            	<input type="file" name="branch1[]" multiple>
    		</p>
    		<p>
    			<label>Fichiers Branche 2 : </label>
            	<input type="file" name="branch2[]" multiple>
    		</p>
            <input type="submit" value="Upload">
        </form>

    </body>
</html>