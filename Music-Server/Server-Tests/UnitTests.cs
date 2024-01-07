using System.IO;
using System.Net.Sockets;
using System.Text;
using MusicServer;

namespace Server_Tests
{
    [TestClass]
    public class ServerTest
    {
        // Setting Up
        const int port = 8000;
        const string IP = "localhost";
        
        [TestMethod]
        public void GetResult()
        {
            string sendText = "Search:Rizz";
            string response = GetReponseFromServer(sendText);
            string[] splitResponse = response.Split("__NEXT_HEADER__");
            Assert.IsTrue(splitResponse[0].StartsWith("__NAME__"));
            Assert.IsTrue(splitResponse[1].StartsWith("__FILE__"));
        }

        [TestMethod]
        public void GetNoResult()
        {
            string sendText = "Search:raofnsofnos";
            string response = GetReponseFromServer(sendText);
            Assert.IsTrue(!string.IsNullOrEmpty(response));
            Assert.IsTrue(response.StartsWith("No Result"));
        }

        private string GetReponseFromServer(string sendText)
        {
            string result = "";
            try
            {
                // Create TCPClient object with IP and port
                TcpClient client = new TcpClient(IP, port);

                // Translate the passed message into ASCII and store it as a Byte array
                Byte[] data = System.Text.Encoding.ASCII.GetBytes(sendText);

                using (NetworkStream stream = client.GetStream())
                {
                    // Send the message to the connected TcpServer.
                    stream.Write(data, 0, data.Length);


                    // Read the response from the server until the delimiter is found
                    using (MemoryStream memoryStream = new MemoryStream())
                    {
                        byte[] buffer = new byte[1024];
                        int bytesRead;

                        // Define the delimiter
                        byte[] delimiter = Encoding.ASCII.GetBytes("__END_OF_TRANSMISSION__");

                        while (true)
                        {
                            bytesRead = stream.Read(buffer, 0, buffer.Length);
                            memoryStream.Write(buffer, 0, bytesRead);

                            // Check if the delimiter is present in the received data
                            if (ByteArrayEndsWith(memoryStream.ToArray(), delimiter))
                                break;
                        }

                        // Convert the received bytes to a string (excluding the delimiter)
                        string response = Encoding.ASCII.GetString(memoryStream.ToArray(), 0, (int)memoryStream.Length - delimiter.Length);
                        result = response;
                    }
                }   
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
            return result;
        }

        // Helper function
        private bool ByteArrayEndsWith(byte[] buffer, byte[] delimiter)
        {
            if (buffer.Length < delimiter.Length) return false;
            for (int i = 0; i < delimiter.Length; i++)
            {
                if (buffer[buffer.Length - delimiter.Length + i] != delimiter[i])
                {
                    return false;
                }
            }
            return true;
        }
    }

    
}