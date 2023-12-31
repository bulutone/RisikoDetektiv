<?php

// Telegram bot API key
$API_KEY = "xxx";

// Channel ID
$CHANNEL_ID = "xx";  // 

// XML source URL
$XML_URL = "x";

function scrapeXml() {
    global $XML_URL;

    try {
        // Step 1: Get the XML source
        $xmlContent = file_get_contents($XML_URL);
        if ($xmlContent === false) {
            throw new Exception("Failed to retrieve XML content");
        }
        echo "Step 1: Completed\n";

        // Step 2: Use SimpleXML to parse the XML content
        libxml_use_internal_errors(true);  // Ignore XML errors
        $xml = simplexml_load_string($xmlContent);
        if ($xml === false) {
            throw new Exception("Failed to parse XML content");
        }
        echo "Step 2: Completed\n";

        // Step 3: Find the items with "(DEU)" in their text
        $relevantItems = [];
        foreach ($xml->channel->item as $item) {
            if (strpos((string)$item->title, '(DEU)') !== false) {
                $relevantItems[] = [
                    'title' => (string)$item->title,
                    'description' => (string)$item->description,
                    'link' => (string)$item->link,
                    'date' => substr((string)$item->pubDate, 0, 10) . " " . substr((string)$item->pubDate, 11),
                ];
            }
        }
        echo "Step 3: Completed\n";

        return $relevantItems;

    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
        return null;
    }
}

function sendMessage($data) {
    global $API_KEY, $CHANNEL_ID;

    try {
        // Step 4: Send messages to the Telegram channel
        foreach ($data as $item) {
            $message = "{$item['title']}\n{$item['description']}\n{$item['link']}\n{$item['date']}\n";
            file_get_contents("https://api.telegram.org/bot$API_KEY/sendMessage?chat_id=$CHANNEL_ID&text=" . urlencode($message));
        }
        echo "Step 4: Completed\n";

    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }
}

try {
    // Step 3: Get the data
    $data = scrapeXml();
    if ($data !== null) {
        echo "Step 3: Completed\n";

        // Step 5: Send the data to the Telegram channel
        sendMessage($data);
        echo "Step 5: Completed\n";
    } else {
        echo "Step 3: Failed (No relevant data)\n";
    }

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
