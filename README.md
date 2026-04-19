![Web App CI](https://github.com/swe-students-spring2026/4-containers-fantastic_4/actions/workflows/web-app-ci.yml/badge.svg) ![Machine Learning Client CI](https://github.com/swe-students-spring2026/4-containers-fantastic_4/actions/workflows/machine-learning-client-ci.yml/badge.svg)

# Containerized App Exercise

## App Description

A web application that coverts audio recordings into written class notes, helping students capture and organize their lecture notes effortlessly.

## Team Members

[Eddy Yue](https://github.com/YechengYueEddy)

[Robin Chen](https://github.com/localhost433)

[Chenyu (Ginny) Jiang](https://github.com/ginny1536)

[Carolina Lee](https://github.com/CarolLee04)

[Uwa Igbinedion](https://github.com/uwa00)

## Running the Application

### Prerequisites

- Install and run [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### Step 1: Machine Learning Client Setup

1. In the `machine-learning-client/` folder, create a new file called `.env` by copying `.env.example`:
   ```bash
   cp machine-learning-client/.env.example machine-learning-client/.env
   ```
2. Get your **AssemblyAI** API key:
   - Go to [AssemblyAI](https://www.assemblyai.com/) and sign in
   - Click **API Keys** in the left sidebar and copy your key
   - Replace `your_assemblyai_api_key_here` in `.env` with your key
3. Get your **Google Gemini** API key:
   - Go to [Google AI Studio](https://aistudio.google.com/) and sign in
   - Click **Get API key**, then **Create API key**
   - Replace `your_google_api_key_here` in `.env` with your key

### Step 2: Web App Setup

1. In the `web-app/` folder, create a new file called `.env`
2. Copy the contents of `web-app/.env.example` into `.env`
3. Set `SECRET_KEY`
4. Update `MONGO_URI` and `ML_CLIENT_URL` if not on local defaults

### Step 3: Build and Start All Containers

```bash
docker-compose up --build
```

This starts all three containers:
- **Web App** at `http://localhost:5002`
- **ML Client** at `http://localhost:5001`
- **MongoDB** at `localhost:27017`

### Step 4: Use the App

Open `http://localhost:5002` in your browser, register an account, and start recording lectures.

### Stopping the App

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```
