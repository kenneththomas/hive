using System;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        Console.WriteLine("smells like updog in here");

        string fixMessage = "8=FIX.4.2;49=DeutscheBank-800;11=2345;54=1;55=AAPL;38=100;44=150.00;40=2;59=0;10=004";
        Dictionary<string, string> fixDictionary = ParseFixMessage(fixMessage);

        // Generate a fill message
        string fillMessage = GenerateFillMessage(fixDictionary);

        Console.WriteLine("Fill Message: " + fillMessage);
    }

    public static Dictionary<string, string> ParseFixMessage(string fixMessage)
    {
        // Split on ';' to get key-value pairs
        string[] keyValuePairs = fixMessage.Split(';');

        // Create a dictionary of key-value pairs
        Dictionary<string, string> fixDictionary = new Dictionary<string, string>();

        foreach (string pair in keyValuePairs)
        {
            // Split on '=' to get key and value
            string[] keyValue = pair.Split('=');

            // Add to dictionary
            fixDictionary.Add(keyValue[0], keyValue[1]);
        }

        return fixDictionary;
    }
    public static string GenerateFillMessage(Dictionary<string, string> fixMessage)
    {
        // Initialize the fill message with unique identifiers for tags 17 and 37
        string fillMessage = $"17={Guid.NewGuid().ToString()};37={Guid.NewGuid().ToString()};150=2;";

        // Check if the original message has the order quantity (tag 38)
        string orderQty = fixMessage.ContainsKey("38") ? fixMessage["38"] : "0";

        // Add tag 14 (Cumulative Quantity) to match the order quantity, indicating full fill
        fillMessage += $"14={orderQty};";

        // Add the current timestamp to tag 52
        string timestamp = DateTime.UtcNow.ToString("yyyyMMdd-HH:mm:ss.fff");
        fillMessage += $"52={timestamp};";

        // Add "HPTY" as the value for the LastMkt and ExecBroker
        fillMessage += "30=HPTY;76=HPTY;";

        // Create a set of tags that are already included in the fill message
        HashSet<string> includedTags = new HashSet<string> { "17", "37", "150", "14", "52", "30", "76" };

        foreach (KeyValuePair<string, string> item in fixMessage)
        {
            // Skip adding tags that are already included in the fill message
            if (!includedTags.Contains(item.Key))
            {
                fillMessage += $"{item.Key}={item.Value};";
            }
        }

        // 8 in the front 10 at the end, eventually enforce the header/footer in this section
        fillMessage = MoveTag8ToFront(fillMessage);
        fillMessage = MoveTag10ToEnd(fillMessage);

        return fillMessage;
    }
    public static string MoveTag8ToFront(string message)
    {
        // Split the message into key-value pairs
        string[] keyValuePairs = message.Split(';');

        // Find the pair with tag 8 and remove it from the array
        string tag8Pair = "";
        List<string> otherPairs = new List<string>();
        foreach (string pair in keyValuePairs)
        {
            if (pair.StartsWith("8="))
            {
                tag8Pair = pair;
            }
            else
            {
                otherPairs.Add(pair);
            }
        }

        // Reconstruct the message with tag 8 at the front
        string newMessage = tag8Pair + ";" + string.Join(";", otherPairs);

        return newMessage;
    }

    public static string MoveTag10ToEnd(string message)
    {
        // Split the message into key-value pairs
        string[] keyValuePairs = message.Split(';');

        // Find the pair with tag 10 and remove it from the array
        string tag10Pair = "";
        List<string> otherPairs = new List<string>();
        foreach (string pair in keyValuePairs)
        {
            if (pair.StartsWith("10="))
            {
                tag10Pair = pair;
            }
            else
            {
                otherPairs.Add(pair);
            }
        }

        // Reconstruct the message with tag 10 at the end
        string newMessage = string.Join(";", otherPairs) + ";" + tag10Pair;

        return newMessage;
    }

}

