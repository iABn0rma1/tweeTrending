# Trending Tweet Topics

Scraping the current Hot topics of Twitter using [Selenium](https://www.selenium.dev/downloads/), [ProxyMesh](https://proxymesh.com), and [MongoDB](https://www.mongodb.com/pricing).

### Prerequisites

- [Python3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Clone the Repository

```bash
git clone https://github.com/iABn0rma1/tweeTrending.git
cd tweeTrending
```

### Install Dependencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies.

```bash
pip install -r requirements.txt
```

### Create a .env File
> [!NOTE]
> Create a `.env` file to store the sensitive information

Example:
```bash
MONGO_URI=mongodb://your_username:your_password@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=tweeTrending
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
```

### Run the Application

To start the FastAPI server, run the following command:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit `localhost:8000/` in your browser.

---
