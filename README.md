<a id="readme-top"></a>

<!-- project shields -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- project header -->
<br />
<div align="center">
  <h3 align="center">AI Compare API</h3>

  <p align="center">
    A zero-latency raw JSON API hosted on GitHub Pages for AI model rankings, benchmarks, specifications, and model comparisons.
    <br />
    <a href="https://github.com/yamanist0/Ai-Compare-Api"><strong>Explore the documentation »</strong></a>
    <br />
    <br />
    <a href="https://yamanist0.github.io/Ai-Compare-Api/">Live API Endpoint</a>
    &middot;
    <a href="https://github.com/yamanist0/Ai-Compare-Api/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/yamanist0/Ai-Compare-Api/issues">Request Feature</a>
  </p>
</div>

<!-- table of contents -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#github-pages-deployment">GitHub Pages Deployment</a></li>
      </ul>
    </li>
    <li>
      <a href="#api-usage">API Usage</a>
      <ul>
        <li><a href="#1-compare-multiple-models">1. Compare Multiple Models</a></li>
        <li><a href="#2-get-complete-model-details">2. Get Complete Model Details</a></li>
        <li><a href="#3-query-a-specific-property">3. Query A Specific Property</a></li>
        <li><a href="#4-fuzzy-matching-and-typo-correction">4. Fuzzy Matching and Typo Correction</a></li>
        <li><a href="#5-direct-static-raw-json-endpoints">5. Direct Static Raw JSON Endpoints</a></li>
      </ul>
    </li>
    <li><a href="#nightly-synchronization">Nightly Synchronization</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- about the project -->
## About The Project

AI Compare API is a serverless, zero-latency raw JSON API that serves specifications, pricing, modalities, and benchmark rankings for hundreds of artificial intelligence models.

Hosted completely on GitHub Pages, this repository eliminates backend server overhead by distributing structured, static JSON datasets combined with an in-browser query handler that responds exclusively in raw JSON format.

Every night at midnight, automated GitHub Actions workflows fetch the newest benchmarks directly from ZeroEval, update the model data in memory, and commit the fresh snapshots to the repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

This project relies on lightweight, standardized technologies to guarantee maximum uptime, zero server hosting costs, and fast delivery over global content delivery networks:

* [![Python][Python-shield]][Python-url]
* [![GitHub Actions][GitHub-Actions-shield]][GitHub-Actions-url]
* [![GitHub Pages][GitHub-Pages-shield]][GitHub-Pages-url]
* [![JSON][JSON-shield]][JSON-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Key Features

* Multi-Model Comparison: Compare two or more AI models simultaneously with automatic descending sorting based on the conservative benchmark score.
* Full Specification Extraction: Returns all known metadata including model type, organization, release date, licensing, open weights status, supported input and output modalities, and token pricing.
* Isolated Property Queries: Query a single attribute (such as conservative score, rank, input price, or license) directly from any model.
* Fuzzy Search and Typo Tolerance: If an invalid model name is supplied, the API suggests the closest existing model. When the fuzzy flag is enabled, it automatically resolves to the best matching model.
* Case-Insensitive Inputs: Automatically normalizes uppercase names and identifiers to lowercase.
* Direct Static Endpoints: CORS-enabled static JSON files that can be fetched directly by frontends, backend services, or mobile applications.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- getting started -->
## Getting Started

Follow these instructions to set up, deploy, or run the sync pipeline locally.

### Prerequisites

* Python 3.10 or higher
* Git command line tools
* GitHub Personal Access Token with repository write permissions (stored in repository secrets as `gh_pat`)

### GitHub Pages Deployment

1. Clone the repository:
   ```sh
   git clone https://github.com/yamanist0/Ai-Compare-Api.git
   cd Ai-Compare-Api
   ```

2. Push the files to your main branch:
   ```sh
   git add .
   git commit -m "initialize raw json api"
   git push -u origin main
   ```

3. Enable GitHub Pages:
   * Go to your repository settings on GitHub.
   * Navigate to the Pages tab in the left sidebar.
   * Under Build and deployment, set Source to "Deploy from a branch".
   * Select the "main" branch and "/ (root)" directory, then click Save.

4. Your raw API will be available at:
   `https://yamanist0.github.io/Ai-Compare-Api/`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- api usage and endpoints -->
## API Usage

Base API URL: `https://yamanist0.github.io/Ai-Compare-Api/`

All endpoints return raw JSON output without any HTML formatting.

### 1. Compare Multiple Models

Provide two or more model identifiers separated by commas. The API returns all matched models sorted from highest conservative benchmark score to lowest, identifying the winner at the top.

Endpoint:
```
GET https://yamanist0.github.io/Ai-Compare-Api/?compare=claude-opus-5-5,gpt-6-astra,gemma-3-1b-it
```

Example cURL request:
```sh
curl -s "https://yamanist0.github.io/Ai-Compare-Api/?compare=claude-opus-5-5,gpt-6-astra,gemma-3-1b-it"
```

Example JSON response:
```json
{
  "status": "success",
  "total_compared": 3,
  "winner": {
    "model_id": "claude-opus-5-5",
    "name": "Claude Opus 5.5",
    "conservative": 59.7,
    "rank": 1
  },
  "models": [
    {
      "model_id": "claude-opus-5-5",
      "name": "Claude Opus 5.5",
      "organization": "Anthropic",
      "rank": 1,
      "conservative": 59.7,
      "mu": 63.64,
      "sigma": 1.31,
      "input_modalities": ["image", "text"],
      "output_modalities": ["text"],
      "input_price": 200000.0,
      "license": "proprietary",
      "is_open": false
    },
    {
      "model_id": "gpt-6-astra",
      "name": "GPT-6 Astra",
      "organization": "OpenAI",
      "rank": 2,
      "conservative": 59.49,
      "mu": 63.17,
      "sigma": 1.23,
      "input_modalities": ["image", "text"],
      "output_modalities": ["text"],
      "input_price": 1000000.0,
      "license": "proprietary",
      "is_open": false
    },
    {
      "model_id": "gemma-3-1b-it",
      "name": "Gemma 3 1B",
      "organization": "Google",
      "rank": 373,
      "conservative": -10.53,
      "mu": -6.71,
      "sigma": 1.27,
      "input_modalities": [],
      "output_modalities": [],
      "input_price": null,
      "license": "gemma",
      "is_open": true
    }
  ]
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 2. Get Complete Model Details

Retrieve every known attribute for a given model, including benchmark ranks, uncertainty parameters, modality support, and licensing terms.

Endpoint:
```
GET https://yamanist0.github.io/Ai-Compare-Api/?model=gpt-6-astra
```

Example cURL request:
```sh
curl -s "https://yamanist0.github.io/Ai-Compare-Api/?model=gpt-6-astra"
```

Example JSON response:
```json
{
  "status": "success",
  "data": {
    "model_id": "gpt-6-astra",
    "name": "GPT-6 Astra",
    "model_type": "llm",
    "organization": "OpenAI",
    "organization_id": "openai",
    "announcement_date": "2026-09-03",
    "release_date": "2026-09-04",
    "multimodal": true,
    "license": "proprietary",
    "is_open": false,
    "input_modalities": ["image", "text"],
    "output_modalities": ["text"],
    "input_price": 1000000.0,
    "output_price": null,
    "rank": 2,
    "conservative": 59.49,
    "mu": 63.17,
    "sigma": 1.23,
    "ci_lower": 60.72,
    "ci_upper": 65.63,
    "games_played": 22,
    "rank_delta_14d": -1
  }
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 3. Query A Specific Property

Request a targeted field from an AI model without receiving the full payload.

Endpoint:
```
GET https://yamanist0.github.io/Ai-Compare-Api/?model=claude-opus-5-5&property=conservative
```

Example cURL request:
```sh
curl -s "https://yamanist0.github.io/Ai-Compare-Api/?model=claude-opus-5-5&property=conservative"
```

Example JSON response:
```json
{
  "status": "success",
  "model_id": "claude-opus-5-5",
  "model_name": "Claude Opus 5.5",
  "property": "conservative",
  "value": 59.7
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 4. Fuzzy Matching and Typo Correction

When a requested model identifier does not match any record exactly, the API suggests the closest match based on string distance:

```sh
curl -s "https://yamanist0.github.io/Ai-Compare-Api/?model=claud-opus"
```

Response:
```json
{
  "status": "error",
  "message": "model 'claud-opus' not found",
  "searched": "claud-opus",
  "suggestion": "claude-opus-5",
  "all_suggestions": [
    "claude-opus-5",
    "claude-opus-5-5",
    "claude-opus-4-8"
  ],
  "hint": "add &fuzzy=true to automatically match the closest model"
}
```

By appending `&fuzzy=true`, the API automatically selects the best matching candidate:

```sh
curl -s "https://yamanist0.github.io/Ai-Compare-Api/?model=claud-opus&fuzzy=true"
```

Response:
```json
{
  "status": "success",
  "auto_matched": true,
  "searched": "claud-opus",
  "matched_model_id": "claude-opus-5",
  "data": {
    "model_id": "claude-opus-5",
    "name": "Claude Opus 5",
    "rank": 3,
    "conservative": 54.75
  }
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 5. Direct Static Raw JSON Endpoints

If you prefer static files without query parameter processing, you can consume the raw JSON datasets directly. These files include complete cross-origin resource sharing headers:

* All Models (Full Specifications and Benchmark Scores):
  ```
  GET https://yamanist0.github.io/Ai-Compare-Api/api/all.json
  ```
* Leaderboard (All Ranked Models Ordered by Conservative Score):
  ```
  GET https://yamanist0.github.io/Ai-Compare-Api/api/leaderboard.json
  ```
* Individual Model Snapshots:
  ```
  GET https://yamanist0.github.io/Ai-Compare-Api/api/models/{model_id}.json
  ```
  Examples:
  ```sh
  curl -s "https://yamanist0.github.io/Ai-Compare-Api/api/models/gpt-6-astra.json"
  curl -s "https://yamanist0.github.io/Ai-Compare-Api/api/models/claude-opus-5-5.json"
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- automated sync -->
## Nightly Synchronization

Data updates are fully automated using GitHub Actions defined in `.github/workflows/sync.yml`.

* Schedule: Runs every night at midnight (00:00 Turkey Time / 21:00 UTC).
* In-Memory Operations: The synchronization script pulls updates from ZeroEval, combines benchmarks with technical specifications, generates the target JSON structures, and updates the repository.
* Repository Secret: Requires a Personal Access Token stored as `gh_pat` under repository secrets to permit automated commits.

To manually trigger a synchronization run:
1. Navigate to the Actions tab in your repository.
2. Select "Sync AI Compare Data".
3. Click "Run workflow".

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- roadmap -->
## Roadmap

- [x] Merge ZeroEval models and leaderboard into consolidated datasets
- [x] Multi-model comparison engine with conservative score ordering
- [x] Isolated property query endpoint
- [x] Fuzzy name resolution and auto-match parameter
- [x] Pure raw JSON output mode on GitHub Pages
- [x] Nightly GitHub Actions synchronization pipeline
- [ ] Historical benchmark score tracking and change deltas
- [ ] Category-specific leaderboards for coding, reasoning, and vision

See the [open issues](https://github.com/yamanist0/Ai-Compare-Api/issues) for proposed features and known items.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- contributing -->
## Contributing

Contributions make the open-source community a great place to build useful tools. Any contributions you make are greatly appreciated.

If you have an idea or improvement:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'add new feature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- license -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- contact -->
## Contact

Project Link: [https://github.com/yamanist0/Ai-Compare-Api](https://github.com/yamanist0/Ai-Compare-Api)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- acknowledgments -->
## Acknowledgments

* [ZeroEval Leaderboard](https://zeroeval.com)
* [GitHub Pages](https://pages.github.com)
* [GitHub Actions](https://github.com/features/actions)
* [Img Shields](https://shields.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- markdown links and badges -->
[contributors-shield]: https://img.shields.io/github/contributors/yamanist0/Ai-Compare-Api.svg?style=for-the-badge
[contributors-url]: https://github.com/yamanist0/Ai-Compare-Api/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/yamanist0/Ai-Compare-Api.svg?style=for-the-badge
[forks-url]: https://github.com/yamanist0/Ai-Compare-Api/network/members
[stars-shield]: https://img.shields.io/github/stars/yamanist0/Ai-Compare-Api.svg?style=for-the-badge
[stars-url]: https://github.com/yamanist0/Ai-Compare-Api/stargazers
[issues-shield]: https://img.shields.io/github/issues/yamanist0/Ai-Compare-Api.svg?style=for-the-badge
[issues-url]: https://github.com/yamanist0/Ai-Compare-Api/issues
[license-shield]: https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge
[license-url]: https://github.com/yamanist0/Ai-Compare-Api/blob/main/LICENSE
[Python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[GitHub-Actions-shield]: https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white
[GitHub-Actions-url]: https://github.com/features/actions
[GitHub-Pages-shield]: https://img.shields.io/badge/GitHub_Pages-222222?style=for-the-badge&logo=github&logoColor=white
[GitHub-Pages-url]: https://pages.github.com/
[JSON-shield]: https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white
[JSON-url]: https://www.json.org/