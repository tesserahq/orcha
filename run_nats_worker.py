from app.messaging import NatsEventSubscriber
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    subscriber = NatsEventSubscriber()

    # Register handlers here
    async def handle_event(msg):
        print(msg)

    subscriber.subscribe("linden.*", handle_event)
    # or subscriber.subscribe_bulk({...})

    subscriber.run()


if __name__ == "__main__":
    main()
