# Project Setup and Running Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation and Setup](#installation-and-setup)
4. [Running the Application](#running-the-application)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)

## Introduction

Welcome to the project! This guide provides detailed instructions on setting up and running the application using Docker and Python. Please follow the steps outlined below to ensure a smooth setup process.

## Prerequisites

Before proceeding with the installation, make sure you have the following prerequisites installed on your machine:

- [Docker](https://www.docker.com/get-started)
- [Python](https://www.python.org/downloads/)

## Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd <project_directory>


```
- docker network create elastic
- docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.4
- docker run --name es07 --net elastic -p 9200:9200 -it -m 1GB --restart always docker.elastic.co/elasticsearch/elasticsearch:8.11.4

-> replace password, SH256 into line 6,7 at file api/app.py
- uvicorn main:app
```

## Usage

**Answering exercises and algorithmically searching for similar exercises.**




