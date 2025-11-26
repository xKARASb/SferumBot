# Max2TG Bot Deployment Guide

This guide provides instructions for deploying and running the Max2TG bot using Docker, including steps for initial PyMax authentication and persistent session management.

## Prerequisites

*   Docker is installed and running.
*   The `max2tg-bot` Docker image has been built. If not, navigate to the `SferumBot` directory and run:
    ```bash
    docker build -t max2tg-bot .
    ```
*   Your `SferumBot/.env` file is configured with the necessary environment variables (Telegram `BOT_TOKEN`, `TG_CHAT_ID`, `TG_TOPIC_ID`, Sferum `SFERUM_AUTH_COOKIE`, `SFERUM_CHAT_ID`, `SFERUM_TOPIC_ID`, Max `MAX_PHONE`, `MAX_CHAT_ID`, `MAX_TOPIC_ID`).

## Initial PyMax Interactive Authentication (One-Time Setup)

The PyMax client requires an initial interactive login to generate a session file for persistent, non-interactive use. This `session.db` file will be stored in a Docker named volume.

1.  **Stop and remove any existing `max2tg-container`:**
    ```bash
    docker stop max2tg-container 2>/dev/null || true
    docker rm max2tg-container 2>/dev/null || true
    ```
    *(The `2>/dev/null || true` part suppresses errors if the container doesn't exist)*

2.  **Create a Docker named volume for the Max session:**
    This volume will store your PyMax session file persistently.
    ```bash
    docker volume create max2tg_cache
    ```

3.  **Run the Docker container in interactive mode for authentication:**
    This command will launch a bash shell inside the container, mounting the named volume for session persistence.
    ```bash
    docker run -it --rm --name max2tg-auth-container -v max2tg_cache:/app/cache --env-file SferumBot/.env max2tg-bot /bin/bash
    ```
    *   `-it`: Runs in interactive mode with a pseudo-TTY.
    *   `--rm`: Automatically removes the container when it exits.
    *   `--name max2tg-auth-container`: Assigns a name to this temporary authentication container.
    *   `-v max2tg_cache:/app/cache`: Mounts the `max2tg_cache` named volume to `/app/cache` inside the container. This is where PyMax will save its `session.db` file.
    *   `--env-file SferumBot/.env`: Loads environment variables, including `MAX_PHONE`.
    *   `max2tg-bot`: The name of your Docker image.
    *   `/bin/bash`: Overrides the default command to start a bash shell inside the container.

4.  **Start the unified bot script within the container and authenticate:**
    Once you are inside the container's bash shell (you will see something like `root@<container_id>:/app#`), run the bot:
    ```bash
    python unified_bot.py
    ```
    *   **Follow the PyMax authentication prompts:** PyMax will prompt you to "Введите код:". **Carefully enter the exact authentication code** you receive in your Max messenger app.
    *   After successful authentication, PyMax will log "Login successful, token saved to database". The bot will then continue running.

5.  **Exit the interactive container:**
    Once PyMax authentication is complete and the bot is running (or has exited after a successful save), you can exit the container's shell by typing `exit` and pressing Enter. The `max2tg_cache` volume will retain your session.

## Running the Bot in Detached Mode (Background)

Once PyMax has been authenticated and its session saved to the `max2tg_cache` volume, you can run the bot non-interactively in the background.

1.  **Stop and remove any existing `max2tg-container`:**
    ```bash
    docker stop max2tg-container 2>/dev/null || true
    docker rm max2tg-container 2>/dev/null || true
    ```

2.  **Run the bot in detached mode, mounting the session volume:**
    ```bash
    docker run -d --name max2tg-container -v max2tg_cache:/app/cache --env-file SferumBot/.env max2tg-bot
    ```
    *   `-d`: Runs the container in detached (background) mode.
    *   `-v max2tg_cache:/app/cache`: Mounts the named volume containing your PyMax session.
    *   `--env-file SferumBot/.env`: Loads environment variables.

3.  **Monitor Bot Logs:**
    To check the bot's status and message forwarding activity, use:
    ```bash
    docker logs -f max2tg-container
    ```
    *(Press `Ctrl+C` to stop following the logs)*

## Verifying Message Forwarding

1.  Ensure the bot is running in detached mode.
2.  **Send a test message from your Sferum account** to the chat ID specified by your `SFERUM_CHAT_ID` environment variable.
3.  **Send a test message from your Max account** to the chat ID(s) specified by your `MAX_CHAT_ID` environment variable.
4.  Check the bot's logs (using `docker logs -f max2tg-container`) for lines indicating message reception and successful forwarding to Telegram:
    *   `Received message from Max:`
    *   `[MAIN] raw_msg:` (for Sferum)
    *   `📤 Пересылка сообщения: ... → Telegram`
    *   `✅ Сообщение успешно доставлено: ...`

## Troubleshooting `TOPIC_CLOSED` Error

If you still encounter a `Telegram server says - Bad Request: TOPIC_CLOSED` error for any message, it means your Telegram chat requires a topic ID, and one is not being provided or is invalid for that specific message.
*   **Edit `SferumBot/.env`:** Set `TG_TOPIC_ID` to a valid integer topic ID in your Telegram chat for general bot status messages. If your chat doesn't use topics, ensure `TG_TOPIC_ID` is empty.