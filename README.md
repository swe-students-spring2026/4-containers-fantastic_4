![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

## App Description

A web application that coverts audio recordings into written class notes, helping students capture and organize their lecture notes effortlessly.

## Team Members

[Eddy Yue](https://github.com/YechengYueEddy)

[Robin Chen](https://github.com/localhost433)

[Chenyu (Ginny) Jiang](https://github.com/ginny1536)

## Machine Learning Client Setup

1. Go to [assemblyai.com](https://www.assemblyai.com/) and log in with your Google account
2. Once on the dashboard, click **API Keys** in the left sidebar
3. Copy your API key
4. In the `machine-learning-client/` folder, create a new file called `.env`
5. Copy the contents of `.env.example` into `.env`
6. Replace `your_assemblyai_api_key_here` with your actual API key