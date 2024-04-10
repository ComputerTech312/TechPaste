# TechPaste

TechPaste is a simple pastebin software that uses client side encryption for web based usage, and server side encryption for API usage.

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/pasteapi.git
cd pasteapi
pip install -r requirements.txt
```

## API Usage

### Create a new paste

To create a new paste, send a POST request to `/api/v1/secure-paste` with a JSON body containing the `data` field. You can also include an optional `expiry` field to specify when the paste should expire.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"data":"Hello, World!", "expiry":"2022-12-31 23:59:59"}' curl -X POST -H "Content-Type: application/json" -d '{"data":"Hello, World!", "expiry":"2022-12-31 23:59:59"}' http://localhost:5000/api/v1/secure-paste
```

The response will be a JSON object with a `success` field and, if the request was successful, an `id` field containing the id of the created paste.

### Retrieve a paste

To retrieve a paste, send a GET request to `/api/v1/secure-paste/{paste_id}`, replacing `{paste_id}` with the id of the paste.

```bash
curl -X GET http://localhost:5000/api/v1/secure-paste/1234567890
```

The response will be the content of the paste if it exists and has not expired. If the paste does not exist or has expired, the response will be an error message.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

Please replace `localhost:5000` and `yourusername` with the actual server address and port where your application is running and your actual GitHub username respectively.
