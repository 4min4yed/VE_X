import vm_controller
import pika

#RabbitMQ sends data as raw bytes
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()

def callback(ch, method, properties, body):
    filepath=body.decode()
    vm_controller.run_vm_analysis(filepath)

channel.basic_consume(queue='vm_tasks', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
