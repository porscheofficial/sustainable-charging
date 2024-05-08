# Chargify: Sustainable EV Charging

![License: MIT](https://img.shields.io/github/license/konstantinjdobler/nlp-research-template?color=green)

This repository holds the code for Chargify, focused on machine learning based EV charge scheduling. This project started in the AI in Practice course together with Porsche Digital.

## Structure

| Module Name            | Folder        | Description                                        |
| ---------------------- | ------------- |----------------------------------------------------|
| Model related          | model         | Code related to training the different models.     |
| Model results          | model_results | The weights and checkpoints of the trained models. |
| Frontend               | frontend      | Code for the frontend.                             |
| API                    | api           | The backend API code.                              |
| Experimental Notebooks | experiments   | Experiments we did during development.             |
| Experimental Data      | data          | Experimental data we used during development.      |

## Setup

### Database
We use a local MongoDB as database.

```bash
docker run --name chargify -d -p 27017:27017 mongo
```

Optional: Import a sample dataset to mongodb:
```bash
docker exec -i chargify /usr/bin/mongorestore --uri "mongodb://localhost:27017" --archive < api/mongodb.dump
```
With this import the database is set up to hold a test user called **chargify**, which can be used in the frontend.

### Backend API

It is recommended to run the backend in a virtual environment.

In the project root, run

```bash
python -m venv .venv && source .venv/bin/activate
```

Then install the requirements

```bash
pip install -r api/requirements.txt
```

To start the backend API, move into the api directory (`cd api`) and run

```bash
python -m uvicorn app.main:app --host=0.0.0.0
```

### Frontend

Move into the frontend folder

```bash
cd frontend
```

Install the required packages

```bash
npm install
```

Start the local frontend

```bash
npm start
```

### Model
This repository provides an already trained model to predict the future energy mix in the grid seven days in advance.
The default model used can be found in ```model_results/lstm```, which was trained in January 2024.
If you want to retrain the model, go through the following steps.

Follow these instructions to set up your Python environment to contribute to or run the code in this repository.
It's recommended to use [`mamba`](https://github.com/mamba-org/mamba) to manage dependencies. `mamba` is a drop-in replacement for `conda` re-written in C++ to speed things up significantly (you can stick with `conda` though).

<details><summary>Installing <code>mamba</code></summary>

<p>

On Unix-like platforms, run the snippet below. Otherwise, visit the [mambaforge repo](https://github.com/conda-forge/miniforge#mambaforge). Note this does not use the Anaconda installer, which reduces bloat.

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

</details>

#### Environment

After having installed `mamba`, you can create a `mamba` environment from the `environment.yml` with all necessary dependencies installed. Alternatively, you can use conda (the commands stay the same only replace mamba with conda). 

```bash
mamba env create -f environment.yml
```

You can then activate your environment with

```bash
mamba activate aip-porsche
```

#### Updating the Environment

Working together with many people in a shared environment requires caution.
If you want to add a dependency to the `environment.yml`, install the dependency locally and test that there are no conflicts with the existing environment.
Then open a pull request with an updated `environment.yml` to ensure that all collaborators can reproduce the environment.


## Contributing

Chargify is openly developed in the wild and contributions (both internal and external) are highly appreciated.
See [CONTRIBUTING.md](./CONTRIBUTING.md) on how to get started.

If you have feedback or want to propose a new feature, please [open an issue](https://github.com/porscheofficial/speed-estimation-traffic-monitoring/issues).
Thank you! 😊

## Acknowledgements

This project is a joint initiative of [Porsche AG](https://www.porsche.com), [Porsche Digital](https://www.porsche.digital/) and the [Hasso Plattner Institute](https://hpi.de) (Seminar: [AI in Practice](https://hpi.de/entrepreneurship/ai-in-practice.html)). ✨


## License

Copyright © 2023 Dr. Ing. h.c. F. Porsche AG

Dr. Ing. h.c. F. Porsche AG publishes this open source software and accompanied documentation (if any) subject to the terms of the [MIT license](./LICENSE.md). All rights not explicitly granted to you under the MIT license remain the sole and exclusive property of Dr. Ing. h.c. F. Porsche AG.

Apart from the software and documentation described above, the texts, images, graphics, animations, video and audio files as well as all other contents on this website are subject to the legal provisions of copyright law and, where applicable, other intellectual property rights. The aforementioned proprietary content of this website may not be duplicated, distributed, reproduced, made publicly accessible or otherwise used without the prior consent of the right holder.
