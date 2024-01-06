using System;
using System.Diagnostics.Tracing;
using System.Reflection.Metadata.Ecma335;
using Microsoft.Data.Sqlite;

namespace MusicDB
{
    public class DB
    {
        /// <summary>
        /// Get the song path based on the user search
        /// </summary>
        /// <param name="query"></param>
        public static string[] GetSongFromDb(string query)
        {
            //string currentDirectory = Directory.GetCurrentDirectory();
            //Console.WriteLine($"Current Directory: {currentDirectory}");
            using (var connection = new SqliteConnection("Data Source=musicDB.db"))
            {
                connection.Open();
                var command = connection.CreateCommand();
                command.CommandText = @"SELECT Name, Path FROM Songs WHERE Name LIKE @Val1";
                command.Parameters.AddWithValue("@Val1",$"{query}%");
                using (var reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        string name = reader.GetString(0); // First Column
                        string path = reader.GetString(1); // Second Column
                        Console.WriteLine($"Song Name: {name},Song Path: {path}");
                        string[] songInfo = { name, path };
                        return songInfo;
                    }
                }
            }

            return null;
        }

        /// <summary>
        /// This function is only used by the developer on the server side to add new song to the database.
        /// Param: "artist" is optional
        /// </summary>
        /// <param name="name"></param>
        /// <param name="artist"></param>
        /// <param name="path"></param>
        private static void AddSong(string name, string artist, string path)
        {
            // REPLACE Data Source with an absolute path to the database
            using (var connection = new SqliteConnection("Data Source=musicDB.db"))
            {
                connection.Open();
                var command = connection.CreateCommand();

                // PREPARED STATMENTS: Avoid Injection Attack
                string commandText = @"INSERT INTO Songs";

                if (artist != null)
                {
                    commandText += @"(Name, Artist, Path) VALUES (@Val1, @Val2, @Val3)";
                    command.CommandText = commandText;
                    command.Parameters.AddWithValue("@Val1", name);
                    command.Parameters.AddWithValue("@Val2", artist);
                    command.Parameters.AddWithValue("@Val3", path);
                }
                else
                {
                    commandText += @"(Name, Path) VALUES (@Val1, @Val2)";
                    command.CommandText = commandText;
                    command.Parameters.AddWithValue("@Val1", name);
                    command.Parameters.AddWithValue("@Val2", path);
                }

                try
                {
                    command.ExecuteNonQuery();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
            }
        }

        static void Main(string[] args)
        {
            GetSongFromDb("Rizz");
        }
    }
}

