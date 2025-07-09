# OTP Migration Decoder

This project provides a tool to decode Google OTP Migration QR codes. It extracts and decodes the OTP entries from QR images, allowing you to retrieve account details such as name, issuer, secret, type, algorithm, digits, and counter.

## Features

- Decode OTP migration URLs from QR images.
- Extract account details from the decoded data.
- Supports various OTP algorithms and types.

## Requirements

- Python >= 3.13
- OpenCV for Python
- Protobuf
- Pyzbar
- ZBar libraries (must be installed on the OS)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kagesenshi/google-totp-migration-decoder.git
   cd google-totp-migration-decoder
   ```

2. Install the ZBar libraries:

   On Debian-based systems (using `apt`):

   ```bash
   sudo apt update
   sudo apt install libzbar0
   ```

   On Fedora/Red Hat-based systems (using `dnf`):

   ```bash
   sudo dnf install zbar-libs
   ```

3. Install the dependencies using `uv` and `pyproject.toml`:

   ```bash
   uv sync
   ```

## Usage

To decode a QR image containing a Google OTP Migration URL, run the following command:

```bash
uv run main.py <path_to_qr_image>
```

Replace `<path_to_qr_image>` with the path to your QR image file. The script will output the decoded account details.

## Example

```bash
uv run main.py example_qr.png
```

This will output the account details extracted from the QR code in `example_qr.png`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
