import pusher

pusher_client = pusher.Pusher(
    app_id = "1954040",
    key = "5792836772309a1ad042",
    secret = "f19fde8655bbca88f675",
    cluster = "ap2",
    ssl=True
)
print("Pusher configured successfully!")
