﻿using Music_Streaming_Server;
using System;
using System.IO;
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Text;

namespace StreamingServer
{
    class Server
    {
        // Global Variables
        private static bool running = false;
        public static LinkedList<SocketState> connections = new LinkedList<SocketState>();  


        // State object used to pass between StartServer and AcceptNewClient
        // All We need is the TCPListener and the OnNetworkAction (could use a tuple)
        internal class NewConnectionState
        {
            public Action<SocketState> OnNetworkAction { get; }

            public TcpListener listener { get; }

            public NewConnectionState(Action<SocketState> call, TcpListener listener)
            {
                this.OnNetworkAction = call;
                this.listener = listener;
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="callThis"></param>
        /// <param name="port"></param>
        /// <returns></returns>
        public static TcpListener StartServer(Action<SocketState> callThis, int port)
        {
            IPEndPoint ep = new IPEndPoint(IPAddress.Any, port);
            TcpListener listener = new TcpListener(ep);

            try
            {
                listener.Start();
                NewConnectionState newState = new NewConnectionState(callThis, listener);
                listener.BeginAcceptSocket(AcceptNewClient, newState);
                
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }

            return listener;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="ar"></param>
        public static void AcceptNewClient(IAsyncResult ar)
        {
            NewConnectionState state = (NewConnectionState)ar.AsyncState;
            SocketState newClient = null;
            Socket newSocket = null;

            try
            {
                newSocket = state.listener.EndAcceptSocket(ar);
                newSocket.NoDelay = true;
            }
            catch (Exception ex)
            {
                newClient = new SocketState(state.OnNetworkAction, newSocket)
                {
                    ErrorOccured = true,
                    ErrorMessage = ex.ToString()
                };
                newClient.OnNetworkAction(newClient);
                return;
            }

            // Create a socket state to pass back to the server so it can keep track of all the clients
            newClient = new SocketState(state.OnNetworkAction, newSocket);
            newClient.OnNetworkAction(newClient);

            // Continue the listener event loop to get new clients
            try
            {
                state.listener.BeginAcceptSocket(AcceptNewClient, state);
            }
            catch (Exception ex)
            {
                newClient = new SocketState(state.OnNetworkAction, newSocket)
                {
                    ErrorOccured = true,
                    ErrorMessage = ex.ToString()
                };
                newClient.OnNetworkAction(newClient);
            }

        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="listener"></param>
        public static void StopServer(TcpListener listener)
        {
            try
            {
                listener.Stop();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
            }
        }

        /// <summary>
        /// Get data from the user
        /// </summary>
        /// <param name="state"></param>
        public static void GetData(SocketState state)
        {
            // Await more data
            try
            {
                state.theSocket.BeginReceive(state.buffer, 0, SocketState.BufferSize, 0, ReceiveCallBack, state);
                
            }
            catch (Exception ex)
            {
                state.ErrorOccured = true;
                state.ErrorMessage = ex.ToString();
                state.OnNetworkAction(state);
            }
        }
        private static void ReceiveCallBack(IAsyncResult ar)
        {
            SocketState state = (SocketState)ar.AsyncState;
            Socket socket = state.theSocket;
            try
            {
                int bytesRead = socket.EndReceive(ar);
                if (bytesRead > 0) 
                {
                    // There might be more data, so store the data received so far.
                    lock (state.data)
                    {
                        state.data.Append(Encoding.UTF8.GetString(state.buffer, 0, bytesRead));
                    }
                    Console.WriteLine(state.GetData());
                    // Give the client program's stored function a call so that it can process the data
                    state.OnNetworkAction(state);
                    return;
                }
                else
                {
                    state.ErrorOccured = true;
                    state.ErrorMessage = "Socket was closed";
                }

            }
            catch(Exception ex)
            {
                state.ErrorOccured = true;
                state.ErrorMessage = ex.ToString();
            }
            state.OnNetworkAction(state);
        }

        public static void Send(Socket socket, string data)
        {
            if (!socket.Connected) { return; }
            try
            {
                int offset = 0;
                byte[] byteData = Encoding.UTF8.GetBytes(data);
                socket.BeginSend(byteData, offset, byteData.Length, SocketFlags.None, SendCallBack, socket);
            }
            catch(Exception ex)
            {
                try
                {
                    socket.Shutdown(SocketShutdown.Both);
                    socket.Close();
                }
                catch (Exception e)
                {

                }
            }
        }

        private static void SendCallBack(IAsyncResult ar)
        {
            try
            {
                Socket socket = (Socket)ar.AsyncState;
                if (socket.Connected)
                {
                    socket.EndSend(ar);
                }
            }

            catch(Exception e)
            {

            }
        }


        /// <summary>
        /// When a client first connect, this function will be called to handle that new connection
        /// </summary>
        /// <param name="state"></param>
        private static void HandleNewClient(SocketState state)
        {
            // Return if there is an error during network operation or the server is not running
            if (state.ErrorOccured || !running) { return; }

            Console.WriteLine("New Connection: Client " + state.ID);
            Console.WriteLine("Accepted new connection from " + state.theSocket?.RemoteEndPoint?.ToString());

            lock (connections)
            {
                connections.AddLast(state);
            }
            GetData(state);
            SendFile(state);      
        }

        /// <summary>
        /// Send mp3 file to the user based on their search
        /// </summary>
        /// <param name="state"></param>
        private static void SendFile(SocketState state)
        {
            try
            {
                NetworkStream netstream = new NetworkStream(state.theSocket);
                StreamWriter writer = new StreamWriter(netstream);

                string filename = $"C:\\"; // Replace with an abosulte file path
                FileStream fileStream = File.Open(filename, FileMode.Open, FileAccess.Read, FileShare.Read);
                fileStream.CopyTo(netstream);
                netstream.Flush();
                // Send a message to the client, signal that it is done transfering the data
                Send(state.theSocket, "__END_OF_TRANSMISSION__");
                netstream.Close();
            }
          
            catch (Exception ex)
            {
                // Handle exceptions (log, throw, etc.)
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        // TODO: Implement the protocol for receiving different data from the users

        static void Main(string[] args)
        {
            StartServer(HandleNewClient, 8000);
            running = true;

            Console.ReadLine();
            
        }
    }
}
