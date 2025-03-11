#  Deploying AI Agents: Azure case labcamp
This repo contains code and specifications about the LabCamp "Deploying AI Agents: Azure case" 

## Table of Contents

- [Deploying AI Agents: Azure case labcamp](#deploying-ai-agents-azure-case-labcamp)
  - [Table of Contents](#table-of-contents)
  - [Fine Tuning](#fine-tuning)
  - [Create and use an AI Agent](#create-and-use-an-ai-agent)
- [Authors](#authors)


## Fine Tuning

In the `fine tuning dataset` folder, you can find pre-created dataset files that you can use for fine-tuning related to an exercise: `Festival di Sanremo 2024`.

Using these files, you can directly proceed with the fine-tuning process via the `Azure AI Agent Service`.

## Create and use an AI Agent

In this exercise, we will show you how to create an enterprise AI agent using Azure AI Services. The agent will be equipped with various capabilities including:

- Integration with Bing search for real-time information retrieval
- File search functionality for accessing company documents
- Custom function tools for fetching weather and datetime
- A modern Gradio-based chat interface
- Real-time streaming responses with visual feedback
- Comprehensive event handling and logging

### Exercise Overview

Your goal will be to create a new agent and enhance it with additional tools. The exercise consists of the following steps:

1. Create an AI Agent either through the Azure UI or programmatically via the notebook
2. Test the agent's functionality using the pre-installed tools
3. Add a new vector store containing financial data
4. Implement a new custom tool: `fetch_stock_price` to query stock market data using yahoo finance
5. Evaluate the agent's performance with the new capabilities

This hands-on exercise will help you understand how to create, customize, and extend AI agents with new data sources and tools.

During the labcamp, we will provide you with an `.env` file, containing secret api keys. This file should be uploaded in the Files section in a Colab notebook (or stored in the root directory of the local project). refer to `.env.template` for an example of how to store the keys.

# Authors

- Francesco Miliani | Blockchain Reply IT
- Davide Magliano | Laife Reply IT
