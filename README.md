# Ecommerce Price Tracker

## Overview

This project tracks product prices on **Amazon** and **Flipkart** platforms. It monitors specified product prices and notifies users via email when the price drops to or below the target price.

## Features

- **Track products** on Amazon and Flipkart by URL.
- Set **target price** for each product.
- Sends **email notification** when the product price meets or falls below the target.
- Can be customized for other e-commerce platforms.

## Technologies Used

- **Python**: Core functionality and web scraping.
- **HTML**: Used for frontend (if applicable).
- **SMTP**: For sending email notifications.
- **BeautifulSoup** and **Requests**: For web scraping Amazon and Flipkart.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/nikhilgodfather/EcommerceTracker.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Add product URLs to the script.
2. Set a target price for the product.
3. Run the tracker:
    ```bash
    python tracker.py
    ```

## How It Works

1. **Scraping**: Uses BeautifulSoup to scrape product prices from Amazon and Flipkart.
2. **Comparison**: Compares the current price with the user's target price.
3. **Notification**: Sends an email to notify the user if the price is lower than or equal to the target price.

## Contributing

Feel free to contribute by submitting a pull request or reporting issues.

