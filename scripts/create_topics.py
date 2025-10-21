import subprocess

from dotenv import load_dotenv

load_dotenv()

TOPICS = [
    "cart.updated",
    "cart.checkedout",
    "orders.created",
    "payments.succeeded",
    "payments.failed",
    "inventory.reserved",
    "inventory.failed",
    "shipping.started",
    "shipping.completed",
]


def ensure(topic: str) -> None:
    cmd = [
        "docker",
        "exec",
        "-i",
        "clothing-broker",
        "opt/kafka/bin/kafka-topics.sh",
        "--create",
        "--if-not-exists",
        "--topic",
        topic,
        "--bootstrap-server",
        "localhost:9092",
        "--partitions",
        "1",
        "--replication-factor",
        "1",
    ]
    subprocess.run(cmd, check=False)


for t in TOPICS:
    ensure(t)
print("Topics ensured.")
