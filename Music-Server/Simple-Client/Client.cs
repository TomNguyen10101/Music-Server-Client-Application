using System.Net.Sockets;
namespace Client
{
    class Program
    {
        const int port = 8000;
        const string IP = "localhost";

        static void Main(string[] args)
        {
            // data to send 
            string sendText = "I want this music";

            // Create TCPClient object with IP and port
            TcpClient client = new TcpClient(IP, port);

            // Translate the passed message into ASCII and store it as a Byte array
            Byte[] data = System.Text.Encoding.ASCII.GetBytes(sendText);

            // Get a client stream for reading and writing
            NetworkStream stream = client.GetStream();

            // Send the message to the connected TcpServer.
            stream.Write(data, 0, data.Length);

            Console.WriteLine("Sent: {0}", sendText);

            Console.ReadLine();

        }

    }
}
