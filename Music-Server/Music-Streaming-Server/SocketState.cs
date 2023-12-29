using System;
using System.Net.Sockets;
using System.Text;

namespace Music_Streaming_Server
{

    // A class for representing one network connection and all its realated state
    public class SocketState
    {
        public readonly Socket theSocket = null;            // The Socket
        public const int BufferSize = 8192;                 // Buffer size 
        internal byte[] buffer = new byte[BufferSize];      // Buffer
        internal StringBuilder data = new StringBuilder();  // Unprocessed data

        // Getting error message if one occured
        public string ErrorMessage { get; internal set; }

        // A flag for invoking the user's delegate OnNetworkAction if there is any
        // error occur during the network operation
        public bool ErrorOccured { get; internal set; }

        // Unique Identifer for each connection
        public readonly long ID;
        private static long nextID = 0;
        private static object mutexForID = new object();

        // Function to call when data is received or when a connection is made
        public Action<SocketState> OnNetworkAction;

        // Constructor
        public SocketState(Action<SocketState> toCall, Socket s)
        {
            this.OnNetworkAction = toCall;
            this.theSocket = s;
            lock(mutexForID)
            {
                ID = nextID++;
            }

        }

        // Return the unprocessed data the SocketState has received so far 
        // in thread-safe way
        public string GetData()
        {
            string remainData;
            lock (data)
            {
                remainData = data.ToString();
            }
            return remainData;
        }

        public void RemoveData(int start, int length)
        {
            lock (data)
            {
                data.Remove(start, length);
            }
        }


    }
}
