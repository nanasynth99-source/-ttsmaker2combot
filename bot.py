import asyncio

def main():
    # ... your application setup ...
    application.run_polling()

if __name__ == '__main__':
    # This forces Python 3.14 to create the missing event loop explicitly
    try:
        asyncio.run(main())
    except RuntimeError:
        # Fallback if an event loop is already running or partially configured
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        main()
