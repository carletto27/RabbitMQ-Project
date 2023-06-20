using RabbitMQ.Client;
using RabbitMQ.Client.Events;

var factory = new ConnectionFactory { HostName = "localhost" };

using var connection = factory.CreateConnection();
using var channel = connection.CreateModel();

channel.ExchangeDeclare(exchange: "topic", type: ExchangeType.Topic);

var queueName = channel.QueueDeclare().QueueName;

if (args.Length < 1)
{
    Console.Error.WriteLine("Usage: {0} [binding_key...]",
                            Environment.GetCommandLineArgs()[0]);
    Console.WriteLine(" Press [enter] to exit.");
    Console.ReadLine();
    Environment.ExitCode = 1;
    return;
}

foreach (var bindingKey in args)
{
    channel.QueueBind(queue: queueName,
                      exchange: "topic",
                      routingKey: bindingKey);
}

Console.WriteLine(" [*] Waiting for images. To exit press CTRL+C");

var consumer = new EventingBasicConsumer(channel);
consumer.Received += (model, ea) =>
{

    DateTime now = DateTime.Now;
    string date = now.ToString("dd_MM_yyyy--HH_mm_ss");
    string filePath = "C:/Users/lillo/Desktop/Tesi/Immagini ricevute/receivedImage--" + date + ".jpg";
    var body = ea.Body.ToArray();
    var fs = new FileStream(filePath, FileMode.Create, FileAccess.Write);
    fs.Write(body, 0, body.Length);

    var routingKey = ea.RoutingKey;
    fs.Close();
    Console.WriteLine($" [Image] Received '{routingKey}'");
};
channel.BasicConsume(queue: queueName,
                     autoAck: true,
                     consumer: consumer);

Console.WriteLine(" Press [enter] to exit.");
Console.ReadLine();