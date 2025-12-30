import json
import pika
from .faroukconfig import RABBITMQ_HOST, QUEUE_NAME
from .faroukvm_controller import run_vm_analysis

def on_message(channel, method, properties, body):
    print("📩 Job received")

    payload = json.loads(body.decode())
    job_id = payload["job_id"]
    file_path = payload["file_path"]

    try:
        run_vm_analysis(job_id, file_path)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print("✅ Job completed")
    except Exception as e:
        print("❌ Error:", e)
        channel.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=on_message
    )

    print("🚀 Worker started, waiting for jobs...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
