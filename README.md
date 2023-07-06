# A text to speech client

A Python client that programmatically prepares payment claims against a testnet XRP wallet and uses these to fund requests to [speech to text](https://dhali-app.web.app/#/assets/d82952124-c156-4b16-963c-9bc8b2509b2c).

## Installation 

1. `sudo apt install portaudio19-dev python3-pyaudio`
2. `pip install -r requirements.txt`

## Running

`./run.sh`

## Troubleshooting

If the client fails to start. Check the contents of `stderr.log`, saved to your local directory.
