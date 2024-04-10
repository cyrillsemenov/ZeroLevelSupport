# Zero level support

This project offers an alternative to traditional search engines like Elastic Search, leveraging the power of OpenAI embeddings to enhance the search functionality. It transforms queries into embeddings and searches a PostgreSQL database for the most similar results. This solution features synonym management and special flags to trigger custom behaviors when articles with these flags are identified as similar.

> [!WARNING]  
> This project is still in the early stages of development and is not meant to be used in production.

## Features

- **Embeddings-Based Search:** Utilizes OpenAI embeddings to understand and match queries with similar content in the database.
- **Synonym Support:** Incorporates a synonym feature to recognize and treat different terms or phrases as equivalent in search queries.
- **Custom Flags:** Allows articles to be tagged with special flags, enabling custom actions or filters when these articles are matched.
- **Telegram Bot:** Includes an example Telegram bot for interactive querying, built on a Django backend with a fully functional admin panel.
  Web Interface: Provides a simple web-based interface for knowledge base viewing and editing, making content management straightforward.
- **FastAPI Endpoints:** Offers FastAPI endpoints for webhooks, bot status, and similar searches, facilitating integration with other services.
- **Dockerized Deployment:** Designed to run in a Docker Compose environment with PostgreSQL, ensuring easy setup and scalability.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/cyrillsemenov/ZeroLevelSupport.git
cd ZeroLevelSupport
```

### 2. Configuration

Copy and fill `.env` file.

```bash
cp .env.sample .env
```

You will need:

- `SECRET_KEY` — Django secret key
- Database config — db name, user, password, host, and port for your database
- `HOST` — this is your webhook host
- `OPENAI_API_KEY` - API key for your OpenAI account
- `BOT_API_KEY` - Telegram bot API key, which you can get from [@Botfather](https://t.me/Botfather)
- `WEB_APP_URL` - URL for the [shutdown report form](https://github.com/dyadyaJora/tg-webapp-shutdown-report)

> [!TIP]
> If you're running this project locally, you'll likely want to set up something like [ngrok](https://ngrok.com/) to obtain your webhook host.

### 3. Build and Run with Docker Compose

```bash
docker-compose up --build
```

### 4. Accessing the Admin Panel

Navigate to <http://localhost:8000/admin> to access the Django admin panel. Use the credentials provided during the setup to log in.

### 5. Interacting with the Telegram Bot

After setting up the Telegram bot with [@Botfather](https://t.me/Botfather), you can start querying your knowledge base directly from Telegram.

### 6. Using the Web Interface

Visit <http://localhost:8000/questions> to view, search, and edit the knowledge base articles through the web interface.

### 7. API Usage

The FastAPI documentation available at <http://localhost:8000/docs> details the available endpoints for webhooks, bot status, and similar searches.

### 8. Contributing

Contributions to enhance this project are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.
