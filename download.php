<?php
$db = new PDO('sqlite:users_database.db');
?>

<?php
// Get the file_id from the URL
$file_id = $_GET['file_id'];

// Establish a connection to the SQLite database
$db = new PDO('sqlite:users_database.db');

// Retrieve the file data from the database based on the file_id
$stmt = $db->prepare('SELECT filename, data FROM files WHERE file_id = :file_id');
$stmt->bindParam(':file_id', $file_id);
$stmt->execute();
$file = $stmt->fetch(PDO::FETCH_ASSOC);

// Check if the file data exists
if (!$file) {
    die('File not found.');
}

$filename = $file['filename'];
$file_data = $file['data'];

// Set the appropriate headers for file download
header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="' . $filename . '"');

// Send the file data as the response
echo $file_data;
exit;
?>